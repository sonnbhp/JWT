# Hệ thống AI Agents & Tools

## Session Protocol
**Mandatory First Step — Không thể bỏ qua:**
Khi bắt đầu bất kỳ phiên làm việc mới nào, AI PHẢI:
1. Đọc `.claude/knowledge/knowledge-index.md` để lấy danh sách KI.
2. Nếu task hiện tại liên quan đến bất kỳ tag nào trong index, đọc nội dung KI đó TRƯỚC khi viết code.
3. Nêu rõ trong câu trả lời đầu tiên: "Đã kiểm tra KI — [tên KI liên quan hoặc 'Không có KI liên quan']".

### 👥 Hệ thống Sub-Agents Chuyên biệt

| Định danh | Vai trò chính | Kỹ năng trọng tâm |
| :--- | :--- | :--- |
| **@A-Manager** | Orchestrator (Điều phối) | Lập kế hoạch, Giao việc, Quản lý KI. |
| **@A-Core** | Logic & Hiệu suất | Python Pro, Clean Code, Xử lý API GNOC. |
| **@A-UX** | Trải nghiệm Báo cáo | UI/UX Báo cáo, Định dạng bảng, Emoji, Tagging. |
| **@A-Test** | Kiểm thử & Xác minh | Debugging, LeanKG (Phân tích rủi ro), Puppeteer (Xác minh hình ảnh). |

### 🛠 MCP Tools Menu

| Tên MCP/Tool | Có gì trong tay | Khi nào cần dùng |
| :--- | :--- | :--- |
| **Puppeteer (dev-tools)** | Hệ thống duyệt web ảo có khả năng tương tác (click, type), chụp ảnh màn hình. | Bắt buộc dùng để kiểm tra giao diện, chụp ảnh kết quả automation hoặc debug các trang web nội bộ như GNOC. |
| **LeanKG** | Hệ thống phân tích đồ thị kiến thức để hiểu sự liên quan giữa các khối logic. | Bắt buộc dùng để quét "Blast Radius" (vùng ảnh hưởng) trước khi thay đổi các logic cốt lõi trong pipeline báo cáo. |
