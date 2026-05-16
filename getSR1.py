import requests
import json
import urllib3
from datetime import datetime, timezone, timedelta
from collections import Counter

# Tắt cảnh báo về chứng chỉ SSL (do hệ thống nội bộ thường dùng https không chứng chỉ)
urllib3.disable_warnings()

# URL API của dịch vụ SR
API_URL = "https://gnoc.viettel.vn:9003/sr-service/SR/getListSR"

# ===================== CẤU HÌNH (CONFIG) =====================
TZ_OFFSET_HOURS = 7   # Múi giờ Việt Nam
COUNTRY = 281         # Mã quốc gia Việt Nam
SR_UNIT = "450518"    # Mã đơn vị quản lý SR
PAGE_SIZE = 1000      # Số lượng bản ghi trên một trang

# Bộ lọc nâng cao (để None nếu muốn lấy mặc định)
FILTER_EVALUATE = None  
FILTER_STATUS = None    

# Giới hạn số trang tối đa để tránh vòng lặp vô tận
MAX_PAGES = 200
# =============================================================

def load_token():
    """Đọc Token JWT từ file để xác thực với API."""
    with open("gnoc_token.txt", "r", encoding="utf-8") as f:
        return f.read().strip()

def fmt_utc_z(dt_utc: datetime) -> str:
    """Định dạng thời gian theo chuẩn ISO (YYYY-MM-DDTHH:MM:SS.000Z)."""
    return dt_utc.strftime("%Y-%m-%dT%H:%M:%S.000Z")

def start_of_month(dt_local: datetime) -> datetime:
    """Trả về thời điểm bắt đầu của tháng (ngày 01 lúc 00:00:00)."""
    return dt_local.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

def add_months(dt_local: datetime, months: int) -> datetime:
    """Hàm hỗ trợ cộng/trừ tháng vào một thời điểm cụ thể."""
    y = dt_local.year
    m = dt_local.month + months
    while m > 12:
        y += 1
        m -= 12
    while m < 1:
        y -= 1
        m += 12
    return dt_local.replace(year=y, month=m, day=1, hour=0, minute=0, second=0, microsecond=0)

def prev_month_to_now_range_iso_z(tz_offset_hours=7):
    """Tính toán khoảng thời gian từ đầu tháng trước đến thời điểm hiện tại."""
    tz_local = timezone(timedelta(hours=tz_offset_hours))
    now_local = datetime.now(tz_local)
    start_current = start_of_month(now_local)
    start_prev = add_months(start_current, -1)
    
    # Chuyển đổi sang múi giờ UTC để gửi lên Server
    start_prev_utc = start_prev.astimezone(timezone.utc)
    end_utc = now_local.astimezone(timezone.utc)
    return fmt_utc_z(start_prev_utc), fmt_utc_z(end_utc), start_prev, now_local

def month_chunks_local(start_local: datetime, end_local: datetime):
    """Chia nhỏ khoảng thời gian lớn thành từng tháng để API xử lý dễ hơn."""
    cur = start_of_month(start_local)
    if cur < start_local: cur = start_local
    while cur < end_local:
        nxt = add_months(start_of_month(cur), 1)
        chunk_start = cur
        chunk_end = min(nxt, end_local)
        yield chunk_start, chunk_end
        cur = nxt

def build_payload(create_from_z: str, create_to_z: str, page: int):
    """Tạo gói dữ liệu (JSON Payload) để gửi lên API."""
    payload = {
        "page": page,
        "pageSize": PAGE_SIZE,
        "country": COUNTRY,
        "srUnit": SR_UNIT,
        "createFromDate": create_from_z,
        "createToDate": create_to_z,
        "evaluate": "In deadline",
        "status": "Assigned_Planning,Evaluated,Execution_Halted,New,Planned"
    }
    # Áp dụng bộ lọc nếu có
    if FILTER_EVALUATE: payload["evaluate"] = FILTER_EVALUATE
    if FILTER_STATUS: payload["status"] = FILTER_STATUS
    return payload

def extract_list(resp_json):
    """Trích xuất danh sách SR từ JSON trả về của Server (xử lý nhiều định dạng)."""
    d = resp_json.get("data")
    if isinstance(d, list): return d
    if isinstance(d, dict):
        for k in ("records", "list", "rows", "items", "content"):
            v = d.get(k)
            if isinstance(v, list): return v
    return []

def call_api(headers, payload):
    """Gửi yêu cầu thực tế tới API bằng thư viện requests."""
    r = requests.post(API_URL, headers=headers, json=payload, verify=False, timeout=60)
    if r.status_code != 200:
        raise RuntimeError(f"Lỗi HTTP {r.status_code}: {r.text[:500]}")
    try:
        return r.json()
    except Exception:
        raise RuntimeError(f"Kết quả không phải JSON: {r.text[:500]}")

