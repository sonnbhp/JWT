# 🚀 Base Automation Template - GNOC & Beyond

Dự án này là khung xương mẫu (Template) dùng để kế thừa cho tất cả các dự án tự động hóa liên quan đến GNOC hoặc các hệ thống Web nội bộ.

## 📁 Cấu trúc quan trọng

1.  **`gnoc_lib/`**: Thư viện chứa logic đăng nhập (JWT), gọi API, và gửi tin nhắn NetChat.
2.  **`AGENTS.md` & `RULES.md`**: Bộ quy tắc giúp AI (Claude) hoạt động đúng vai trò Manager, Core, và UX.
3.  **`.claude/knowledge/`**: Nơi lưu trữ các bài học kinh nghiệm (KI) để AI không mắc lại lỗi cũ.

## 🛠 Hướng dẫn triển khai dự án mới

### Bước 1: Sao chép Template
Copy toàn bộ thư mục này sang vị trí dự án mới của bạn.

### Bước 2: Cấu hình Tài khoản
1. Đổi tên `config.json.example` thành `config.json`.
2. Điền `username` và `password` của bạn vào.

### Bước 3: Cài đặt Môi trường
Chạy lệnh sau để cài đặt các thư viện cần thiết:
```bash
pip install -r requirements.txt
playwright install chrome
```

### Bước 4: Khởi tạo Trí nhớ AI
Để AI bắt đầu làm việc hiệu quả, hãy yêu cầu nó:
1. Đọc file `AGENTS.md` để hiểu vai trò.
2. Chạy lệnh `leankg init` để vẽ bản đồ code (nếu có cài LeanKG).

## 💡 Mẹo kế thừa
- Khi bạn gặp một lỗi khó và đã sửa xong, hãy tạo một file `.md` trong `.claude/knowledge/` để lưu lại. Lần sau ở dự án khác, AI sẽ tự đọc lại bài học này để sửa lỗi nhanh hơn.
- Luôn sử dụng các hàm trong `gnoc_lib` thay vì viết lại code raw để đảm bảo tính ổn định.
