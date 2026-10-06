# Data Model
Kiến trúc Dữ liệu V4 chia tách rõ vòng đời:
1. `fields`: Quản lý thửa ruộng, crop age.
2. `images`: Quản lý file ảnh, metadata GPS.
3. `ai_jobs`: Quản lý tiến trình xử lý YOLO.
4. `ai_analysis` & `disease_detections`: Kết quả box bệnh AI.
5. `inspections`: Tổng hợp 1 lượt khảo sát (Map marker map vào đây).
6. `alerts`, `insights`, `reminders`, `ai_feedback`: Hệ sinh thái tương tác thông minh.
