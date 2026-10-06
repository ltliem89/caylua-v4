# AI RICE — MASTER COMMAND
# BẮT BUỘC CẢI TIẾN: V3 + SUPABASE + AI SERVER
# ỨNG DỤNG ĐIỆN THOẠI KHẢO SÁT BỆNH LÚA NGOÀI ĐỒNG

---

# 0. MỤC TIÊU DUY NHẤT

Cải tiến hệ thống thành ứng dụng mà người dùng có thể:

```text
Cầm điện thoại
↓
Mở https://ai.nongnghiepsangtao.io.vn/
↓
Đăng nhập
↓
Chọn ruộng
↓
Đi nhiều vị trí ngoài đồng
↓
GPS tự cập nhật
↓
Chụp/chọn ảnh lúa
↓
Tạo một điểm khảo sát
↓
Ảnh được tải lên Supabase Storage
↓
Metadata/GPS lưu Supabase Database
↓
Gửi ảnh cho AI Server
↓
YOLO phân tích
↓
Kết quả AI ghi về Supabase
↓
Supabase Realtime cập nhật V3
↓
Điểm khảo sát trên bản đồ được cập nhật
↓
Đi tiếp điểm khác
↓
Lưu toàn bộ thành lịch sử khảo sát
```

Đây KHÔNG phải hệ thống upload một ảnh đơn lẻ.

Đây là:

> **Ứng dụng khảo sát bệnh lúa nhiều điểm bằng điện thoại, trong đó mỗi ảnh được gắn với GPS và trở thành một điểm khảo sát trên bản đồ.**

---

# 1. KIẾN TRÚC BẮT BUỘC

Chốt kiến trúc:

```text
                    📱 ĐIỆN THOẠI
                           │
                           ▼
                       V3 WEB
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
          GPS + CAMERA              SUPABASE
                                        │
                         ┌──────────────┼──────────────┐
                         │              │              │
                         ▼              ▼              ▼
                     Database        Storage        Realtime
                         │              │              │
                         └──────────────┼──────────────┘
                                        │
                                        ▼
                                  AI SERVER
                                        │
                                      YOLO
                                        │
                                   AI RESULT
                                        │
                                        ▼
                                    SUPABASE
                                        │
                                    REALTIME
                                        │
                                        ▼
                                      V3
```

Vai trò:

### V3 Web
- giao diện điện thoại
- GPS
- camera
- chụp/chọn ảnh
- bản đồ
- khảo sát
- nhật ký
- hiển thị kết quả

### Supabase
**Nguồn dữ liệu chính của hệ thống.**

Bao gồm:
- Auth
- PostgreSQL Database
- Storage
- Realtime

### AI Server
**Bộ máy xử lý AI, không phải database nghiệp vụ chính.**

Bao gồm:
- FastAPI
- YOLO
- bbox
- confidence
- fusion/sensor nếu đang có
- AI processing
- ghi kết quả vào Supabase

---

# 2. KHÔNG ĐƯỢC VIẾT LẠI HỆ THỐNG

Trước khi sửa:

1. Đọc toàn bộ project.
2. Đọc V3.
3. Đọc server.py.
4. Đọc các module Auth/Storage/IoT.
5. Đọc cấu hình Supabase hiện tại nếu có.
6. Kiểm tra database/schema/bucket hiện tại.
7. Kiểm tra production domain.

Các file bắt buộc đọc:

```text
AI_Rice_UX_Prototype_V3_CLICK_POPUP_FINAL.html
server.py
auth_simple.py
storage_user.py
history_log.py
project_tree.txt
AI_RICE_01_SERVER.txt
AI_RICE_02_GUI.txt
AI_RICE_03_STORAGE.txt
AI_RICE_04_TEST.txt
AI_RICE_05_CONFIG.txt
Tóm tắt điều hành.docx
Đề tài lúa-thanh thiếu niên nhi đồng-v2.docx
Ban thuyết minh 2026.docx
```

Nếu có module IoT thì đọc cả:

