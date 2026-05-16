# 📜 Hiến Pháp Dự Án (Iron Rules)

Các quy tắc sau đây là **BẮT BUỘC** đối với mọi AI Assistant khi tham gia vào dự án này:

### 1. Phân tích trước khi thực thi (LeanKG)
- **Luật**: KHÔNG ĐƯỢC CHẠM VÀO LOGIC CỐT LÕI (như quy trình lấy Token, phân tích dữ liệu SR) nếu chưa dùng **LeanKG** để quét Blast Radius (vùng ảnh hưởng).
- **Mục đích**: Tránh việc sửa code chỗ này làm hỏng tính năng chỗ kia.

### 2. Xác minh kết quả UI/Automation (Puppeteer)
- **Luật**: KHÔNG ĐƯỢC KẾT THÚC TASK UI hoặc Automation nếu chưa dùng **Puppeteer** (hoặc Playwright) để chụp ảnh màn hình và tự kiểm định kết quả.
- **Mục đích**: Đảm bảo các bước login và lấy dữ liệu GNOC thực sự hoạt động như mong đợi.

### 3. Tự động hóa hoàn toàn
- **Luật**: MỌI THAO TÁC DATA/CLOUD/GIT đều phải chạy tự động qua AI/MCP, tuyệt đối không bắt người dùng phải tự gõ các câu lệnh phức tạp.
- **Luật bổ sung**: Phải tuân thủ tuyệt đối quy trình trong [AI_PROTOCOL_GNOC.md](file:///Users/sonnbhp/Library/CloudStorage/GoogleDrive-sonnbhp@gmail.com/My%20Drive/Cyber/JWT/AI_PROTOCOL_GNOC.md) và tham khảo [automation_notes.md](file:///Users/sonnbhp/Library/CloudStorage/GoogleDrive-sonnbhp@gmail.com/My%20Drive/Cyber/JWT/automation_notes.md) khi gặp lỗi mạng.
- **Mục đích**: Đạt được mục tiêu "Quản lý rảnh tay" và đảm bảo tính ổn định lâu dài.
