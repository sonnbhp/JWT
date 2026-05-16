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

### 4. Định danh Sub-Agent & Tài liệu
- **Luật**: Khi một sub-agent được gọi (Core, UX, Test...), câu trả lời luôn phải bắt đầu bằng tên định danh (Ví dụ: `[@A-Core]`, `[@A-UX]`, `[@A-Test]`).
- **Luật**: Nếu có bất kỳ thay đổi nào tác động đến kiến trúc hệ thống, Agent bắt buộc phải cập nhật đồng thời file `ARCHITECTURE.md` và file `README.md`.
- **Mục đích**: Tăng tính minh bạch và đảm bảo tài liệu luôn đồng bộ với mã nguồn.

### 5. Nghiệm thu & Nhật ký Phối hợp
- **Mệnh lệnh Sắt**: Mọi thay đổi chỉ được phép áp dụng chính thức nếu được **@A-Test** đánh giá là **PASS**. Nếu FAIL, phải Rollback về trạng thái ổn định gần nhất.
- **Mệnh lệnh Sắt**: **@A-Manager** phải lưu trữ bằng chứng phối hợp thành file nhật ký hội thoại tại `.claude/skills/agents/A-manager/logs/` để người dùng hậu kiểm.