```text
sensor_routes
sensor_service
device_routes
device_access_manager
image_analysis_service
plant_health_service
fusion_engine
environment_ai_service
```

**Không tạo bảng/API/module trùng với thứ đã có.**

---

# 3. PRODUCTION WEBSITE

Production chính thức:

```text
https://ai.nongnghiepsangtao.io.vn/
```

V3 phải được mở từ domain này.

Không để frontend production phụ thuộc:

```text
localhost
127.0.0.1
:8000
:5000
```

Ưu tiên relative URL:

```javascript
fetch("/api/...")
```

WebSocket:

```javascript
const protocol = location.protocol === "https:" ? "wss:" : "ws:";
const wsUrl = `${protocol}//${location.host}/ws`;
```

Production phải trở thành:

```text
wss://ai.nongnghiepsangtao.io.vn/ws
```

---

# 4. KIỂM TRA WEBSITE THỰC TẾ

Trước khi sửa phải kiểm tra:

```text
https://ai.nongnghiepsangtao.io.vn/
```

Xác định:

- V3 hiện tại có đang được phục vụ không
- API production
- WebSocket production
- Auth
- HTTPS
- proxy/reverse proxy
- CORS
- Supabase config
- upload ảnh
- đường dẫn Storage
- AI endpoint

Nếu môi trường OpenCode không thể truy cập trực tiếp domain thì:

- không được giả định;
- kiểm tra config/server/deployment;
- ghi rõ phần chưa kiểm chứng;
- vẫn phải sửa code theo kiến trúc đã xác định.

---

# 5. SUPABASE LÀ NGUỒN DỮ LIỆU CHÍNH

Tất cả dữ liệu nghiệp vụ khảo sát phải lấy từ Supabase.

Không dùng:

```text
image_history.json
filesystem server
localStorage
file JSON
```

làm database chính.

Server filesystem chỉ được coi là cơ chế legacy/AI processing nếu cần tương thích.

---

# 6. CÁC BẢNG CẦN KIỂM TRA/TẠO

Không tạo trùng.

Tối thiểu cần có:

```text
profiles
fields
survey_sessions
survey_points
survey_images
ai_results
diseases
alerts
gps_tracks
sensor_units
sensor_readings
knowledge
```

Nếu project đã có bảng tương đương:

> sử dụng bảng hiện tại, không tạo bảng thứ hai.

---

# 7. SURVEY SESSION

Mỗi lần người dùng bắt đầu khảo sát một ruộng:

```text
survey_sessions
```

Ví dụ:

```json
{
  "id": "...",
  "user_id": "...",
  "field_id": "...",
  "started_at": "...",
  "ended_at": null,
  "status": "active"
}
```

Trạng thái:

```text
active
completed
cancelled
```

---

# 8. SURVEY POINT

Mỗi lần người dùng bấm:

```text
📷 QUÉT ĐIỂM NÀY
```

phải tạo một `survey_point`.

Ví dụ:

```json
{
  "id": "...",
  "survey_session_id": "...",
  "field_id": "...",
  "latitude": 10.123456,
  "longitude": 105.123456,
  "accuracy": 7.2,
  "captured_at": "...",
  "status": "pending"
}
```

Đây là đơn vị khảo sát quan trọng nhất.

---

# 9. GPS

Dùng:

```javascript
navigator.geolocation.watchPosition()
```

Không chỉ lấy GPS một lần.

Theo dõi:

```text
latitude
longitude
accuracy
timestamp
heading
speed
```

Khi bấm quét:

```text
lấy GPS tốt nhất hiện tại
↓
tạo survey_point
```

Không tự đoán GPS.

Nếu GPS accuracy quá kém:

```text
thông báo người dùng
```

nhưng không làm mất ảnh nếu người dùng vẫn xác nhận.

---

# 10. LUỒNG TẢI ẢNH — PHẢI CHỐT

Đây là cơ chế chính thức.

## Bước 1 — Người dùng chụp ảnh

```text
📱 Camera
↓
File ảnh
```

Không chuyển ảnh thành base64 để lưu database.

## Bước 2 — Tạo survey point

```text
survey_session
↓
survey_point
```

Gắn:

```text
GPS
accuracy
timestamp
field
user
```

## Bước 3 — Tạo record ảnh

Tạo:

```text
survey_images
```

Ví dụ:

```json
{
  "id": "...",
  "user_id": "...",
  "survey_session_id": "...",
  "survey_point_id": "...",
  "file_name": "IMG_001.jpg",
  "mime_type": "image/jpeg",
  "size": 1234567,
  "storage_path": "...",
  "sha256": "...",
  "status": "local_pending",
  "created_at": "..."
}
```

## Bước 4 — Upload Supabase Storage

Bucket:

```text
survey-images
```

Cấu trúc ưu tiên:

```text
survey-images/
    {user_id}/
        {survey_session_id}/
            {survey_point_id}/
                original.jpg
