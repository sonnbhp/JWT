import requests
import json
import urllib3
from .common import fmt_utc_z, log

urllib3.disable_warnings()

SR_API_URL = "https://gnoc.viettel.vn:9003/sr-service/SR/getListSR"

class SRService:
    def __init__(self, token):
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json;charset=UTF-8",
            "Accept": "application/json"
        }

    def fetch_sr_list(self, from_date_z, to_date_z, country=281, unit="450518", page_size=1000):
        payload = {
            "page": 1,
            "pageSize": page_size,
            "country": country,
            "srUnit": unit,
            "createFromDate": from_date_z,
            "createToDate": to_date_z,
            "evaluate": "In deadline",
            "status": "Assigned_Planning,Evaluated,Execution_Halted,New,Planned"
        }
        
        all_items = []
        page = 1
        while True:
            payload["page"] = page
            log(f"Đang tải SR trang {page}...", "📥")
            r = requests.post(SR_API_URL, headers=self.headers, json=payload, verify=False, timeout=60)
            if r.status_code != 200:
                break
            
            data = r.json().get("data", [])
            # Handle different response structures
            items = data if isinstance(data, list) else data.get("records", [])
            
            if not items:
                break
            
            all_items.extend(items)
            if len(items) < page_size:
                break
            page += 1
            if page > 100: break # Safety break
            
        return all_items

    @staticmethod
    def simplify_sr(sr):
        return {
            "srCode": sr.get("srCode"),
            "title": sr.get("title"),
            "status": sr.get("statusName"),
            "service": sr.get("serviceName"),
            "createdTime": sr.get("createdTime"),
            "unit": sr.get("pathSrUnit"),
            "creator": sr.get("createdUser")
        }
