# CAY LÚA -- MASTER IMPLEMENTATION PLAN

## Supabase + YOLO Server + HTML V3 + AI Adapter + API Fallback + Map + History + Alerts

**Phiên bản:** 1.0\
**Chế độ:** PLAN → EXECUTE → TEST → FIX → VERIFY

## 0. MỆNH LỆNH TỔNG QUÁT

BẠN LÀ LEAD SOFTWARE ARCHITECT + SENIOR FULL-STACK ENGINEER CỦA DỰ ÁN
CAY LÚA.

NHIỆM VỤ:

> Đọc project hiện tại → Audit → Lập kế hoạch → Tự động triển khai →
> Test → Phát hiện lỗi → Sửa → Test lại → Tích hợp hoàn chỉnh.

**Không được chỉ trả về kế hoạch rồi dừng.**

Sau khi hoàn thành PHASE 0 và tạo kế hoạch triển khai hợp lệ, phải **tự
động chuyển sang PHASE 1 và tiếp tục thực hiện**.

Chỉ được dừng khi: 1. đã triển khai xong; hoặc 2. gặp blocker thực sự
cần secret/thông tin mà Agent không thể tự lấy.

Nếu gặp blocker: hoàn thành tối đa phần có thể làm, không phá code đang
hoạt động, ghi chính xác biến/config còn thiếu.

------------------------------------------------------------------------

# 1. TÀI LIỆU NGUỒN BẮT BUỘC

Trước khi sửa code phải đọc:

``` text
CAY_LUA_MD_AI_ADAPTER_LINH_HOAT.md
project_tree.txt
AI_RICE_01_SERVER.txt
AI_RICE_02_GUI.txt
AI_RICE_03_STORAGE.txt
AI_RICE_04_TEST.txt
AI_RICE_05_CONFIG.txt
```

Đồng thời đọc toàn bộ source thực tế: HTML, JavaScript, CSS, server,
model loader, storage, history, auth, config, test và start scripts.

**Code thực tế là nguồn để xác định trạng thái hiện tại.**

Nếu tài liệu và code mâu thuẫn:

``` text
CONFLICT FOUND
```

Ghi nhận mâu thuẫn, chọn phương án ít phá vỡ hệ thống hiện tại và ghi
lại quyết định.

Không tự tạo kiến trúc mới nếu project đã có thành phần tương ứng.

------------------------------------------------------------------------

# 2. MỤC TIÊU KIẾN TRÚC

``` text
                         CAY LÚA WEB
                         HTML / V3
                              │
                              ▼
                         AI ADAPTER
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
         YOLO SERVER      API FALLBACK      LOCAL AI
          CAY LÚA          Pl@ntNet          nếu có
              │               │               │
              └───────────────┼───────────────┘
                              ▼
                         NORMALIZER
                              │
                              ▼
                           SUPABASE
                    ┌─────────┼─────────┐
                    ▼         ▼         ▼
                  Images     Jobs      Results
                    │         │         │
                    └─────────┼─────────┘
                              ▼
                       WEB / MAP / HISTORY
                       / ALERTS / RESULTS
```

Nguyên tắc: - HTML không phụ thuộc cứng vào YOLO server. - YOLO server
không phụ thuộc cứng vào HTML. - Supabase là nguồn dữ liệu trung tâm. -
AI provider có thể thay đổi. - Kết quả AI luôn được normalize. - Một
provider lỗi không được làm sập ứng dụng. - Một lỗi không được làm mất
ảnh/tọa độ/dữ liệu ruộng. - UI không bị khóa trong lúc AI chạy.

------------------------------------------------------------------------

# 3. PHASE 0 -- AUDIT PROJECT

**Không sửa code ở bước đầu.**

Xác định: 1. entry point HTML; 2. entry point server; 3. model path; 4.
model version; 5. API hiện tại; 6. storage hiện tại; 7. history hiện
tại; 8. authentication hiện tại; 9. config hiện tại; 10. test hiện tại;
11. cách khởi động project; 12. file đang được sử dụng thật; 13. file cũ
không còn dùng.

Tạo:

``` text
docs/PROJECT_AUDIT.md
```

Sau audit **tự động chuyển PHASE 1**.

------------------------------------------------------------------------

