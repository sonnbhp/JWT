# 🦾 Giao thức AI Vận hành GNOC (AI Protocol)

Đây là các quy chuẩn bắt buộc cho mọi AI Assistant khi tương tác với dự án này.

### I. Quy trình Xác thực (Authentication)
1. **Kiểm tra trước khi Login**: Luôn kiểm tra tính hiệu lực của Token trong `gnoc_token.txt` bằng cách gọi API thử nghiệm tới cổng `9003`.
2. **Login ngầm (Headless Mode)**: Chỉ sử dụng Playwright ở chế độ `headless=True`. Sử dụng `launch_persistent_context` để tận dụng lại Cookies/Session cũ, tránh bắt người dùng nhập OTP nhiều lần.
3. **Capture Logic**: Bắt Token từ `Authorization` header của các yêu cầu XHR. Chỉ tin tưởng Token từ các URL có chứa `sr-service`.

### II. Quy trình Lấy dữ liệu (Data Retrieval)
1. **Cấu hình động**: Tuyệt đối không hard-code mã đơn vị hay trạng thái. Phải đọc từ `config.json`.
2. **Bảo vệ kết nối**:
   - `Timeout`: Mặc định 30 giây.
   - `Retry`: Tối thiểu 3 lần cho mỗi trang dữ liệu.
   - `SSL`: Bỏ qua xác thực chứng chỉ (`verify=False`) để phù hợp với mạng nội bộ.
3. **Xử lý 401**: Nếu nhận mã lỗi 401 khi đang tải dữ liệu, AI phải chủ động quay lại bước Login để làm mới Token.

### III. Quy trình Báo cáo (Reporting)
1. **Phân loại SR**: Chia dữ liệu thành 4 nhóm (Chưa duyệt, Sắp quá hạn, Quá hạn, Bình thường).
2. **Định dạng**: Sử dụng bảng Markdown. Mention người dùng bằng cú pháp `@username`.
3. **Kênh gửi**: Sử dụng `tls_client` để gửi tới NetChat nhằm đảm bảo tính bảo mật và giả lập vân tay trình duyệt chuẩn xác.

### IV. Xử lý lỗi (Error Handling)
1. **Log trước, dừng sau**: Mọi lỗi phải được ghi vào `gnoc_auto.log` kèm theo traceback chi tiết.
2. **Thông báo VPN**: Nếu không phân giải được tên miền, phải thông báo rõ cho người dùng: "Hãy kiểm tra và kết nối lại VPN".