```

Không cho frontend tự ý chọn path của user khác.

## Bước 5 — Upload thành công

Cập nhật:

```text
survey_images.status = uploaded
```

và:

```text
storage_path
size
sha256
```

## Bước 6 — Sau đó mới gửi AI

```text
Supabase Storage
↓
AI Server
```

AI Server nhận:

```text
image
survey_point_id
survey_image_id
```

## Bước 7 — AI hoàn thành

AI Server ghi:

```text
ai_results
```

và preview nếu cần:

```text
survey-images/
    user_id/
        survey_session_id/
            survey_point_id/
                original.jpg
                preview.jpg
```

---

# 11. TUYỆT ĐỐI KHÔNG LƯU ẢNH BASE64 TRONG DATABASE

Không được:

```text
survey_images.image_base64
```

Không được:

```text
localStorage = base64
```

Không được nhét ảnh lớn vào JSON database.

Ảnh:

```text
Supabase Storage
```

Metadata:

```text
Supabase Database
```

---

# 12. STORAGE PATH PHẢI KHÔNG TRÙNG

Mỗi ảnh phải có path duy nhất.

Ưu tiên:

```text
{user_id}/{survey_session_id}/{survey_point_id}/original.jpg
```

Nếu một point có nhiều ảnh:

```text
{user_id}/{survey_session_id}/{survey_point_id}/{image_id}/original.jpg
```

Không dùng chỉ:

```text
IMG_001.jpg
```

vì nhiều điện thoại có thể trùng tên file.

---

# 13. ẢNH PREVIEW

AI Server tạo preview/bbox.

Preview phải lưu về:

```text
Supabase Storage
```

Ví dụ:

```text
preview.jpg
```

Không coi filesystem AI Server là kho ảnh cuối cùng.

Nếu server hiện tại đang tạo:

```text
preview_url
```

thì giữ tương thích trong giai đoạn chuyển đổi, nhưng V3 mới phải có khả năng lấy ảnh từ Supabase.

---

# 14. SIGNED URL

Bucket ảnh khảo sát nên để private.

Không public toàn bộ bucket.

Khi V3 cần xem ảnh:

```text
V3
↓
API/service
↓
Supabase
↓
Signed URL
↓
Browser
```

Signed URL có thời hạn.

Không đưa service-role key xuống browser.

---

# 15. SUPABASE KEY

Frontend chỉ được dùng:

```text
SUPABASE_URL
SUPABASE_ANON_KEY
```

hoặc publishable key tương ứng với cấu hình project.

**Tuyệt đối không đưa:**

```text
SUPABASE_SERVICE_ROLE_KEY
```

vào HTML/JavaScript frontend.

Service role chỉ ở server/backend nếu thực sự cần.

---

# 16. RLS

Bắt buộc bật RLS.

User chỉ được truy cập dữ liệu thuộc mình.

Dùng:

```sql
auth.uid()
```

Không tin:

```text
user_id
```

do frontend gửi.

RLS phải áp dụng cho:

```text
survey_sessions
survey_points
survey_images
ai_results
alerts
gps_tracks
```

và các bảng dữ liệu cá nhân khác.

---

# 17. STORAGE SECURITY

Storage cũng phải giới hạn theo user.

Ví dụ logic:

```text
bucket_id = 'survey-images'
AND path bắt đầu bằng auth.uid()
```

Không cho:

```text
user A → đọc path user B
```

Không cho:

```text
user A → upload vào folder user B
```

---

# 18. AI SERVER

Giữ `server.py` hiện tại làm AI engine.

Tận dụng:

```text
/api/ai/predict
/analyze_mobile
/ws
```

và các cơ chế:

```text
get_context()
check_auth()
YOLO
history
preview
fusion
sensor
```

Không viết lại YOLO nếu không cần.

---

# 19. GỬI ẢNH TỪ SUPABASE ĐẾN AI

Ưu tiên flow:

```text
V3
↓
Upload Supabase
↓
survey_images = uploaded
↓
AI Server nhận:
  survey_image_id
  survey_point_id
  storage_path