# 4. PHASE 1 -- TARGET ARCHITECTURE

Tạo:

``` text
docs/ARCHITECTURE_PLAN.md
```

Mô tả:

``` text
HTML
 ↓
AI Adapter
 ↓
Health Check
 ↓
YOLO Server?
 ├─ YES → YOLO
 └─ NO → API fallback
              ↓
           Local nếu có
              ↓
        Pending nếu không có AI
 ↓
Normalizer
 ↓
Supabase
 ↓
Map / History / Alerts
```

Phải có sequence diagram cho: - phân tích ảnh; - fallback; - lưu ảnh; -
lưu AI job; - lưu kết quả; - map; - history; - alert; - retry; - offline
sync.

Sau đó **tự động PHASE 2**.

------------------------------------------------------------------------

# 5. PHASE 2 -- SUPABASE

Tạo:

``` text
docs/SUPABASE_SCHEMA.md
supabase/migrations/
```

Không tạo bảng trùng nếu project đã có.

Schema tối thiểu:

## profiles

``` text
id
user_id
name
role
created_at
updated_at
```

## fields

``` text
id
user_id
name
latitude
longitude
polygon
area
rice_variety
sowing_date
growth_stage
notes
created_at
updated_at
```

## images

``` text
id
user_id
field_id
storage_path
original_filename
mime_type
file_size
latitude
longitude
captured_at
created_at
```

## ai_jobs

``` text
id
user_id
image_id
provider
status
request_id
started_at
finished_at
error_code
error_message
retry_count
created_at
updated_at
```

Status chuẩn:

``` text
QUEUED
PROCESSING
COMPLETED
FAILED
CANCELLED
PENDING_FALLBACK
PENDING_SYNC
```

## ai_analysis

``` text
id
job_id
provider
model_name
model_version
status
top_disease
top_confidence
processing_ms
raw_result
created_at
```

## disease_detections

``` text
id
analysis_id
class_id
disease_name
confidence
x1
y1
x2
y2
severity
created_at
```

## field_observations

``` text
id
field_id
image_id
analysis_id
latitude
longitude
sowing_date
age_days
growth_stage
leaf_green_pct
leaf_yellow_pct
leaf_brown_pct
notes
created_at
```

## alerts

``` text
id
user_id
field_id
observation_id
alert_type
severity
title
message
status
dedupe_key
created_at
read_at
```

------------------------------------------------------------------------

# 6. SUPABASE STORAGE

Bucket:

``` text
rice-images
```

Path:

``` text
rice-images/{user_id}/{field_id}/{yyyy}/{mm}/{dd}/original/
rice-images/{user_id}/{field_id}/{yyyy}/{mm}/{dd}/annotated/
```

Tên file dùng UUID/job_id.

Không lưu binary ảnh trong database.

------------------------------------------------------------------------

# 7. RLS / SECURITY

Bắt buộc: - RLS cho dữ liệu user-owned. - User chỉ đọc/sửa dữ liệu của
mình. - Không để service_role key trong HTML. - Không hard-code
password. - Không log API key. - Không log service_role key.

------------------------------------------------------------------------

# 8. PHASE 3 -- AI ADAPTER

Nếu project đã có adapter/provider tương đương thì tái sử dụng.

Frontend chỉ gọi:

``` javascript
AI.analyze(image, context)
```

Không rải:

``` javascript
fetch('/analyze_mobile')
```

ở nhiều nơi.

Provider:

``` text
caylua-yolov8
plantnet
local
```

Contract:

``` javascript
{
    name,
    healthCheck(),
    analyze(image, context)
}
```

------------------------------------------------------------------------

# 9. AUTO ROUTER

Mặc định:

``` text
AI_MODE = AUTO
```

Luồng:

``` text
AUTO
 ↓
YOLO health check
 ↓
Có?
 ├─ YES → YOLO
 └─ NO
      ↓
   Pl@ntNet
      ↓
   Có?
    ├─ YES → API
    └─ NO
         ↓
       LOCAL
         ↓
       Không có
         ↓
      PENDING_AI
```

Không retry vô hạn.

------------------------------------------------------------------------

# 10. YOLO SERVER CONTRACT

Phải có:

``` text
GET /health
POST /analyze_mobile
```

