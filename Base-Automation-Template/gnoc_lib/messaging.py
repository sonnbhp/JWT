import requests
import json
from .common import log

NETCHAT_API = "https://netchat.viettel.vn/api/v4/posts"

class NetChatClient:
    def __init__(self, token, channel_id):
        self.token = token
        self.channel_id = channel_id
        self.session = requests.Session()
        self.session.verify = False

    def send_message(self, message):
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        payload = {
            "channel_id": self.channel_id,
            "message": message
        }
        try:
            r = self.session.post(NETCHAT_API, headers=headers, data=json.dumps(payload))
            if r.status_code in [200, 201]:
                log("Đã gửi tin nhắn NetChat thành công.", "✉️")
                return True
            else:
                log(f"Lỗi gửi NetChat ({r.status_code}): {r.text}", "❌")
                return False
        except Exception as e:
            log(f"Lỗi kết nối NetChat: {e}", "❌")
            return False
