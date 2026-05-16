import ssl
import os
from datetime import datetime, timezone, timedelta

# --- SSL Configuration ---
SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

def get_base_dir():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def log(msg, symbol="ℹ️"):
    print(f"{symbol} {msg}")

# --- Date Utilities ---
def fmt_utc_z(dt_utc: datetime) -> str:
    """Format time as ISO (YYYY-MM-DDTHH:MM:SS.000Z)."""
    return dt_utc.strftime("%Y-%m-%dT%H:%M:%S.000Z")

def get_tz_vn():
    return timezone(timedelta(hours=7))

def now_vn():
    return datetime.now(get_tz_vn())

def start_of_month(dt: datetime) -> datetime:
    return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

def add_months(dt: datetime, months: int) -> datetime:
    y = dt.year
    m = dt.month + months
    while m > 12:
        y += 1
        m -= 12
    while m < 1:
        y -= 1
        m += 12
    # Keep the day if possible, or cap at last day
    try:
        return dt.replace(year=y, month=m)
    except ValueError:
        # End of month issues
        return dt.replace(year=y, month=m, day=1) + timedelta(days=32)
