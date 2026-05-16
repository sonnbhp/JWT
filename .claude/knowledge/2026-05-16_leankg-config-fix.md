# 🛠 Sửa lỗi tham số '.' trong LeanKG MCP config

## Vấn đề
Khi cấu hình LeanKG MCP server trong `mcp_config.json`, việc thêm tham số `.` vào sau `mcp-stdio` gây ra lỗi:
`leankg: error: unexpected argument '.' found`

Điều này khiến server không thể khởi tạo (`calling "initialize": EOF`).

## Giải pháp
1. Xóa tham số `.` khỏi mảng `args` trong `mcp_config.json`.
2. Đảm bảo project đã được khởi tạo bằng `leankg init`.
3. Đảm bảo project đã được index bằng `leankg index`.

## Cấu hình đúng
```json
"leankg": {
  "command": "/Users/sonnbhp/.local/bin/leankg",
  "args": ["mcp-stdio", "--watch"],
  "env": {
    "LEANKG_API_KEY": "..."
  }
}
```
