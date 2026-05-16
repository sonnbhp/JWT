# 📒 Nhật ký Tối ưu & Lưu ý Vận hành (Automation Notes)

Tài liệu này lưu lại các "mẹo" và giải pháp cho những lỗi đặc thù của hệ thống GNOC.

### 1. Xác thực & Quản lý Token (JWT)
- **Cổng 9003 là chân lý**: Đừng chỉ kiểm tra Token ở trang chủ (cổng 9000). Hãy kiểm tra trực tiếp trên dịch vụ SR (cổng 9003) vì Token có thể hợp lệ ở Portal nhưng lại bị từ chối ở API nghiệp vụ.
- **Bắt Token linh hoạt**: Trong Playwright, phải đợi trạng thái `networkidle` để đảm bảo bắt được Token từ các yêu cầu ngầm. Luôn lọc Token theo URL chứa từ khóa `sr-service` hoặc `gnoc`.
- **Cơ chế Tự phục hồi**: Nếu gặp lỗi **401 Unauthorized** trong khi đang chạy, phải lập tức xóa Token cũ và kích hoạt quy trình Login mới.

### 2. Xử lý mạng VPN & Kết nối
- **Timeout cao**: Mạng VPN thường rất chậm và chập chờn. Luôn để `timeout` tối thiểu 30-60 giây cho các yêu cầu API.
- **Nhận diện lỗi DNS**: Lỗi `[Errno 8] nodename nor servname provided` là dấu hiệu 100% VPN bị ngắt. Hãy thông báo cho người dùng kết nối lại VPN.
- **Cơ chế Retry**: Luôn bọc các lệnh gọi API bằng vòng lặp `Retry` (tối thiểu 3 lần) để vượt qua các giây phút mạng bị lag.

### 3. Định dạng Dữ liệu API GNOC
- **Cấu trúc biến thiên**: API GNOC lúc trả về `List`, lúc trả về `Dict`. Hàm trích xuất dữ liệu phải kiểm tra `isinstance(data, list)` trước khi xử lý.
- **Ngày tháng phức tạp**: Định dạng `createdTime` có thể chứa phần nghìn giây (`.000Z`). Sử dụng `datetime.fromisoformat` hoặc `strptime` với `%f` để tránh lỗi phân tích.

### 4. Báo cáo NetChat
- **Định dạng Bảng**: Sử dụng Markdown Table để báo cáo chi tiết SR. Giới hạn 15 bản ghi mỗi bảng để tránh tin nhắn quá dài.
- **Mention tự động**: Luôn tag tên người xử lý (`@username`) cho các đầu việc sắp quá hạn để tăng tốc độ phản ứng.
