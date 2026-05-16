import tls_client
import json

API_URL = "https://netchat.viettel.vn/api/v4/posts"
"""
# --- Kênh chat test---
TOKEN = "qfjjoah3gtfcffjwurrdfbir3w"
CHANNEL_ID = "hxrxqxaj1idbjjtj9jgz6dhywo"
"""
TOKEN = "qfjjoah3gtfcffjwurrdfbir3w"
CHANNEL_ID = "hxrxqxaj1idbjjtj9jgz6dhywo"

def send_to_netchat(message):

    # giả Chrome 120
    session = tls_client.Session(
        client_identifier="chrome120"
    )

    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://netchat.viettel.vn",
        "Referer": "https://netchat.viettel.vn/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    payload = {
        "channel_id": CHANNEL_ID,
        "message": message
    }

    r = session.post(
        API_URL,
        headers=headers,
        data=json.dumps(payload)
    )

    print("STATUS:", r.status_code)
    print(r.text)
