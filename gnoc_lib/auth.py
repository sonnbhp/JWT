import os
import json
import time
import urllib.request
import urllib.error
from playwright.sync_api import sync_playwright
from .common import SSL_CTX, log, get_base_dir

GNOC_URL = "https://gnoc.viettel.vn:9000/"
PROFILE_DIR = os.path.expanduser("~/.gnoc_browser_profile")

class GnocLoginTool:
    def __init__(self, config_path="config.json", token_file="gnoc_token.txt"):
        self.base_dir = get_base_dir()
        self.config_path = os.path.join(self.base_dir, config_path)
        self.token_path = os.path.join(self.base_dir, token_file)
        self.jwt_token = None
        self.config = self._load_config()

    def _load_config(self):
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Config file not found at {self.config_path}")
        with open(self.config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def load_cached_token(self):
        if os.path.exists(self.token_path):
            with open(self.token_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        return None

    def validate_token(self, token):
        try:
            req = urllib.request.Request(GNOC_URL)
            req.add_header("Authorization", f"Bearer {token}")
            with urllib.request.urlopen(req, context=SSL_CTX, timeout=5) as res:
                return res.status == 200
        except urllib.error.HTTPError as e:
            return e.code != 401
        except:
            return False

    def capture_jwt_handler(self, req):
        auth = req.headers.get("authorization")
        if auth and auth.lower().startswith("bearer "):
            token = auth.split(None, 1)[1].strip()
            if len(token) > 100:
                self.jwt_token = token
                with open(self.token_path, "w", encoding="utf-8") as f:
                    f.write(token)

    def login_and_get_token(self, headless=True):
        with sync_playwright() as p:
            log("Khởi động trình duyệt...", "🚀")
            browser_ctx = p.chromium.launch_persistent_context(
                user_data_dir=PROFILE_DIR,
                channel="chrome",
                headless=headless,
                ignore_https_errors=True,
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
            )
            try:
                page = browser_ctx.pages[0] if browser_ctx.pages else browser_ctx.new_page()
                page.on("request", self.capture_jwt_handler)
                page.goto(GNOC_URL, timeout=60000)
                
                try:
                    page.wait_for_selector("button.password-button", timeout=5000)
                    page.click("button.password-button")
                    page.fill("input[type='text']", self.config["username"])
                    page.fill("input[type='password']", self.config["password"])
                    page.click("button[type='submit']")
                    
                    try:
                        page.wait_for_selector(".otp-input", timeout=10000)
                        log("⚠️ Cần nhập OTP!", "🔐")
                        otp = input("👉 Nhập mã OTP: ").strip()
                        if otp:
                            for i, char in enumerate(otp):
                                page.locator(".otp-input").nth(i).fill(char)
                    except: pass
                except:
                    log("Đã có phiên đăng nhập sẵn.", "✅")

                for _ in range(15):
                    if self.jwt_token: break
                    time.sleep(1)
                
                return self.jwt_token
            finally:
                browser_ctx.close()

    def get_token(self, force_refresh=False):
        if not force_refresh:
            token = self.load_cached_token()
            if token and self.validate_token(token):
                self.jwt_token = token
                return token
        
        return self.login_and_get_token()
