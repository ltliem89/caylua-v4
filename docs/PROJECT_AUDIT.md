# PROJECT AUDIT

## 1. Hiện trạng Dự án
- **Frontend**: Ứng dụng HTML/JS/CSS tĩnh (V3), giao diện bản đồ (Leaflet) đóng vai trò trung tâm (Map-Centric). Các file chính gồm `index.html`, `map_centric.js`, `v3_services.js`.
- **Backend (AI)**: Server Python (FastAPI + YOLOv8) xử lý ảnh bệnh cây lúa.
- **Cơ sở dữ liệu**: Đang dùng Supabase làm nguồn dữ liệu chính. Có sẵn các bảng cơ bản như `survey_images`, `survey_points`, `ai_results`.
- **Lưu trữ ảnh**: Đang sử dụng Supabase Storage bucket `survey-images`.
- **Cơ chế hoạt động**:
  1. Người dùng quét ảnh tại ruộng.
  2. Dữ liệu tạm (nếu offline) được giữ qua IndexedDB (qua Dexie).
  3. Lên mạng, dữ liệu đẩy lên Supabase Storage và gọi Backend YOLO API xử lý.
  4. Backend xử lý xong đẩy ngược `ai_results` lên Supabase DB.
  5. Frontend nhận Realtime event và cập nhật Marker trên bản đồ.

## 2. Khoảng trống Kiến trúc (Kiểm định so với Lệnh Triển khai V4)
- **Thiếu vòng đời chuẩn của 1 Bức Ảnh**: Ảnh hiện tại chỉ gắn với `survey_points` và `ai_results`. Chưa có cơ chế Job (`ai_jobs`), tách biệt Analysis (`ai_analysis`) và Detections (`disease_detections`).
- **Thiếu Quản lý Tuổi lúa & Mùa vụ**: Bảng `fields` cũ chưa lưu `sowing_date` và `growth_stage`. `inspections` cần snapshot `crop_age_days`.
- **Thiếu Insight & Feedback**: Chưa có bảng lưu các "Phản hồi thông minh" (`insights`) và xác nhận từ người dùng hay chuyên gia (`ai_feedback`).
- **Data Access Layer**: Code frontend tuy đã tách ra `v3_services.js` nhưng vẫn gọi Supabase rải rác. Cần refactor để cô lập vào thư mục `src/data/`.
- **Chưa Deploy Production**: Toàn bộ hệ thống vẫn chạy ở localhost (backend localhost:8000, frontend HTTP-Server localhost:8080).

## 3. Lộ trình Triển khai End-to-End
1. **Migration DB**: Cập nhật Supabase Schema (Tạo mới và update bảng).
2. **Refactor Codebase**: Migrate các hàm API thành Data Access Object (DAO) pattern.
3. **Smart Interaction & Map Data Flow**: Sửa đổi map_centric.js để đọc từ data model mới.
4. **Vercel & GitHub Deploy**: Tổ chức lại code, tạo Vercel config. Hướng dẫn Public YOLO server.
5. **E2E Testing**: Khởi chạy smoke test và xác thực các case offline, fallback.