def fetch_by_pagination(headers, create_from_z: str, create_to_z: str):
    """Lấy dữ liệu theo cơ chế phân trang và kiểm tra xem Server có hỗ trợ phân trang không."""
    all_items = []
    seen = set()
    page1_codes = None
    pagination_ignored = False

    for page in range(1, MAX_PAGES + 1):
        payload = build_payload(create_from_z, create_to_z, page)
        j = call_api(headers, payload)
        items = extract_list(j)
        print(f"[Phân trang] Trang {page}: {len(items)} bản ghi")

        if not items: break

        # Kiểm tra xem Server có bị lỗi 'luôn trả về trang 1' không (Overlap detection)
        codes = [it.get("srCode") for it in items if isinstance(it, dict)]
        codes_set = set([c for c in codes if c])
        if page == 1:
            page1_codes = codes_set.copy()
        else:
            if page1_codes and len(codes_set) > 0:
                overlap = len(codes_set.intersection(page1_codes))
                if overlap / max(1, len(codes_set)) >= 0.85:
                    pagination_ignored = True
                    print("⚠️ Cảnh báo: API có vẻ bỏ qua phân trang (trang sau trùng trang đầu).")
                    break

        for it in items:
            if not isinstance(it, dict): continue
            code = it.get("srCode")
            if code and code in seen: continue
            if code: seen.add(code)
            all_items.append(it)
        if len(items) < PAGE_SIZE: break
    return all_items, pagination_ignored

def fetch_by_month_chunks(headers, start_local: datetime, end_local: datetime):
    """Phương án dự phòng: Chia nhỏ truy vấn theo từng tháng để lấy hết dữ liệu."""
    all_items = []
    seen = set()
    for i, (c_start_local, c_end_local) in enumerate(month_chunks_local(start_local, end_local), start=1):
        c_start_utc = c_start_local.astimezone(timezone.utc)
        c_end_utc = c_end_local.astimezone(timezone.utc)
        create_from_z = fmt_utc_z(c_start_utc)
        create_to_z = fmt_utc_z(c_end_utc)
        print(f"\n[Mảnh dữ liệu] {i}) {c_start_local.strftime('%Y-%m-%d')} -> {c_end_local.strftime('%Y-%m-%d')}")
        chunk_items, _ = fetch_by_pagination(headers, create_from_z, create_to_z)
        for it in chunk_items:
            code = it.get("srCode")
            if code and code not in seen:
                seen.add(code)
                all_items.append(it)
    return all_items

def summarize_months(items):
    """In bảng thống kê số lượng SR theo từng tháng."""
    months = Counter()
    for it in items:
        ct = it.get("createdTime")
        if ct: months[ct[:7]] += 1
    print("\n==== THỐNG KÊ ====")
    print("Tổng số SR:", len(items))
    print("Phân bổ tháng:", dict(sorted(months.items())))

def clean_items(sr_list):
    """Lọc bỏ các trường thừa và định dạng lại ngày tháng cho file kết quả."""
    clean = []
    for sr in sr_list:
        create_time = sr.get("createdTime")
        if create_time:
            try:
                dt = datetime.strptime(create_time[:19], "%Y-%m-%dT%H:%M:%S")
                create_time = dt.strftime("%d/%m/%Y %H:%M")
            except: pass
        clean.append({
            "srCode": sr.get("srCode"),
            "title": sr.get("title"),
            "status": sr.get("statusName"),
            "service": sr.get("serviceName"),
            "createdTime": create_time,
            "sla": sr.get("slaReceiveTime"),
            "unit": sr.get("pathSrUnit"),
            "creator": sr.get("createdUser"),
            "evaluate": sr.get("evaluate"),
            "executionTime": sr.get("executionTime"),
            "srUser": sr.get("srUser"),
            "remainExecutionTime": sr.get("remainExecutionTime"),
        })
    return clean

def main():
    """Quy trình chính của script."""
    token = load_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json;charset=UTF-8",
        "Accept": "application/json"
    }

    # 1. Xác định khoảng thời gian lấy dữ liệu
    create_from_z, create_to_z, start_local, now_local = prev_month_to_now_range_iso_z(TZ_OFFSET_HOURS)
    print(f"Khoảng thời gian: {start_local.strftime('%Y-%m-%d')} -> {now_local.strftime('%Y-%m-%d')}")

    # 2. Thử lấy dữ liệu bằng cơ chế phân trang mặc định
    print("\n=== Đang tải dữ liệu SR ===")
    sr_list, ignored = fetch_by_pagination(headers, create_from_z, create_to_z)

    # 3. Nếu phân trang bị lỗi (trả trùng trang 1), chuyển sang lấy theo từng tháng
    if ignored:
        print("\n=== Chuyển sang phương án dự phòng: Chia nhỏ theo tháng ===")
        sr_list = fetch_by_month_chunks(headers, start_local, now_local)

    # 4. Lưu dữ liệu thô (Raw)
    with open("sr_raw_all.json", "w", encoding="utf-8") as f:
        json.dump(sr_list, f, ensure_ascii=False, indent=2)

    # 5. In thống kê và lưu dữ liệu tinh gọn (Clean)
    summarize_months(sr_list)
    clean = clean_items(sr_list)
    with open("sr_clean_all.json", "w", encoding="utf-8") as f:
        json.dump(clean, f, ensure_ascii=False, indent=2)
    print("🏁 Hoàn tất! Kết quả đã lưu vào file sr_clean_all.json")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("❌ LỖI:", e)