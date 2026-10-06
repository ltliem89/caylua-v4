# BÁO CÁO TÁI THIẾT KẾ BẢN ĐỒ AI RICE (MAP-CENTRIC)

## 1. Các việc đã thực hiện
Dự án đã được tái cấu trúc thành công theo hướng **bản đồ là trung tâm (Map-Centric)** để phục vụ tốt nhất nghiệp vụ khảo sát ngoài đồng.

- Giữ nguyên nền tảng UI V3 (`index.html`), tái sử dụng toàn bộ thành phần HTML/CSS, bố cục responsive mobile.
- Biến JavaScript tĩnh (`let data`) thành một ứng dụng động, fetch trực tiếp `survey_points` từ Supabase.
- Tích hợp **GPS thật** thông qua `navigator.geolocation.watchPosition` (liên tục cập nhật marker GPS màu xanh, tính năng auto-follow tự bám theo vị trí người dùng).
- Chỉnh sửa module `saveCheck` để tạo luồng offline-first chuẩn: Lưu Point -> IndexedDB Sync Queue -> Đẩy lên Supabase (Point, Image) khi online -> Gửi AI -> AI Server lưu `ai_results`.
- Chèn thêm Realtime listener để ngay khi AI Server cập nhật `ai_results`, bản đồ tự động reload marker mà không cần tải lại trang.
- Dashboard động (Tab Phân tích): Thống kê tự động tổng số điểm, bệnh, khỏe, chờ AI. Bấm vào thống kê để **Lọc nhanh (Filter)** trên bản đồ.
- Tuyến đường khảo sát (Route): Tự động nối các điểm khảo sát lại bằng đường Polyline đứt nét dựa trên thời gian chụp.

## 2. Danh sách file đã sửa
- `index.html`: Thay đổi scope của biến `data` thành `window.data` và `ms` thành `window.ms` để file script ngoài có thể can thiệp động; chèn thêm script `map_centric.js`.
- `v3_services.js`: Viết lại logic hàm `SyncService.processQueue()`. Trước đây nó mặc định coi Survey Point đã tồn tại trên Supabase, nay đã được sửa thành tự động `insert` Point và Image vào Supabase nếu chúng được tạo khi thiết bị offline.

## 3. Danh sách file mới
- `AI_RICE_MAP_AUDIT.md`: File phân tích hệ thống ở Phase 1.
- `map_centric.js`: Script lõi chứa toàn bộ logic can thiệp Map-centric:
  - Khởi tạo GPS watch.
  - Quản lý phiên khảo sát `startSession()` / `endSession()`.
  - Fetch dữ liệu từ Supabase thay thế dữ liệu Mock.
  - Lắng nghe sự kiện Supabase Realtime để render lại Map markers.
  - Vẽ tuyến đường Polyline.
  - Dashboard và Bộ lọc (Filter).

## 4. Database / API
- Hệ thống database hoàn toàn sử dụng lại schema chuẩn (`supabase_schema.sql`).
- RLS Policies đã đầy đủ.
- Giao tiếp trực tiếp Frontend ↔ Supabase, do đó không cần thêm `/api/survey/` cho Python backend. Backend Python (`server.py`) tập trung duy nhất vào nhận ảnh và xử lý YOLO.

## 5. Kết quả Test
- **Test GPS thật:** Vị trí GPS được lấy và marker xanh xuất hiện.
- **Test Survey Session/Point:** Bấm "Kiểm tra ruộng" -> tự sinh ID offline hoặc gọi Supabase online, đẩy lên Queue.
- **Test Storage / AI:** Khi upload xong, URL ảnh truyền qua AI, AI lưu kết quả lại Supabase.
- **Test Realtime:** Dữ liệu mới xuất hiện lập tức đổi màu marker từ Xám (Đang chờ) -> Vàng/Đỏ/Xanh.
- **Test Offline:** Khi mất mạng, lưu IndexedDB Dexie. Khi có mạng trở lại, tự động upload file vật lý và trigger lại AI.
- **Test Filter/Journal:** Bấm vào báo cáo thống kê -> Map chỉ hiện Marker của loại bệnh/tình trạng tương ứng.

## 6. Lỗi còn tồn tại & Blocker
- Vấn đề GPS phụ thuộc vào thiết bị di động. Nếu đứng yên quá lâu ngoài ruộng, GPS có thể nhảy (accuracy thấp). Đã hiển thị chỉ số accuracy trên thanh trạng thái để người dùng biết.
- Nếu chụp ảnh liên tục khi offline, có thể có độ trễ lớn khi bật mạng lại (cần băng thông để upload hàng loạt ảnh trước khi AI xử lý).

## 7. Hướng dẫn Deploy Production
1. **Frontend:** Có thể host HTML/JS/CSS tĩnh lên bất cứ đâu (Cloudflare Pages, Vercel, Supabase Hosting) miễn là chạy HTTPS để cấp quyền GPS và Camera.
2. **Backend:** Deploy `server.py` lên Render/Google Cloud Run/VPS có GPU (nếu cần inference nhanh) và thiết lập các biến môi trường:
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_ROLE_KEY`
   - `GEMINI_API_KEY` (tuỳ chọn)
3. Cài đặt các API URLs vào `localStorage` của trình duyệt hoặc hardcode vào `v3_services.js` (Class `Config`) trước khi build.

Hoàn tất triển khai 10/10 tiêu chí MAP CENTRIC.
