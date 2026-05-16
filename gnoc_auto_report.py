import os
import json
import time
import ssl
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
PROFILE_DIR = os.path.expanduser("~/.gnoc_browser_profile")

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

    def log(self, msg, symbol="ℹ️"):
        print(f"{symbol} {msg}")

    # ==========================================
    # BƯỚC 1: QUẢN LÝ LOGIN & JWT TOKEN
    # ==========================================
    def check_jwt(self, token):
        """Kiểm tra token còn hạn hay không."""
        try:
            req = urllib.request.Request(self.gnoc_url)
            req.add_header("Authorization", f"Bearer {token}")
            with urllib.request.urlopen(req, context=SSL_CTX, timeout=5) as res:
                return 'VALID' if res.status == 200 else 'EXPIRED'
        except urllib.error.HTTPError as e:
            return 'EXPIRED' if e.code == 401 else 'VALID'
        except:
            return 'CONN_ERROR'

    def get_jwt_token(self):
        """Lấy Token: Ưu tiên dùng file cũ, nếu hỏng thì dùng Playwright."""
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, "r") as f:
                old_token = f.read().strip()
                status = self.check_jwt(old_token)
                if status == 'VALID':
                    self.log("Token sẵn có vẫn tốt, bỏ qua bước đăng nhập.", "🚀")
                    self.jwt_token = old_token
                    return True
                elif status == 'CONN_ERROR':
                    self.log("Lỗi kết nối GNOC. Hãy kiểm tra VPN!", "🚫")
                    return False

        self.log("Token hết hạn hoặc không tồn tại. Đang khởi động Chrome ngầm...", "🔑")
        with sync_playwright() as p:
            ctx = p.chromium.launch_persistent_context(
                user_data_dir=PROFILE_DIR, channel="chrome", headless=True,
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
            )
            
            def capture_req(req):
                auth = req.headers.get("authorization")
                if auth and auth.lower().startswith("bearer ") and len(auth) > 100:
                    self.jwt_token = auth.split(None, 1)[1].strip()
            
            page = ctx.pages[0] if ctx.pages else ctx.new_page()
            page.on("request", capture_req)
            page.goto(self.gnoc_url, timeout=60000)

            try:
                page.wait_for_selector("button.password-button", timeout=5000)
                page.click("button.password-button")
                page.fill("input[type='text']", self.config["username"])
                page.fill("input[type='password']", self.config["password"])
                page.click("button[type='submit']")
                
                try:
                    page.wait_for_selector(".otp-input", timeout=10000)
                    self.log("Yêu cầu OTP!", "🔐")
                    otp = input("👉 Nhập mã OTP từ điện thoại: ").strip()
                    for i, char in enumerate(otp):
                        page.locator(".otp-input").nth(i).fill(char)
                        time.sleep(0.05)
                except: pass
                
                try:
                    page.wait_for_selector("#register-device-yes-btn", timeout=5000)
                    page.click("#register-device-toggle")
                    page.click("#register-device-yes-btn")
                except: pass
            except:
                self.log("Đã đăng nhập trước đó.", "✅")

            for _ in range(20):
                if self.jwt_token: break
                time.sleep(1)
            
            ctx.close()
            
        if self.jwt_token:
            with open(TOKEN_FILE, "w") as f: f.write(self.jwt_token)
            return True
        return False

    # ==========================================
    # BƯỚC 2: TẢI DỮ LIỆU SR
    # ==========================================
    def fetch_sr_data(self):
        """Tải danh sách SR từ API."""
        self.log("Đang tải danh sách SR...", "📡")
        tz_vn = timezone(timedelta(hours=7))
        now_vn = datetime.now(tz_vn)
        start_date = (now_vn.replace(day=1) - timedelta(days=1)).replace(day=1, hour=0, minute=0, second=0)
        
        start_z = start_date.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
        end_z = now_vn.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")

        headers = {"Authorization": f"Bearer {self.jwt_token}", "Content-Type": "application/json"}
        all_sr = []
        page = 1
        
        while page <= 10: # Giới hạn 10 trang
            payload = {
                "page": page, "pageSize": 500, "country": 281, "srUnit": "450518",
                "createFromDate": start_z, "createToDate": end_z,
                "evaluate": "In deadline", "status": "Assigned_Planning,Evaluated,Execution_Halted,New,Planned"
            }
            res = requests.post(self.sr_api_url, headers=headers, json=payload, verify=False)
            items = res.json().get("data", {}).get("records", [])
            if not items: break
            all_sr.extend(items)
            if len(items) < 500: break
            page += 1
            
        self.log(f"Đã tải {len(all_sr)} SR.", "✅")
        return all_sr

    # ==========================================
    # BƯỚC 3: PHÂN TÍCH & GỬI NETCHAT
    # ==========================================
    def analyze_and_send(self, raw_sr):
        """Phân tích dữ liệu và gửi báo cáo."""
        self.log("Đang phân tích dữ liệu và gửi NetChat...", "📊")
        now_str = datetime.now().strftime("%H:%M %d/%m/%Y")
        month_now = datetime.now().strftime("%m/%Y")
        
        opened = [s for s in raw_sr if s.get("createdTime", "").startswith(datetime.now().strftime("%Y-%m"))]
        unapproved = [s for s in opened if not s.get("srUser")]
        overdue = [s for s in opened if s.get("remainExecutionTime") == "0"]
        near_due = [s for s in opened if s.get("remainExecutionTime") != "0" and float(s.get("remainExecutionTime", 0)) < 1.0]

        report = f"📡 **BÁO CÁO SR TRUYỀN DẪN KV1**\n\n"
        report += f"🕒 {now_str}\nTháng: **{month_now}**\n\n"
        report += f"Tổng SR đang mở: **{len(opened)}**\n"
        report += f"🟡 Chưa duyệt: **{len(unapproved)}**\n"
        report += f"🟠 Sắp quá hạn: **{len(near_due)}**\n"
        report += f"🔴 Quá hạn: **{len(overdue)}**\n\n"
        
        if near_due:
            report += "⚠️ **Nhắc xử lý:** " + " ".join(set([f"@{s.get('srUser')}" for s in near_due if s.get('srUser')]))

        # Gửi NetChat
        session = tls_client.Session(client_identifier="chrome_112")
        headers = {"Authorization": f"Bearer {self.config['netchat_token']}", "Content-Type": "application/json"}
        payload = {"channel_id": self.config['netchat_channel_id'], "message": report}
        
        res = session.post(self.netchat_url, headers=headers, json=payload)
        if res.status_code == 201:
            self.log("Đã gửi báo cáo thành công lên NetChat!", "🎉")
        else:
            self.log(f"Lỗi gửi NetChat: {res.status_code} - {res.text}", "❌")

    def run(self):
        if self.get_jwt_token():
            sr_data = self.fetch_sr_data()
            if sr_data:
                self.analyze_and_send(sr_data)
        self.log("Quy trình kết thúc.", "🏁")

if __name__ == "__main__":
    GnocAutomationPipeline().run()
