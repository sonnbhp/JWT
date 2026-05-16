import os
import json
import time
import ssl
import logging
import urllib.request
import urllib.error
import requests
import urllib3
import tls_client
from datetime import datetime, timezone, timedelta
from playwright.sync_api import sync_playwright

# Tắt cảnh báo SSL cho các yêu cầu API
urllib3.disable_warnings()
SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

# --- ĐỊNH NGHĨA ĐƯỜNG DẪN ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
TOKEN_FILE = os.path.join(BASE_DIR, "gnoc_token.txt")
LOG_FILE = os.path.join(BASE_DIR, "gnoc_auto.log")
PROFILE_DIR = os.path.expanduser("~/.gnoc_browser_profile")

# --- CẤU HÌNH LOGGING ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("GnocAuto")

class GnocAutomationPipeline:
    def __init__(self):
        self.config = self._load_config()
        self.jwt_token = None
        self.gnoc_url = "https://gnoc.viettel.vn:9000/"
        self.sr_api_url = "https://gnoc.viettel.vn:9003/sr-service/SR/getListSR"
        self.netchat_url = "https://netchat.viettel.vn/api/v4/posts"

    def _load_config(self):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def safe_float(self, val, default=0.0):
        """Ép kiểu float an toàn."""
        try:
            if val is None: return default
            return float(str(val).replace(",", "."))
        except:
            return default

    # ==========================================
    # BƯỚC 1: QUẢN LÝ LOGIN & JWT TOKEN
    # ==========================================
    def check_jwt(self, token):
        """Kiểm tra token thực tế trên cổng 9003 (Dịch vụ SR)."""
        try:
            # Gửi một yêu cầu lấy 1 bản ghi để kiểm tra Token thực tế
            payload = {"page": 1, "pageSize": 1, "country": 281}
            res = requests.post(self.sr_api_url, headers={"Authorization": f"Bearer {token}"}, json=payload, verify=False, timeout=30)
            if res.status_code == 401:
                return 'EXPIRED'
            return 'VALID'
        except requests.exceptions.RequestException as e:
            logger.warning(f"Lỗi kết nối khi kiểm tra Token: {e}")
            return 'CONN_ERROR'
        except Exception as e:
            logger.warning(f"Lỗi không xác định: {e}")
            return 'CONN_ERROR'

    def get_jwt_token(self, force_login=False):
        """Lấy Token: Ưu tiên dùng file cũ, trừ khi force_login=True."""
        if not force_login and os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, "r") as f:
                old_token = f.read().strip()
                status = self.check_jwt(old_token)
                if status == 'VALID':
                    logger.info("🚀 Token sẵn có vẫn tốt, sử dụng tiếp.")
                    self.jwt_token = old_token
                    return True
                elif status == 'CONN_ERROR':
                    logger.warning("⚠️ Lỗi kết nối khi check Token. Sẽ thử đăng nhập lại để làm mới kết nối...")
                    # Thay vì dừng lại, ta thử login mới để xem có cứu vãn được không
                else:
                    logger.info("🔑 Token cũ đã hết hạn thực tế.")

        logger.info("🔑 Đang khởi động Chrome ngầm để lấy Token mới...")
        # ... (giữ nguyên phần Playwright bên dưới)
        try:
            with sync_playwright() as p:
                ctx = p.chromium.launch_persistent_context(
                    user_data_dir=PROFILE_DIR, channel="chrome", headless=True,
                    args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
                )
                
                def capture_req(req):
                    url = req.url
                    auth = req.headers.get("authorization")
                    if auth and auth.lower().startswith("bearer ") and len(auth) > 100:
                        token = auth.split(None, 1)[1].strip()
                        # Chỉ lấy token nếu gọi tới các dịch vụ quan trọng hoặc cổng 9003
                        if "sr-service" in url or "gnoc" in url:
                            self.jwt_token = token
                            logger.info(f"🎯 Đã bắt được Token từ URL: {url[:80]}...")
                            
                page = ctx.pages[0] if ctx.pages else ctx.new_page()
                page.on("request", capture_req)
                page.goto(self.gnoc_url, timeout=90000)
                
                # Đợi một chút để các yêu cầu ngầm được thực hiện hoàn tất
                page.wait_for_load_state("networkidle")

                # Logic đăng nhập
                try:
                    if page.locator("button.password-button").is_visible(timeout=5000):
                        page.click("button.password-button")
                        page.fill("input[type='text']", self.config["username"])
                        page.fill("input[type='password']", self.config["password"])
                        page.click("button[type='submit']")
                        
                        # Xử lý OTP
                        try:
                            page.wait_for_selector(".otp-input", timeout=10000)
                            logger.info("🔐 Hệ thống yêu cầu mã OTP!")
                            otp = input("👉 Nhập mã OTP từ điện thoại: ").strip()
                            for i, char in enumerate(otp):
                                page.locator(".otp-input").nth(i).fill(char)
                                time.sleep(0.05)
                        except: pass
                        
                        # Đăng ký thiết bị nếu cần
                        try:
                            if page.locator("#register-device-yes-btn").is_visible(timeout=5000):
                                page.click("#register-device-toggle")
                                page.click("#register-device-yes-btn")
                        except: pass
                except Exception as e:
                    logger.info(f"✅ Đã có session sẵn hoặc đăng nhập tự động: {e}")

                # Đợi bắt Token
                for _ in range(20):
                    if self.jwt_token: break
                    time.sleep(1)
                
                ctx.close()
        except Exception as e:
            logger.error(f"❌ Lỗi Playwright: {e}")
            
        if self.jwt_token:
            with open(TOKEN_FILE, "w") as f: f.write(self.jwt_token)
            logger.info("✅ Đã cập nhật Token mới thành công.")
            return True
        return False

    # ==========================================
    # BƯỚC 2: TẢI DỮ LIỆU SR (Với Retry)
    # ==========================================
    def _extract_list(self, resp_json):
        """Trích xuất danh sách SR linh hoạt từ JSON trả về."""
        if isinstance(resp_json, list): return resp_json
        if not isinstance(resp_json, dict): return []
        
        d = resp_json.get("data")
        if isinstance(d, list): return d
        if isinstance(d, dict):
            for k in ("records", "list", "rows", "items", "content"):
                v = d.get(k)
                if isinstance(v, list): return v
        return []

    def fetch_sr_data(self):
        """Tải danh sách SR từ API với cơ chế Retry."""
        logger.info("📡 Đang tải danh sách SR...")
        tz_vn = timezone(timedelta(hours=7))
        now_vn = datetime.now(tz_vn)
        start_date = (now_vn.replace(day=1) - timedelta(days=1)).replace(day=1, hour=0, minute=0, second=0)
        
        start_z = start_date.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
        end_z = now_vn.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")

        headers = {"Authorization": f"Bearer {self.jwt_token}", "Content-Type": "application/json"}
        all_sr = []
        page = 1
        max_retries = self.config.get("max_retries", 3)
        
        while page <= 20:
            payload = {
                "page": page, "pageSize": 500, "country": 281, 
                "srUnit": self.config.get("sr_unit_id", "450518"),
                "createFromDate": start_z, "createToDate": end_z,
                "evaluate": "In deadline", 
                "status": self.config.get("sr_status_list")
            }
            
            success = False
            items = []
            for attempt in range(max_retries):
                try:
                    res = requests.post(self.sr_api_url, headers=headers, json=payload, verify=False, timeout=60)
                    if res.status_code == 401:
                        logger.warning("⚠️ Token bị từ chối (401) trong khi tải dữ liệu.")
                        return "REAUTH_NEEDED"
                    res.raise_for_status()
                    data = res.json()
                    
                    items = self._extract_list(data)
                    if not items and page > 1: 
                        success = True
                        break # Hết dữ liệu ở các trang sau
                        
                    all_sr.extend(items)
                    logger.info(f"✅ Đã tải trang {page} (+{len(items)} SR)")
                    success = True
                    break
                except Exception as e:
                    logger.warning(f"⚠️ Thử lại lần {attempt+1}/{max_retries} do lỗi: {e}")
                    time.sleep(self.config.get("retry_delay_sec", 5))
            
            if not success:
                logger.error(f"❌ Không thể tải dữ liệu tại trang {page} sau {max_retries} lần thử.")
                break
                
            if len(items) < 500: break
            page += 1
            
        logger.info(f"✅ Tổng cộng tải được {len(all_sr)} SR.")
        return all_sr

    # ==========================================
    # BƯỚC 3: PHÂN TÍCH & GỬI NETCHAT
    # ==========================================
    def _parse_any_created(self, v):
        """Chuyển đổi chuỗi thời gian từ API sang đối tượng datetime (Linh hoạt)."""
        if not v: return None
        s = str(v).strip().replace("T", " ").replace("Z", "")
        # Thử các định dạng phổ biến
        for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M"):
            try: return datetime.strptime(s, fmt)
            except: pass
        try: return datetime.fromisoformat(s)
        except: return None

    def analyze_and_send(self, raw_sr):
        """Phân tích dữ liệu và gửi báo cáo chi tiết kèm bảng."""
        logger.info("📊 Đang phân tích dữ liệu và chuẩn bị gửi NetChat...")
        now = datetime.now()
        month_now = now.strftime("%m/%Y")
        
        overdue, warning, unapproved, normal = [], [], [], []
        
        for r in raw_sr:
            # Ưu tiên lấy created_dt để sắp xếp, nếu lỗi thì vẫn dùng object raw
            created_dt = self._parse_any_created(r.get("createdTime"))
            r["_created_dt"] = created_dt if created_dt else now
            
            if not r.get("srUser"):
                unapproved.append(r)
                continue

            rem = self.safe_float(r.get("remainExecutionTime"), default=999.0)
            r["remain"] = round(rem, 2)
            
            if rem <= 0: overdue.append(r)
            elif rem < 1.0: warning.append(r)
            else: normal.append(r)

        # Xây dựng nội dung tin nhắn
        msg = [f"📡 **BÁO CÁO SR TRUYỀN DẪN KV1 (DỮ LIỆU MỚI NHẤT)**\n"]
        msg.append(f"🕒 {now.strftime('%H:%M %d/%m/%Y')}\nTháng hiện tại: **{month_now}**\n")
        msg.append(f"Tổng SR đang mở: **{len(overdue) + len(warning) + len(normal) + len(unapproved)}**")
        msg.append(f"🟡 Chưa duyệt: **{len(unapproved)}** | 🟠 Sắp quá hạn: **{len(warning)}** | 🔴 Quá hạn: **{len(overdue)}**\n")
        msg.append("---")

        # Mention người xử lý sắp quá hạn
        if warning:
            users = set([f"@{s.get('srUser')}" for s in warning if s.get('srUser')])
            if users:
                msg.append(f"⚠️ **Nhắc xử lý:** {' '.join(users)}\n")

        # Bảng SR Chưa phê duyệt
        if unapproved:
            msg.append("### 🟡 SR chưa phê duyệt")
            msg.append("| SR | Trạng thái | Tạo lúc | Còn lại |")
            msg.append("|---|---|---|---:|")
            for r in sorted(unapproved, key=lambda x: x.get("_created_dt") or now)[:10]:
                msg.append(f"| {r.get('srCode','')} | {r.get('status','')} | {r['_created_dt'].strftime('%d/%m %H:%M')} | {r.get('remainExecutionTime','?')}d |")
            msg.append("")

        # Bảng SR Sắp quá hạn
        if warning:
            msg.append("### 🟠 SR sắp quá hạn (<1d)")
            msg.append("| SR | Người xử lý | Còn lại | Tạo lúc |")
            msg.append("|---|---|---:|---|")
            for r in sorted(warning, key=lambda x: x.get("remain", 999))[:10]:
                msg.append(f"| {r.get('srCode','')} | {r.get('srUser','')} | {r['remain']}d | {r['_created_dt'].strftime('%d/%m %H:%M')} |")
            msg.append("")

        # Bảng SR Quá hạn
        if overdue:
            msg.append("### 🔴 SR quá hạn (remain=0)")
            msg.append("| SR | Người xử lý | Tạo lúc |")
            msg.append("|---|---|---|")
            for r in sorted(overdue, key=lambda x: x.get("_created_dt") or now)[:15]:
                msg.append(f"| {r.get('srCode','')} | {r.get('srUser','')} | {r['_created_dt'].strftime('%d/%m %H:%M')} |")
            msg.append("")

        # Bảng SR Đang thực hiện (Bình thường)
        if normal:
            msg.append("### 🟢 SR đang thực hiện (còn hạn >1d)")
            msg.append("| SR | Người xử lý | Còn lại | Tạo lúc |")
            msg.append("|---|---|---:|---|")
            for r in sorted(normal, key=lambda x: x.get("remain", 999))[:15]:
                msg.append(f"| {r.get('srCode','')} | {r.get('srUser','')} | {r['remain']}d | {r['_created_dt'].strftime('%d/%m %H:%M')} |")
            msg.append("")

        # Gửi NetChat
        try:
            session = tls_client.Session(client_identifier="chrome_112")
            headers = {"Authorization": f"Bearer {self.config['netchat_token']}", "Content-Type": "application/json"}
            payload = {"channel_id": self.config['netchat_channel_id'], "message": "\n".join(msg)}
            res = session.post(self.netchat_url, headers=headers, json=payload)
            if res.status_code in [200, 201]:
                logger.info("🎉 Đã gửi báo cáo chi tiết thành công!")
            else:
                logger.error(f"❌ Lỗi gửi NetChat: {res.status_code}")
        except Exception as e:
            logger.error(f"❌ Lỗi kết nối NetChat: {e}")

    def run(self):
        try:
            # Lần thử 1
            if self.get_jwt_token():
                sr_data = self.fetch_sr_data()
                
                # Nếu fetch báo cần Re-auth (lỗi 401 giữa chừng)
                if sr_data == "REAUTH_NEEDED":
                    logger.info("🔄 Đang thử đăng nhập lại để lấy Token mới...")
                    if self.get_jwt_token(force_login=True):
                        sr_data = self.fetch_sr_data()
                
                if isinstance(sr_data, list) and sr_data:
                    self.analyze_and_send(sr_data)
                elif sr_data != "REAUTH_NEEDED":
                    logger.warning("⚠️ Không có dữ liệu SR để phân tích.")
            else:
                logger.error("❌ Không lấy được JWT Token. Quy trình dừng.")
        except Exception as e:
            logger.critical(f"💥 LỖI HỆ THỐNG: {e}", exc_info=True)
        logger.info("🏁 Quy trình kết thúc.\n" + "="*40)

if __name__ == "__main__":
    GnocAutomationPipeline().run()
