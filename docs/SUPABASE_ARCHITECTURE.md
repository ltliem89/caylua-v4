# Supabase Architecture
Hệ thống sử dụng Supabase làm nguồn dữ liệu trung tâm (Source of Truth). 
- **PostgreSQL**: Lưu trữ toàn bộ dữ liệu có cấu trúc (Fields, Images, Jobs, Detections, Inspections, Alerts).
- **Storage**: Bucket `survey-images` lưu trữ ảnh gốc và ảnh AI đã box.
- **Auth**: Quản lý session người dùng.
- **RLS**: Row Level Security đảm bảo data isolation.