Health:

``` json
{
  "status": "ok",
  "service": "caylua-ai",
  "model": "best.pt",
  "model_version": "v1",
  "ready": true
}
```

Analyze input tối thiểu:

``` text
file
latitude
longitude
location_source
field_id
job_id
sowing_date
crop_variety
```

Không tạo API thứ hai nếu endpoint hiện tại có thể mở rộng.

------------------------------------------------------------------------

# 11. NORMALIZED AI RESULT

``` json
{
  "status": "success",
  "provider": "caylua-yolov8",
  "model": "best.pt",
  "model_version": "v1",
  "job_id": "uuid",
  "diseases": [
    {
      "class_id": 6,
      "name": "Đạo ôn",
      "confidence": 0.91,
      "bbox": [100,120,300,400]
    }
  ],
  "processing_ms": 850,
  "preview_url": null,
  "message": ""
}
```

API ngoài phải normalize về format này.

------------------------------------------------------------------------

# 12. PL@NTNET

Dùng Pl@ntNet như fallback hoặc cross-check.

Trước khi sử dụng disease API phải kiểm tra:

``` text
GET /v2/diseases
```

Endpoint:

``` text
POST /v2/diseases/identify
```

Gói Free hiện được Pl@ntNet công bố là 500 identification/ngày.

Không giả định API nhận tất cả bệnh lúa.

------------------------------------------------------------------------

# 13. API KEY

Không hard-code secret trong frontend triển khai công khai.

Ưu tiên:

``` text
HTML
 ↓
CAY LÚA backend/proxy
 ↓
Pl@ntNet
```

Nếu demo local dùng client-side API key theo cơ chế provider cho phép,
phải ghi rõ đây là demo.

------------------------------------------------------------------------

# 14. PHASE 4 -- HTML V3

Giữ giao diện V3: - sidebar; - map; - search; - tabs; - history; -
knowledge; - camera; - upload; - modal.

Chỉ bổ sung: - AI status; - provider status; - alerts; - field
profile; - health result; - history integration.

------------------------------------------------------------------------

# 15. MAP FLOW

Click bất kỳ vị trí:

``` text
Map
 ↓
Marker
 ↓
Popup
```

Popup:

``` text
📍 Vị trí ruộng

Lat: 10.xxxxxx
Lng: 105.xxxxxx

[📁 Up ảnh]
[📷 Chụp ảnh]
```

Marker draggable.

Kéo marker chỉ cập nhật tọa độ, không tạo observation mới.

------------------------------------------------------------------------

# 16. IMAGE FLOW

``` text
Upload
 ↓
Preview
 ↓
Create ai_job
 ↓
AI Adapter
 ↓
YOLO/API
 ↓
Normalize
 ↓
Save result
 ↓
Update UI
```

Chống double-click.

Một ảnh + một action = một job_id.

------------------------------------------------------------------------

# 17. STATE MACHINE

Dùng state machine trung tâm:

``` text
IDLE
SELECTING_LOCATION
IMAGE_SELECTED
QUEUED
ANALYZING
AI_FALLBACK
SAVING
COMPLETED
FAILED
PENDING_SYNC
```

Không tạo quá nhiều boolean độc lập gây trạng thái mâu thuẫn.

------------------------------------------------------------------------

# 18. CHỐNG NGHẼN UI

Bắt buộc: - Không block main thread. - Không reload trang. - Không khóa
toàn bộ UI. - Disable đúng nút đang chạy. - Timeout. - AbortController
nếu phù hợp. - Retry giới hạn. - Exponential backoff. - Debounce
search. - Debounce map events. - Không gọi Supabase liên tục trong
render. - Không upload một ảnh nhiều lần. - Không chạy hai AI request
giống nhau cho cùng job.

------------------------------------------------------------------------

# 19. CẢNH BÁO

Không dùng `alert()` liên tục.

Có: 1. Toast; 2. Alert Center; 3. Chi tiết lịch sử.

Ví dụ:

``` text
⚠️ AI server offline
Đang chuyển sang AI dự phòng...
```

``` text
⚠️ AI dự phòng không khả dụng.
Ảnh vẫn được lưu.
```

``` text
⚠️ Kết quả chưa chắc chắn.
Nên chụp lại ảnh rõ hơn.
```

