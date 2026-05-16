import urllib.request
import urllib.error
import json
import time
import os
import ssl
from playwright.sync_api import sync_playwright

# --- CẤU HÌNH HỆ THỐNG ---
# URL chính của hệ thống GNOC
GNOC_URL = "https://gnoc.viettel.vn:9000/"
# File chứa thông tin đăng nhập (username, password)
CONFIG_FILE = "config.json"
# File để lưu trữ Token JWT sau khi lấy được
TOKEN_FILE = "gnoc_token.txt"
# Đường dẫn thư mục hiện tại của script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Thư mục lưu trữ dữ liệu trình duyệt (để nhớ trạng thái đăng nhập, tránh đòi OTP nhiều lần)
PROFILE_DIR = os.path.expanduser("~/.gnoc_browser_profile")

# Cấu hình bỏ qua kiểm tra chứng chỉ SSL (vì GNOC dùng https nội bộ có thể gây lỗi SSL)
SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

class GnocLoginTool:
    """Lớp chính điều khiển toàn bộ quy trình đăng nhập và lấy Token."""
    
    def __init__(self):
        # Khởi tạo các biến cơ bản
        self.jwt_token = None
        self.config = self._load_config()
        self.token_path = os.path.join(BASE_DIR, TOKEN_FILE)

    def _load_config(self):
        """Đọc file config.json để lấy Username và Password."""
        path = os.path.join(BASE_DIR, CONFIG_FILE)
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def log(self, msg, symbol="ℹ️"):
        """Hàm hỗ trợ in thông báo ra màn hình Terminal với biểu tượng."""
        print(f"{symbol} {msg}")

    def validate_existing_token(self):
        """Kiểm tra xem Token cũ trong file gnoc_token.txt còn dùng được không."""
        if not os.path.exists(self.token_path):
            return False # Không có file token thì coi như hết hạn
            
        with open(self.token_path, "r", encoding="utf-8") as f:
            token = f.read().strip()
            
        # Gọi hàm kiểm tra kết nối và tính hiệu lực
        status = self.check_connectivity_and_token(token)
        if status == 'VALID':
            self.jwt_token = token
            return True
        elif status == 'CONN_ERROR':
            # Nếu lỗi kết nối (chưa bật VPN) thì dừng luôn
            self.log("Dừng quy trình: VPN chưa được kết nối. Hãy bật Suite Agent!", "🛑")
            exit(0)
        return False # Token hết hạn hoặc lỗi khác

    def check_connectivity_and_token(self, token):
        """
        Gửi một yêu cầu thử tới GNOC để xác định:
        - VALID: Kết nối tốt, Token đúng.
        - EXPIRED: Kết nối tốt, nhưng Token sai/hết hạn.
        - CONN_ERROR: Không thể kết nối tới server (thường do chưa bật VPN).
        """
        self.log("Đang kiểm tra kết nối và token...")
        try:
            req = urllib.request.Request(GNOC_URL)
            req.add_header("Authorization", f"Bearer {token}")
            # Thử mở URL với timeout 5 giây
            with urllib.request.urlopen(req, context=SSL_CTX, timeout=5) as res:
                if res.status == 200:
                    return 'VALID'
        except urllib.error.HTTPError as e:
            # Nếu server trả về 401 Unauthorized nghĩa là Token hết hạn
            return 'EXPIRED' if e.code == 401 else 'VALID'
        except urllib.error.URLError:
            # Lỗi này thường do không tìm thấy host (chưa bật VPN)
            return 'CONN_ERROR'
        return 'UNKNOWN'

    def capture_jwt_handler(self, req):
        """
        Hàm xử lý sự kiện: Mỗi khi trình duyệt gửi một yêu cầu (request), 
        hàm này sẽ kiểm tra xem trong Header có chứa Token Bearer không.
        """
        try:
            auth = req.headers.get("authorization")
            if auth and auth.lower().startswith("bearer "):
                token = auth.split(None, 1)[1].strip()
                # Kiểm tra độ dài để chắc chắn đây là chuỗi JWT xịn
                if len(token) > 100: 
                    self.jwt_token = token
                    # Lưu ngay vào file khi vừa bắt được
                    with open(self.token_path, "w", encoding="utf-8") as f:
                        f.write(token)
        except:
            pass

    def run_automation(self):
        """Khởi động trình duyệt ngầm để thực hiện đăng nhập tự động."""
        with sync_playwright() as p:
            self.log("Khởi động Chrome (Chế độ chạy ngầm)...", "🚀")
            # Mở trình duyệt với Profile cố định để nhớ trạng thái login
            browser_ctx = p.chromium.launch_persistent_context(
                user_data_dir=PROFILE_DIR,
                channel="chrome",
                headless=True, # Chạy ẩn, không hiện cửa sổ
                ignore_https_errors=True,
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
                viewport={'width': 1280, 'height': 800}
            )
            
            try:
                page = browser_ctx.pages[0] if browser_ctx.pages else browser_ctx.new_page()
                # Đăng ký hàm bắt Token
                page.on("request", self.capture_jwt_handler)

                self.log(f"Đang truy cập hệ thống: {GNOC_URL}", "🌐")
                page.goto(GNOC_URL, timeout=60000)
                
                # Kiểm tra xem hệ thống có yêu cầu đăng nhập bằng mật khẩu không
                try:
                    page.wait_for_selector("button.password-button", timeout=5000)
                    self.log("Phát hiện màn hình đăng nhập.", "🔑")
                    
                    # Thực hiện click nút đăng nhập và điền User/Pass
                    page.click("button.password-button")
                    page.fill("input[type='text']", self.config["username"])
                    page.fill("input[type='password']", self.config["password"])
                    page.click("button[type='submit']")
                    
                    # Kiểm tra xem có bị hỏi mã OTP (2-Step Verification) không
                    try:
                        page.wait_for_selector(".otp-input", timeout=10000)
                        self.log("Hệ thống yêu cầu mã OTP!", "🔐")
                        # Tạm dừng script để người dùng nhập OTP từ điện thoại vào Terminal
                        otp = input("👉 Nhập mã OTP từ điện thoại của bạn: ").strip()
                        if otp:
                            # Điền từng chữ số vào các ô OTP tương ứng
                            for i, char in enumerate(otp):
                                page.locator(".otp-input").nth(i).fill(char)
                                time.sleep(0.05)
                    except:
                        pass # Nếu không thấy ô OTP thì bỏ qua bước này
                    
                    # Xử lý màn hình "Tin cậy thiết bị này" (Remember this device)
                    try:
                        page.wait_for_selector("#register-device-yes-btn", timeout=5000)
                        page.click("#register-device-toggle") # Tích vào checkbox nhớ thiết bị
                        page.click("#register-device-yes-btn") # Nhấn đồng ý
                        self.log("Đã xác nhận tin cậy thiết bị.", "✅")
                    except:
                        pass
                except:
                    # Nếu không thấy nút Login, có thể do trình duyệt đã tự đăng nhập từ trước
                    self.log("Phiên làm việc vẫn còn hiệu lực, không cần đăng nhập lại.", "✅")

                # Sau khi đăng nhập, đợi một lúc để script bắt được chuỗi JWT từ các request ngầm
                self.log("Đang chờ hệ thống đồng bộ và bắt chuỗi JWT...", "⏳")
                for _ in range(20): # Đợi tối đa 20 giây
                    if self.jwt_token: break
                    time.sleep(1)
                
                if self.jwt_token:
                    self.log(f"Thành công! Token đã được lưu vào {TOKEN_FILE}", "🎉")
                else:
                    self.log("Cảnh báo: Không tìm thấy token mới trong phiên này.", "⚠️")

            finally:
                # Đảm bảo trình duyệt luôn được đóng để giải phóng RAM
                browser_ctx.close()

    def start(self):
        """Điểm bắt đầu của ứng dụng."""
        # Bước 1: Thử dùng token cũ xem còn hạn không
        if self.validate_existing_token():
            self.log(f"Token cũ vẫn dùng tốt, sử dụng luôn: {self.jwt_token[:30]}...", "🚀")
            return
        
        # Bước 2: Nếu token cũ hỏng, chạy trình duyệt để lấy cái mới
        self.run_automation()
        self.log("Toàn bộ quy trình đã hoàn tất.", "🏁")

# Lệnh khởi chạy script
if __name__ == "__main__":
    tool = GnocLoginTool()
    tool.start()
