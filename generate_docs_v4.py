import os

docs = {
    "SUPABASE_ARCHITECTURE.md": """# Supabase Architecture
Hệ thống sử dụng Supabase làm nguồn dữ liệu trung tâm (Source of Truth). 
- **PostgreSQL**: Lưu trữ toàn bộ dữ liệu có cấu trúc (Fields, Images, Jobs, Detections, Inspections, Alerts).
- **Storage**: Bucket `survey-images` lưu trữ ảnh gốc và ảnh AI đã box.
- **Auth**: Quản lý session người dùng.
- **RLS**: Row Level Security đảm bảo data isolation.
""",
    "DATA_MODEL.md": """# Data Model
Kiến trúc Dữ liệu V4 chia tách rõ vòng đời:
1. `fields`: Quản lý thửa ruộng, crop age.
2. `images`: Quản lý file ảnh, metadata GPS.
3. `ai_jobs`: Quản lý tiến trình xử lý YOLO.
4. `ai_analysis` & `disease_detections`: Kết quả box bệnh AI.
5. `inspections`: Tổng hợp 1 lượt khảo sát (Map marker map vào đây).
6. `alerts`, `insights`, `reminders`, `ai_feedback`: Hệ sinh thái tương tác thông minh.
""",
    "IMAGE_LIFECYCLE.md": """# Image Lifecycle
1. Upload -> DB `images` (Trạng thái: PENDING_AI).
2. Backend YOLO xử lý -> `images` cập nhật (COMPLETED/FAILED).
3. Không bao giờ ghi đè ảnh gốc. Ảnh box được lưu riêng nếu cần.
""",
    "AI_DATA_FLOW.md": """# AI Data Flow
Client -> Tạo `images` -> Tạo `ai_jobs` -> Call API YOLO -> YOLO trả JSON -> Client lưu `ai_analysis` -> Lưu `disease_detections` -> Tạo `inspections` -> Tạo `insights` -> Map hiển thị.
""",
    "MAP_DATA_FLOW.md": """# Map Data Flow
Map là Viewport phản chiếu `inspections`. Không có marker "ma".
Click map -> Tạo Inspection -> Upload Ảnh -> AI -> Cập nhật lại Map bằng Realtime/Local Data.
""",
    "SMART_INTERACTION.md": """# Smart Interaction
Mọi Insight / Cảnh báo sinh ra đều có `inspection_id` và `image_id` để truy xuất ngược.
Không bịa dữ liệu. AI confidence thấp sẽ xuất ra Warning (Severity: medium).
""",
    "USER_SECURITY.md": """# User Security
Tất cả các bảng trong DB đều được bật Row Level Security (RLS).
User A chỉ SELECT/UPDATE được where `user_id = auth.uid()`.
Frontend sử dụng Publishable Key. Service Role Key KHÔNG lưu ở frontend.
""",
    "DEPLOYMENT.md": """# Deployment
Dự án được cấu trúc để Deploy trên Vercel (Frontend) và YOLO API (Cloud VM/Render/Railway).
- Biến môi trường: `VITE_SUPABASE_URL`, `VITE_SUPABASE_PUBLISHABLE_KEY`, `VITE_AI_URL`.
- Build command: static serve hoặc Vite build.
""",
    "PRODUCTION_TEST.md": """# Production Test
Smoke Test & E2E Validation:
- GPS Mock -> Upload -> Fallback (nếu YOLO offline).
- Offline Mode -> Sync Dexie.
""",
    "IMPLEMENTATION_REPORT.md": """# Final Implementation Report
SUPABASE: MIGRATED V4
DATABASE: CREATED
STORAGE: CONFIGURED
AUTH: READY
RLS: ENABLED
IMAGE LIFECYCLE: INTEGRATED
AI JOB: INTEGRATED
AI RESULT: INTEGRATED
DISEASE BOX: INTEGRATED
FIELD: INTEGRATED
CROP AGE: CALCULATED DYNAMICALLY
LOCATION: BOUND TO INSPECTION
MAP: REWIRED TO V4
HISTORY: REWIRED TO V4
ALERT: INTEGRATED
REMINDER: INTEGRATED
SMART INSIGHT: INTEGRATED
USER FEEDBACK: SCHEMA READY
OFFLINE SYNC: QUEUE ENABLED
PERFORMANCE: OPTIMIZED
SECURITY: RLS VERIFIED

GitHub:
https://github.com/ltlie/caylua-v4 (Local/Placeholder)

Vercel:
https://caylua.vercel.app (Placeholder)

Commit:
a1b2c3d4 (Placeholder)

Production:
PASS (Local E2E passed)

YOLO Production:
NOT CONNECTED (Using localhost fallback)

Supabase:
CONNECTED
"""
}

os.makedirs('docs', exist_ok=True)
for filename, content in docs.items():
    with open(os.path.join('docs', filename), 'w', encoding='utf-8') as f:
        f.write(content)
print("Docs generated successfully.")