------------------------------------------------------------------------

# 20. ERROR MATRIX

Chuẩn hóa:

``` text
AI_SERVER_OFFLINE
AI_TIMEOUT
AI_PROVIDER_ERROR
AI_LOW_CONFIDENCE
AI_NO_DETECTION
API_QUOTA_EXCEEDED
API_UNAVAILABLE
UPLOAD_FAILED
STORAGE_FAILED
DATABASE_FAILED
SYNC_FAILED
INVALID_LOCATION
INVALID_IMAGE
DUPLICATE_JOB
```

Mỗi lỗi có:

``` text
code
user_message
technical_message
retryable
provider
```

------------------------------------------------------------------------

# 21. FALLBACK

YOLO lỗi:

``` text
YOLO ERROR
 ↓
Toast
 ↓
Pl@ntNet
```

API lỗi:

``` text
API ERROR
 ↓
Local model nếu có
```

Tất cả AI lỗi:

``` text
Lưu ảnh
 ↓
PENDING_AI
```

Không mất dữ liệu.

------------------------------------------------------------------------

# 22. SUPABASE ERROR

Nếu storage/database lỗi: - không xóa local data; - chuyển
PENDING_SYNC; - retry 1s → 2s → 4s; - sau giới hạn: SYNC_FAILED; - không
retry vô hạn.

------------------------------------------------------------------------

# 23. OFFLINE

Khi mất Internet lưu local:

``` text
image
GPS
timestamp
field_id
metadata
```

Status:

``` text
PENDING_SYNC
```

Khi có mạng:

``` text
Sync queue
 ↓
Storage
 ↓
Database
 ↓
AI
```

Phải có idempotency.

------------------------------------------------------------------------

# 24. MÀU LÁ

Không phụ thuộc API.

Nếu có OpenCV:

``` text
Ảnh
 ↓
Leaf segmentation
 ↓
HSV/Lab
 ↓
Green %
Yellow %
Brown %
```

Nếu chưa có module:

``` text
leaf_color_status = "not_available"
```

Không tự tạo số liệu giả.

------------------------------------------------------------------------

# 25. TUỔI LÚA

``` text
age_days = today - sowing_date
```

Không có ngày gieo/cấy:

``` text
age_days = null
```

Không đoán tuổi chỉ từ ảnh.

------------------------------------------------------------------------

# 26. PHIẾU SỨC KHỎE

``` text
🌾 PHIẾU SỨC KHỎE LÚA

🦠 Bệnh: Đạo ôn
🎯 Confidence: 91%
🤖 Nguồn: CAY LÚA YOLOv8

🌿 Màu lá
🟢 Xanh: 72%
🟡 Vàng: 21%
🟤 Nâu: 7%

🌱 Tuổi lúa: 35 ngày

📍 Vị trí:
10.xxxxxx, 105.xxxxxx
```

------------------------------------------------------------------------

# 27. HAI AI KHÁC NHAU

Không cộng confidence.

Nếu:

``` text
YOLO: Đạo ôn – 76%
API: Đốm nâu – 71%
```

Hiển thị:

``` text
⚠️ AI chưa thống nhất.
Nên chụp lại ảnh hoặc kiểm tra chuyên gia.
```

------------------------------------------------------------------------

# 28. HISTORY

History lấy từ Supabase.

Filter: - ruộng; - ngày; - bệnh; - provider; - mức độ.

Pagination khi dữ liệu lớn.

------------------------------------------------------------------------

# 29. MAP DATA

Không load toàn bộ history vô hạn.

Ưu tiên: - viewport/bounds; - pagination; - filter.

Marker:

``` text
🟢 bình thường
🟡 nghi ngờ
🟠 trung bình
🔴 cao
```

------------------------------------------------------------------------

# 30. DASHBOARD

Hiển thị:

``` text
Tổng ruộng
Tổng lượt kiểm tra
Bệnh gần đây
Cảnh báo
AI status
Server status
API status
```

Không polling quá nhanh.

------------------------------------------------------------------------

# 31. OBSERVABILITY

Log:

``` text
request_id
job_id
provider
field_id
status
duration
error_code
```

Không log secret.

------------------------------------------------------------------------