↓
AI Server lấy ảnh được phép truy cập
↓
YOLO
↓
ai_results
```

Nếu AI Server không thể trực tiếp đọc private Storage:

Tạo một backend endpoint trung gian an toàn hoặc signed URL có thời hạn.

Không public bucket chỉ để AI đọc.

---

# 20. AI RESULT

Bảng:

```text
ai_results
```

phải liên kết:

```text
survey_point_id
survey_image_id
job_id
```

Lưu tối thiểu:

```text
status
class_id
disease
confidence
final_confidence
environment_score
bbox
preview_path
model_version
created_at
updated_at
```

Nếu nhiều bệnh trong một ảnh:

```text
mỗi detection phải được lưu đầy đủ
```

hoặc dùng JSONB có schema rõ ràng.

Không chỉ lưu một chuỗi text.

---

# 21. TRẠNG THÁI ẢNH

Chốt state machine:

```text
local_pending
      ↓
uploading
      ↓
uploaded
      ↓
ai_pending
      ↓
ai_processing
      ↓
completed
```

Lỗi:

```text
upload_failed
ai_failed
```

Retry được.

Không retry vô hạn.

---

# 22. KHÔNG XÓA ẢNH LOCAL QUÁ SỚM

Khi người dùng chụp:

```text
IndexedDB
↓
ảnh tạm
```

Chỉ xóa local copy khi:

```text
Supabase upload thành công
AND
metadata đã xác nhận
```

Nếu cần hỗ trợ offline, giữ local cho đến khi sync hoàn tất.

---

# 23. OFFLINE-FIRST

Khi ngoài đồng mất mạng:

```text
📱 Chụp
↓
IndexedDB
↓
survey_point
↓
survey_image
↓
sync_queue
```

Không báo:

```text
Lỗi hệ thống
```

mà báo:

```text
Đã lưu khảo sát trên điện thoại.
Sẽ đồng bộ khi có mạng.
```

---

# 24. SYNC QUEUE

Tạo:

```text
sync_queue
```

Ví dụ:

```json
{
  "id": "...",
  "entity": "survey_image",
  "entity_id": "...",
  "operation": "upload",
  "status": "pending",
  "retry_count": 0,
  "last_error": null,
  "created_at": "..."
}
```

Các operation:

```text
create
upload
update
delete
```

---

# 25. KHI CÓ MẠNG LẠI

Tự động:

```text
IndexedDB
↓
sync queue
↓
Supabase
↓
upload ảnh
↓
AI
↓
ai_results
↓
Realtime
↓
V3
```

Không yêu cầu người dùng nhập lại.

---

# 26. SUPABASE REALTIME

V3 subscribe:

```text
survey_points
survey_images
ai_results
alerts
sensor_readings
```

Ví dụ:

```text
ai_results.status:
pending
↓
processing
↓
completed
```

V3 cập nhật ngay.

Không F5.

---

# 27. BẢN ĐỒ

Mỗi `survey_point` tạo marker.

Popup:

```text
Điểm khảo sát
GPS
accuracy
thời gian
ảnh
bệnh
confidence
AI status
```

Bấm marker:

```text
→ mở chi tiết khảo sát
```

Bấm record Nhật ký:

```text
→ map panTo đúng GPS
```

---

# 28. NHẬT KÝ

Nhật ký phải lấy từ:

```text
survey_sessions
survey_points
survey_images
ai_results
```

Hiển thị:

```text
ảnh
tên tùy chỉnh
ruộng
GPS
Ấp
Xã
Tỉnh/Thành phố
thời gian
bệnh
confidence
AI status
sync status
⭐
```

---

# 29. MỘT CHUYẾN KHẢO SÁT CÓ NHIỀU ĐIỂM

Ví dụ:

```text
RUỘNG A

