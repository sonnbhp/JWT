# 📡 GNOC Mobility Suite Automation

Hệ thống tự động hóa việc lấy dữ liệu Service Request (SR) từ GNOC Viettel, phân tích và gửi báo cáo thông minh lên NetChat.

## 🚀 Tính năng nổi bật
- **Auto-Login**: Tự động vượt qua bước đăng nhập bằng Playwright để lấy JWT.
- **Resilience**: Tự động thử lại khi mạng VPN chập chờn hoặc Token hết hạn.
- **Smart Report**: Phân loại SR theo mức độ ưu tiên (Quá hạn, Sắp quá hạn, Chưa duyệt) kèm bảng chi tiết.
- **Multi-Agent**: Đội ngũ AI chuyên biệt giúp vận hành và bảo trì hệ thống.

## 🛠 Hướng dẫn sử dụng
1. Kết nối VPN Viettel.
2. Cấu hình các tham số cần thiết trong `config.json`.
3. Chạy lệnh:
   ```bash
   python3 gnoc_auto_report.py
   ```

## 👥 Đội ngũ vận hành
Xem chi tiết tại [AGENTS.md](AGENTS.md).