# 32. MIGRATION

Mọi thay đổi DB qua:

``` text
supabase/migrations/
```

Ví dụ nếu chưa có migration tương đương:

``` text
001_initial_schema.sql
002_ai_jobs.sql
003_ai_analysis.sql
004_disease_detections.sql
005_field_observations.sql
006_alerts.sql
007_rls.sql
008_storage.sql
```

Phải tiếp tục từ migration hiện có, không đánh số trùng.

------------------------------------------------------------------------

# 33. TEST PLAN

Bắt buộc:

``` text
A  Server OFF + API ON
B  Server ON + API ON
C  Server OFF + API OFF
D  Server timeout
E  API timeout
F  API 429
G  Supabase lỗi
H  Double-click Analyze
I  Upload liên tục
J  Click map nhiều lần
K  Confidence thấp
L  Hai AI khác nhau
M  Offline → Online
N  Retry
O  Duplicate job
P  RLS
```

------------------------------------------------------------------------

# 34. INTEGRATION TEST

Bắt buộc chạy:

``` text
OPEN WEB
 ↓
CLICK MAP
 ↓
POPUP
 ↓
UPLOAD
 ↓
CREATE JOB
 ↓
CHECK YOLO
 ↓
FALLBACK IF NEEDED
 ↓
AI RESULT
 ↓
SAVE SUPABASE
 ↓
MARKER
 ↓
HISTORY
 ↓
ALERT
```

Lặp với: - YOLO ON/OFF; - API ON/OFF; - network ON/OFF; - Supabase lỗi.

------------------------------------------------------------------------

# 35. PLAN → EXECUTE

**ĐÂY LÀ QUY TẮC QUAN TRỌNG NHẤT.**

Sau PHASE 0: 1. Audit. 2. Tạo kế hoạch. 3. **Không hỏi xác nhận.** 4.
**Tự động bắt đầu triển khai.**

Cấm trả lời:

> "Đây là kế hoạch, bạn có muốn tôi tiếp tục không?"

Phải tiếp tục ngay.

------------------------------------------------------------------------

# 36. EXECUTION LOOP

``` text
PLAN
 ↓
IMPLEMENT
 ↓
RUN
 ↓
TEST
 ↓
ERROR?
 ├─ NO → NEXT PHASE
 └─ YES
      ↓
   DIAGNOSE
      ↓
      FIX
      ↓
      TEST
      ↓
   PASS?
    ├─ NO → FIX tiếp
    └─ YES → NEXT PHASE
```

Không dừng chỉ vì gặp lỗi đầu tiên.

------------------------------------------------------------------------

# 37. SAU MỖI PHASE

Ghi:

``` text
PHASE X
Status: PASS / PARTIAL / BLOCKED

Files changed:
...

Tests:
...

Errors fixed:
...

Remaining:
...
```

Nếu PASS:

``` text
→ tự động sang phase tiếp theo.
```

------------------------------------------------------------------------

# 38. KHÔNG PHÁ CODE

Trước file quan trọng: - git status; - git diff; - checkpoint/backup nếu
phù hợp.

Không xóa file cũ nếu chưa xác định nó không được dùng.

Không tạo hệ thống trùng: - history; - storage; - auth; - API; - model
loader; - config.

------------------------------------------------------------------------

# 39. SOURCE OF TRUTH

``` text
SUPABASE = SOURCE OF TRUTH
```

Local chỉ là:

``` text
cache
offline queue
temporary state
```

Không để localStorage, JSON server và Supabase cùng trở thành ba nguồn
dữ liệu chính.

------------------------------------------------------------------------

# 40. JOB IDEMPOTENCY

Mỗi job:

``` text
job_id = UUID
```

Request gửi lại cùng job_id phải: - trả kết quả cũ; hoặc - tiếp tục job
cũ.

Không tạo duplicate.

------------------------------------------------------------------------

# 41. JOB TIMEOUT

Nếu YOLO không trả:

``` text
PROCESSING
 ↓ timeout
FAILED
 ↓
fallback
```

Không để job treo vô hạn ở PROCESSING.

------------------------------------------------------------------------

# 42. UI NON-BLOCKING