Điểm 01 → Đạo ôn 91%
Điểm 02 → Bạc lá 87%
Điểm 03 → Không phát hiện
Điểm 04 → Đạo ôn 76%
Điểm 05 → Chờ AI
...
```

Tất cả phải cùng thuộc:

```text
survey_session_id
```

nếu cùng một chuyến khảo sát.

---

# 30. TRAJECTORY

Nếu cần lưu đường đi:

```text
gps_tracks
```

Không gửi mọi GPS update lên Supabase nếu không cần.

Có thể lấy mẫu theo:

```text
khoảng cách
hoặc
thời gian
```

để tránh dữ liệu quá lớn.

---

# 31. AI OFFLINE

Nếu AI Server tắt:

```text
survey_point = saved
survey_image = uploaded hoặc pending_upload
ai_result = pending
```

Không:

```text
mock disease
```

Không:

```text
pending = no disease
```

Người dùng vẫn tiếp tục khảo sát.

---

# 32. AI ONLINE LẠI

Khi AI hoạt động:

```text
ai_pending
↓
AI Server
↓
YOLO
↓
ai_results
↓
Supabase Realtime
↓
V3
```

Marker tự cập nhật.

---

# 33. API SERVICE TRONG V3

Tạo lớp:

```text
ApiService
```

và:

```text
SupabaseService
StorageService
AIService
RealtimeService
GPSService
SurveyService
SyncService
```

Không để từng component tự viết logic upload.

---

# 34. SUPABASE SERVICE

Tất cả thao tác database:

```text
SupabaseService
```

Ví dụ:

```text
createSurvey()
createSurveyPoint()
createSurveyImage()
updateImageStatus()
createAIResult()
getSurveyPoints()
getHistory()
```

---

# 35. STORAGE SERVICE

Tạo:

```text
StorageService
```

Chịu trách nhiệm:

```text
uploadOriginal()
uploadPreview()
getSignedUrl()
deleteImage()
checkUpload()
```

Không để UI trực tiếp thao tác Storage.

---

# 36. AI SERVICE

Tạo:

```text
AIService
```

Chịu trách nhiệm:

```text
submitImage()
checkStatus()
retryPending()
handleResult()
```

---

# 37. REALTIME SERVICE

Tạo:

```text
RealtimeService
```

Chịu trách nhiệm:

```text
subscribeSurvey()
subscribeAI()
subscribeAlerts()
subscribeSensors()
unsubscribe()
reconnect()
```

---

# 38. AI SERVER → SUPABASE

AI Server sau khi hoàn thành phải ghi kết quả về Supabase.

Không để V3 phụ thuộc:

```text
image_history.json
```

để biết AI result cuối cùng.

Nếu cần giữ endpoint cũ:

```text
/api/image-history
```

thì dùng cho backward compatibility/migration.

---

# 39. WEBSOCKET

Giữ `/ws` cho các event AI/server nếu đang sử dụng.

Nhưng dữ liệu nghiệp vụ cuối cùng phải được ghi vào Supabase.

Mô hình:

```text
AI Server
 ├── ghi Supabase
 └── WebSocket event
          ↓
         V3
