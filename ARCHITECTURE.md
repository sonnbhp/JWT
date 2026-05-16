# 🏗️ Kiến Trúc Hệ Thống GNOC Automation

Dự án được xây dựng theo mô hình Multi-agent Orchestration.

## 1. Thành phần Logic (Backend)
- **`gnoc_auto_report.py`**: Pipeline cốt lõi xử lý Authenticate, Fetch, Analyze và Notify.
- **`config.json`**: Quản lý tham số và cấu hình hệ thống.
- **`gnoc_token.txt`**: Lưu trữ JWT tạm thời.

## 2. Hệ thống Agent (Orchestration Layer)
- **@A-Manager**: Điều phối, lập kế hoạch và quản lý tri thức (`.claude/knowledge/`).
- **@A-Core**: Xử lý logic nghiệp vụ và API.
- **@A-UX**: Định dạng hiển thị và trải nghiệm báo cáo.
- **@A-Test**: Kiểm thử, xác minh kết nối và tính chính xác dữ liệu.

## 3. Luồng dữ liệu (Data Flow)
1. `check_jwt` -> 2. `get_jwt_token` (Playwright) -> 3. `fetch_sr_data` (Requests) -> 4. `analyze_and_send` (tls_client).
