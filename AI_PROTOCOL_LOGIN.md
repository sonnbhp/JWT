# 🤖 AI Protocol: GNOC Login Tool (`login.py`)

Tài liệu này định nghĩa cấu trúc, logic vận hành và các tiêu chuẩn phát triển cho script `login.py`.

## 1. Mục tiêu (Objective)
Tự động hóa việc trích xuất JWT Token từ hệ thống GNOC Viettel, hỗ trợ đa nền tảng (Windows/macOS), chạy ở chế độ ẩn danh (Headless) và xử lý xác thực 2 lớp (OTP) qua Command Line.

## 2. Kiến trúc mã nguồn (Code Architecture)
Mã nguồn được viết theo mô hình hướng đối tượng (OOP) thông qua lớp `GnocLoginTool`.

### Các thành phần chính:
- **`validate_existing_token()`**: Kiểm tra token sẵn có. Trả về `VALID` nếu ok, `CONN_ERROR` nếu chưa bật VPN.
- **`run_automation()`**: Khởi động Playwright (Chromium) để thực hiện luồng login.
- **`capture_jwt_handler()`**: Bắt Token Bearer từ Network Request Header.
- **`PROFILE_DIR`**: Sử dụng Persistent Context để duy trì session (nhớ thiết bị), giảm tần suất đòi OTP.

## 3. Quy trình thực hiện (Execution Flow)
1. **Khởi tạo**: Đọc `config.json` -> Xác định đường dẫn file token.
2. **Kiểm tra nhanh**: Gọi API `urllib` để check token cũ.
   - Nếu Token lỗi kết nối: Dừng và báo bật VPN.
   - Nếu Token hợp lệ: Kết thúc sớm.
3. **Tự động hóa (nếu cần)**:
   - Mở Chrome Headless.
   - Điền User/Pass.
   - Nếu gặp `.otp-input`: Dừng chờ `input()` từ người dùng.
   - Nếu gặp `#register-device-yes-btn`: Tự động click để "Tin cậy thiết bị".
4. **Đồng bộ**: Đợi tối đa 20s để bắt được JWT mới qua Listener.
5. **Dọn dẹp**: Đóng Browser Context và lưu Token vào file.

## 4. Hướng dẫn bảo trì cho AI (Maintenance for AI)
Khi thực hiện thay đổi, hãy tuân thủ các nguyên tắc:
- **Xử lý SSL**: Luôn sử dụng `SSL_CTX` (ignore verify) vì hệ thống GNOC thường gặp lỗi chứng chỉ nội bộ.
- **Headless Mode**: Mặc định luôn để `headless: True` để đảm bảo trải nghiệm "Silent Execution".
- **Chế độ đa nền tảng**: Tránh sử dụng các thư viện đặc thù của OS (như `applescript` cho Mac hoặc `win32api` cho Windows) trong file này.
- **Độ trễ (Delays)**: Do GNOC là Webview/Single Page App, luôn sử dụng `wait_for_selector` thay vì `time.sleep` cố định.

## 5. Các tham số cấu hình (Configuration)
- `GNOC_URL`: Cửa trang chủ hệ thống.
- `CONFIG_FILE`: Chứa `username`, `password`.
- `TOKEN_FILE`: File đầu ra `gnoc_token.txt`.

---
*Protocol Version: 1.0.0*
