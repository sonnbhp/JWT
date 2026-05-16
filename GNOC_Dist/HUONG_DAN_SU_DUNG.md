# HƯỚNG DẪN SỬ DỤNG GNOC AUTO TOOL (STANDALONE EXE)

## 1. Giới thiệu
Đây là công cụ tự động hóa lấy báo cáo SR từ hệ thống GNOC và gửi qua NetChat. Công cụ đã được đóng gói thành duy nhất **01 file thực thi (.exe)**, không cần cài đặt Python hay thư viện.

## 2. Cấu trúc thư mục chạy
Để công cụ hoạt động, bạn chỉ cần đặt 2 file này ở cùng một thư mục:
- `GNOC_Auto_Tool.exe`: File chương trình chính.
- `config.json`: File chứa thông tin cấu hình (Tài khoản, Token NetChat, ID Channel).

## 3. Cách sử dụng
1.  Chỉnh sửa file `config.json` với thông tin cá nhân của bạn.
2.  Click đúp vào file `GNOC_Auto_Tool.exe`.
3.  Chương trình sẽ tự động:
    - Kiểm tra Token cũ.
    - Nếu hết hạn, tự khởi động Chrome ngầm để lấy Token mới (Yêu cầu máy có cài Google Chrome).
    - Tải danh sách SR.
    - Phân tích và gửi báo cáo vào NetChat.
4.  Sau khi xong, nhấn **Enter** để đóng cửa sổ.

## 4. Lưu ý quan trọng
- **Google Chrome:** Máy tính chạy tool **phải cài sẵn Google Chrome** bản mới nhất.
- **Quyền truy cập:** Đảm bảo file `.exe` và `config.json` nằm ở thư mục có quyền ghi (Ví dụ: `C:\GNOC_Tool` hoặc `Desktop`). Không nên để trong `C:\Program Files`.
- **Virus Scanner:** Do file `.exe` được đóng gói từ Python, một số trình duyệt hoặc Windows Defender có thể cảnh báo "Unknown Publisher". Bạn hãy chọn "Run anyway" để khởi chạy.

## 5. Cập nhật mã nguồn
Nếu bạn muốn thay đổi logic và đóng gói lại:
1.  Sửa file `gnoc_auto_report.py`.
2.  Chạy PowerShell: `.\build_exe.ps1`.
3.  File EXE mới sẽ nằm trong thư mục `dist/`.

---
*Phiên bản ổn định v2.2 - (c) 2024*