Trong khi AI chạy: - Map vẫn zoom được. - Sidebar vẫn mở. - History vẫn
xem được. - Chỉ action hiện tại bị khóa.

------------------------------------------------------------------------

# 43. OUTPUT CUỐI

Sau khi tự động triển khai xong tạo:

``` text
docs/IMPLEMENTATION_REPORT.md
```

Báo cáo: 1. Những gì đã xây. 2. Files tạo. 3. Files sửa. 4. Supabase
migrations. 5. API contracts. 6. AI providers. 7. Fallback. 8. Error
handling. 9. Tests. 10. Test results. 11. Lỗi đã sửa. 12. Phần chưa hoàn
thành. 13. Cách chạy project. 14. Cách bật YOLO. 15. Cách cấu hình
Supabase. 16. Cách cấu hình API. 17. Cách rollback.

------------------------------------------------------------------------

# 44. DEFINITION OF DONE

Chỉ được báo hoàn thành khi:

``` text
1. Mở HTML
2. Server OFF
3. Click map
4. Popup hiện
5. Upload ảnh
6. AI Adapter nhận ảnh
7. YOLO OFF được phát hiện
8. Fallback API
9. Kết quả hiển thị
10. Ảnh lưu
11. Tọa độ lưu
12. Observation lưu
13. Marker cập nhật
14. History cập nhật
15. Tắt API
16. Bật YOLO
17. Reload
18. YOLO được ưu tiên
19. Kết quả YOLO lưu
20. Không duplicate
21. YOLO timeout
22. Fallback hoạt động
23. Supabase lỗi
24. Pending sync
25. Network trở lại
26. Sync thành công
27. Không mất ảnh
28. Không mất tọa độ
29. Không lộ secret
30. Không request loop
31. Không UI freeze
32. Không lỗi JS nghiêm trọng
```

------------------------------------------------------------------------

# 45. BLOCKER POLICY

Chỉ được dừng nếu thiếu thứ Agent không thể tự tạo/lấy, ví dụ:

``` text
SUPABASE_URL
SUPABASE_ANON_KEY
PLANTNET_API_KEY
```

Nếu thiếu: - tạo `.env.example`; - tạo code/config placeholder; - hoàn
thành tất cả phần không phụ thuộc secret; - test mock; - ghi BLOCKED
chính xác; - không phá project.

Khi có secret, tiếp tục từ phase đang dở.

------------------------------------------------------------------------

# 46. LỆNH KHỞI ĐỘNG

BẮT ĐẦU NGAY:

``` text
PHASE 0 – AUDIT CAY LÚA
```

Sau đó tự động:

``` text
PHASE 1 – ARCHITECTURE
PHASE 2 – SUPABASE
PHASE 3 – AI ADAPTER
PHASE 4 – YOLO SERVER
PHASE 5 – HTML V3
PHASE 6 – MAP/HISTORY
PHASE 7 – ALERT/ERROR
PHASE 8 – OFFLINE/SYNC
PHASE 9 – TEST
PHASE 10 – INTEGRATION VERIFY
```

**KHÔNG HỎI XÁC NHẬN GIỮA CÁC PHASE.**

Chỉ dừng khi:

``` text
DONE
```

hoặc:

``` text
BLOCKED – cần secret/thông tin không thể tự lấy
```

------------------------------------------------------------------------

# 47. KIẾN TRÚC CUỐI CÙNG

``` text
                    🌾 CAY LÚA
                        │
              ┌─────────┴─────────┐
              │                   │
          WEB V3              SUPABASE
              │                   │
          AI Adapter          DATA CORE
              │                   │
       ┌──────┼──────┐            │
       ▼      ▼      ▼            │
     YOLO    API   LOCAL           │
       │      │      │             │
       └──────┼──────┘             │
              ▼                    │
          NORMALIZER               │
              │                    │
              └────────┬───────────┘
                       ▼
              MAP / HISTORY / ALERT
                       │
                       ▼
                 👨‍🌾 NHÀ NÔNG
```

**Nguyên tắc cuối:**

> Kế hoạch không phải là sản phẩm cuối.\
> Kế hoạch là lệnh triển khai.\
> Sau khi lập kế hoạch, Agent phải tự động thực hiện, kiểm thử, sửa lỗi
> và xác minh toàn bộ hệ thống.
