# MAP AUDIT BEFORE FIX

## 1. Lỗi phát hiện
- **Lỗi lớn nhất:** File `index.html` chứa lỗi cú pháp JavaScript nghiêm trọng. Ở dòng 694 (phần thông báo offline của hàm `testServer`), chuỗi ký tự bị tách dòng (`alert("❌ Server Offline hoặc không thể kết nối: " + e.message + " \n\n Hãy chắc chắn server đã được bật và đúng địa chỉ.");`) mà không sử dụng template literal (dấu backtick ``` `` ```) hoặc ký tự ngắt dòng `\n`.
- **Hệ quả:** Lỗi `SyntaxError: Invalid or unexpected token` đã làm cho toàn bộ file inline script không thể biên dịch và thực thi. Toàn bộ logic khởi tạo bản đồ `L.map('map')`, gán biến `map`, `data` cũng như các hàm cốt lõi đều không được định nghĩa.
- **Biểu hiện UI:** Giao diện trắng bản đồ hoặc không hiển thị bất kỳ marker/list nào, người dùng báo "bản đồ không hoạt động".

## 2. Các module bị ảnh hưởng
- **Leaflet Map Initialization:** Không chạy, `div#map` trắng.
- **Dữ liệu Mock / Supabase:** Các mảng `window.data`, `window.ms` không được cấp phát, kéo theo các module ngoại vi như `map_centric.js` cũng fail vì không tìm thấy `window.data`.
- **Toàn bộ App V3:** Không thể hoạt động.

## 3. Mức độ nghiêm trọng
- **Blocker (CRITICAL):** Lỗi Syntax làm sập toàn bộ JavaScript engine của trình duyệt cho thẻ `<script>` tương ứng.

## 4. Cách sửa dự kiến
- Viết script Python/NodeJS để phân tích chuỗi lỗi và thay thế bằng template literal ES6 (`alert(\`...\`)`).
- Chạy lại kiểm tra cú pháp toàn bộ file `index.html` và các file `.js`.
- Bật lại Web server để load map.
