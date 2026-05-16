# KI: Xử lý mạng VPN chập chờn và Timeout

## 🔴 Problem
Script thường xuyên bị lỗi "Read timed out" hoặc "Failed to resolve" khi chạy trên môi trường VPN Viettel.

## 🔍 Root Cause
Đường truyền VPN có độ trễ cao và DNS nội bộ đôi khi không ổn định, dẫn đến việc các request mặc định (10-15s) bị đóng trước khi nhận được phản hồi.

## ✅ Solution
- Tăng `timeout` lên tối thiểu 30 giây cho các API nghiệp vụ và 90 giây cho Playwright `goto`.
- Triển khai vòng lặp Retry (tối thiểu 3 lần) cho mọi request quan trọng.
- Xử lý ngoại lệ `NameResolutionError` để thông báo người dùng kết nối lại VPN thay vì crash chương trình.

## 🛡️ Prevention
Check kết nối VPN (DNS check) ngay tại hàm `main` trước khi thực hiện các logic tốn kém khác.