```

Supabase Realtime là nguồn đồng bộ bền vững.

WebSocket là kênh phản hồi nhanh.

---

# 40. AUTH

Giữ cơ chế auth hiện tại của server nếu cần tương thích.

Đồng thời đồng bộ user với Supabase Auth.

Không tạo hai user identity độc lập.

Phải có mapping rõ:

```text
Supabase auth.uid()
        ↕
server user_id
```

Không hard-code user ID.

---

# 41. USER DATA OWNERSHIP

Không được tin ID frontend gửi lên.

Server/Supabase phải xác định quyền bằng:

```text
auth.uid()
```

và ownership.

Không cho user:

```text
đổi user_id
```

để đọc dữ liệu khác.

---

# 42. ẢNH GỐC VÀ PREVIEW

Chốt:

```text
original.jpg
```

là ảnh người dùng khảo sát.

```text
preview.jpg
```

là ảnh AI đã annotate bbox nếu có.

Cả hai thuộc cùng:

```text
survey_image_id
```

hoặc mapping rõ ràng.

---

# 43. HASH ẢNH

Tạo SHA-256 cho ảnh nếu phù hợp.

Dùng để:

```text
phát hiện upload trùng
cache
đồng bộ
kiểm tra toàn vẹn
```

Nếu cùng ảnh được retry:

```text
không tạo bản sao vô hạn
```

---

# 44. RESUME UPLOAD

Nếu ảnh lớn và thiết bị/mạng yếu:

- nếu Supabase SDK hỗ trợ cơ chế upload phù hợp thì sử dụng;
- nếu không, retry có kiểm soát;
- không tạo nhiều bản copy.

Không làm mất ảnh khi upload gián đoạn.

---

# 45. NÉN ẢNH

Trước upload:

```text
giữ ảnh đủ chất lượng cho YOLO
```

Có thể tạo:

```text
original
thumbnail
```

Không giảm chất lượng quá mức làm ảnh AI kém chính xác.

Không lưu thumbnail thay cho original.

---

# 46. CAMERA MOBILE

V3 phải ưu tiên camera điện thoại.

Hỗ trợ:

```text
capture
file picker
gallery
```

Nếu browser cho phép:

```text
capture="environment"
```

để dùng camera sau.

---

# 47. KHÔNG CHẶN KHẢO SÁT VÌ AI

Nguyên tắc:

```text
AI chậm
→ vẫn đi khảo sát

AI offline
→ vẫn đi khảo sát

