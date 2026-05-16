import json
from datetime import datetime
from netchatSend import send_to_netchat

SLA_FMT = "%d/%m/%Y %H:%M:%S"      # ví dụ: 13/02/2026 19:15:00
CREATED_FMT = "%d/%m/%Y %H:%M"     # ví dụ: 12/02/2026 11:45
EPS = 1e-6


def load():
    with open("sr_clean_all.json", "r", encoding="utf-8") as f:
        return json.load(f)


def parse_sla(s: str) -> datetime:
    return datetime.strptime(s, SLA_FMT)


def parse_any_created(v):
    if not v:
        return None
    s = str(v).strip().replace("T", " ").replace("Z", "")
    for fmt in (CREATED_FMT, "%d/%m/%Y %H:%M:%S", SLA_FMT, "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(s, fmt)
        except Exception:
            pass
    try:
        return datetime.fromisoformat(s)
    except Exception:
        return None


def parse_remain_hours(v):
    if v is None:
        return None
    try:
        return float(str(v).replace(",", "."))
    except Exception:
        return None


def is_unapproved(r) -> bool:
    v = r.get("srUser")
    return v is None or str(v).strip() == ""


def is_in_current_month(created_dt: datetime, now: datetime) -> bool:
    return created_dt.year == now.year and created_dt.month == now.month


def classify(rows, now: datetime):
    overdue, warning, normal, unapproved = [], [], [], []

    for r in rows:
        if r.get("status") in ["Closed", "Resolved", "Cancelled"]:
            continue

        created_dt = parse_any_created(r.get("createdTime"))
        if not created_dt:
            continue
        if not is_in_current_month(created_dt, now):
            continue
        r["_created_dt"] = created_dt

        if is_unapproved(r):
            unapproved.append(r)
            continue

        remain = parse_remain_hours(r.get("remainExecutionTime"))
        if remain is None:
            continue
        r["remain"] = round(remain, 2)

        if abs(remain) <= EPS:
            overdue.append(r)
        elif 0 < remain < 1:
            warning.append(r)
        else:
            normal.append(r)

    return overdue, warning, normal, unapproved


def fmt_created_short(r):
    dt = r.get("_created_dt")
    return dt.strftime("%d/%m %H:%M") if dt else ""


def fmt_sla_short(r):
    sla_raw = r.get("sla")
    if not sla_raw:
        return ""
    try:
        return parse_sla(str(sla_raw)).strftime("%d/%m %H:%M")
    except Exception:
        return str(sla_raw)


def build_mentions_overdue(overdue):
    """
    Tạo dòng mention cho các user có SR quá hạn.
    Nếu netchat yêu cầu format khác (ví dụ <@user>), đổi ở đây.
    """
    users = []
    seen = set()
    for r in overdue:
        u = r.get("srUser")
        if not u:
            continue
        u = str(u).strip()
        if not u or u in seen:
            continue
        seen.add(u)
        users.append(u)

    if not users:
        return ""

    # Format mặc định: @username
    return " ".join([f"@{u}" for u in users])


def build_mentions_warning(warning):
    """
    Tạo dòng mention cho các user có SR sắp quá hạn.
    Nếu netchat yêu cầu format khác (ví dụ <@user>), đổi ở đây.
    """
    users = []
    seen = set()
    for r in warning:
        u = r.get("srUser")
        if not u:
            continue
        u = str(u).strip()
        if not u or u in seen:
            continue
        seen.add(u)
        users.append(u)

    if not users:
        return ""

    # Format mặc định: @username
    return " ".join([f"@{u}" for u in users])


def table_unapproved(items):
    lines = []
    lines.append("### 🟡 SR chưa phê duyệt (srUser = null)")
    lines.append("| SR | Trạng thái | Tạo lúc | SLA | Còn lại |")
    lines.append("|---|---|---|---|---:|")

    items.sort(key=lambda x: x.get("_created_dt") or datetime.min)

    for r in items[:15]:
        remain = parse_remain_hours(r.get("remainExecutionTime"))
        remain_disp = "?" if remain is None else round(remain, 2)
        lines.append(
            f"| {r.get('srCode','')} | {r.get('status','')} | {fmt_created_short(r)} | {fmt_sla_short(r)} | {remain_disp}d |"
        )
    return "\n".join(lines)


def table_overdue(items):
    lines = []
    lines.append("### 🔴 SR quá hạn (remain=0)")
    lines.append("| SR | Người xử lý | Tạo lúc | SLA |")
    lines.append("|---|---|---|---|")

    items.sort(key=lambda x: x.get("sla", ""))

    for r in items[:15]:
        lines.append(
            f"| {r.get('srCode','')} | {r.get('srUser','')} | {fmt_created_short(r)} | {fmt_sla_short(r)} |"
        )
    return "\n".join(lines)


def table_warning(items):
    lines = []
    lines.append("### 🟠 Sắp quá hạn (0<remain<1d)")
    lines.append("| SR | Người xử lý | Còn lại | Tạo lúc | SLA |")
    lines.append("|---|---|---:|---|---|")

    items.sort(key=lambda x: x.get("remain", 10**9))

    for r in items[:15]:
        lines.append(
            f"| {r.get('srCode','')} | {r.get('srUser','')} | {r.get('remain','?')}d | {fmt_created_short(r)} | {fmt_sla_short(r)} |"
        )
    return "\n".join(lines)


def build_message():
    now = datetime.now()
    rows = load()

    overdue, warning, normal, unapproved = classify(rows, now)

    mentions_overdue = build_mentions_overdue(overdue)
    mentions_warning = build_mentions_warning(warning)  # Add new mentions for warning SRs

    msg = []
    msg.append("📡 **BÁO CÁO SR TRUYỀN DẪN KV1 (TRONG THÁNG)**")
    msg.append("")
    msg.append(f"🕒 {now:%H:%M %d/%m/%Y}")
    msg.append(f"Tháng báo cáo: **{now:%m/%Y}**")
    msg.append("")
    msg.append(f"Tổng SR (tháng) đang mở: **{len(overdue) + len(warning) + len(normal) + len(unapproved)}**")
    msg.append(f"Chưa phê duyệt: 🟡 **{len(unapproved)}**")
    msg.append(f"Sắp quá hạn (0<remain<1d): 🟠 **{len(warning)}**")
    msg.append(f"Quá hạn (remain=0): 🔴 **{len(overdue)}**")
    msg.append("")
    msg.append("---")
    msg.append("")

    """# Mention user nếu có SR quá hạn
    if mentions_overdue:
        msg.append("🚨 **Nhắc xử lý SR quá hạn:** " + mentions_overdue)
        msg.append("")
    """
    # Mention user nếu có SR sắp quá hạn
    if mentions_warning:
        msg.append("⚠️ **Nhắc xử lý SR sắp quá hạn:** " + mentions_warning)
        msg.append("")

    msg.append(table_unapproved(unapproved))
    msg.append("")
    msg.append(table_warning(warning))
    msg.append("")
    msg.append(table_overdue(overdue))
    return "\n".join(msg)


if __name__ == "__main__":
    message = build_message()
    print(message)
    send_to_netchat(message)