Internet mất
→ vẫn đi khảo sát
```

---

# 48. THÔNG BÁO TRẠNG THÁI

Hiển thị rõ:

```text
📍 GPS: OK
☁️ Supabase: OK
🤖 AI: OK
🔄 Sync: 3
```

Nếu AI offline:

```text
🤖 AI: OFFLINE
```

nhưng app vẫn hoạt động.

---

# 49. PERMISSIONS POLICY

Kiểm tra server header.

Nếu đang có:

```text
geolocation=()
```

phải sửa để production domain được phép sử dụng GPS.

---

# 50. CORS

Production phải cho phép:

```text
https://ai.nongnghiepsangtao.io.vn
```

Không để localhost là cấu hình production chính.

---

# 51. KHÔNG ĐƯỢC

```text
❌ dùng JSON file làm database chính
❌ dùng filesystem AI server làm database chính
❌ lưu base64 ảnh trong DB
❌ lưu ảnh lớn trong localStorage
❌ đưa service_role key xuống frontend
❌ public toàn bộ bucket ảnh cá nhân
❌ bỏ RLS
❌ mock AI production
❌ tự bịa GPS
❌ mất ảnh khi offline
❌ tạo survey point không có liên kết ảnh
❌ gắn nhầm AI result sang điểm khác
❌ reload trang để cập nhật realtime
❌ hard-code localhost production
❌ tạo backend/database trùng nếu đã có
```

---

# 52. KIỂM TRA 5 ĐIỂM NGOÀI ĐỒNG

Bắt buộc test thực tế bằng điện thoại:

```text
1. Mở website
2. Login
3. Cho GPS
4. Chọn ruộng
5. Start survey
6. Quét điểm 01
7. Upload Supabase
8. AI
9. Kết quả
10. Marker
11. Điểm 02
12. Điểm 03
13. Điểm 04
14. Điểm 05
```

Phải chứng minh:

```text
5 survey_points
5 ảnh
5 GPS
đúng 5 liên kết
AI result đúng từng point
```

---

# 53. TEST MẤT MẠNG

Trong lúc khảo sát:

```text
Điểm 01 → online
Điểm 02 → online
Điểm 03 → offline
Điểm 04 → offline
Điểm 05 → offline
```

Phải có:

```text
03 local_pending
04 local_pending
05 local_pending
```

Không mất ảnh.

Khi mạng trở lại:

```text
03 → upload
04 → upload
05 → upload
```

Sau đó:

```text
AI
↓
result
↓
Supabase
↓
Realtime
↓
V3
```

---

# 54. TEST AI SERVER OFFLINE

Tắt AI Server.

V3 vẫn phải:

```text
GPS
camera
survey
Supabase
Storage
map
history
```

Ảnh có thể:

```text
uploaded
ai_pending
```

Khi AI Server bật:

```text
ai_pending
↓
AI
↓
completed
```

---

# 55. TEST USER A / USER B

User A:

```text
không được đọc
ảnh/ruộng/kết quả
của User B
```

Test cả:

```text
Database RLS
Storage RLS
AI API authorization
```

---

# 56. TEST RELOAD

Sau khi quét 5 điểm:

```text
F5
```

Dữ liệu vẫn phải tồn tại vì nguồn chính là:

```text
Supabase
```

Không phụ thuộc state RAM của V3.

---

# 57. TEST ĐÓNG MỞ TRÌNH DUYỆT

Đóng browser.

Mở lại:

```text
https://ai.nongnghiepsangtao.io.vn/
```

Phải đọc lại được:

```text
survey
points
images
AI results
```

---

# 58. TEST ẢNH

Kiểm tra:

```text
original.jpg
preview.jpg
signed URL
permission
hash
size
```

User khác không được mở ảnh.

---

# 59. TEST REALTIME

Tạo AI result từ server.

Không F5.

V3 phải tự nhận:

```text
pending
→ processing
→ completed
```

và marker/popup/Nhật ký phải thay đổi.

---

# 60. OUTPUT BẮT BUỘC SAU KHI SỬA

Báo cáo:

```text
1. File đã sửa
2. File mới
3. Supabase tables
4. Supabase Storage buckets
5. RLS policies
6. Upload flow
7. Offline flow
8. AI flow
9. Realtime flow
10. GPS flow
11. API đã sử dụng
12. API mới
13. WebSocket
14. Auth mapping
15. Production config
16. Test 5 điểm
17. Test offline
18. Test AI offline
19. Test RLS
20. Lỗi còn lại
```

Mỗi mục phải ghi đúng:

```text
DONE
PARTIAL
TODO
```

Không ghi DONE nếu chưa kiểm chứng.

---

# 61. TIÊU CHUẨN HOÀN THÀNH

Chỉ coi hoàn thành khi luồng sau hoạt động:

```text
📱 ĐIỆN THOẠI
      ↓
V3
      ↓
GPS
      ↓
SURVEY POINT
      ↓
SUPABASE
      ↓
ẢNH → SUPABASE STORAGE
      ↓
AI SERVER
      ↓
YOLO
      ↓
AI RESULT
      ↓
SUPABASE DATABASE
      ↓
SUPABASE REALTIME
      ↓
V3
      ↓
🗺️ MARKER
+
📖 NHẬT KÝ
+
📷 ẢNH BBOX
```

Và khi mất mạng:

```text
📱
↓
IndexedDB
↓
sync_queue
↓
mạng trở lại
↓
Supabase
↓
AI
↓
Realtime
```

**Không được chỉ lập kế hoạch. Phải sửa code, cấu hình, migration cần thiết và chạy kiểm thử.**
