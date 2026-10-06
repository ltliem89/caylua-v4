# AI RICE / CÂY LÚA — MASTER SPEC CẢI TIẾN TOÀN DIỆN V3

## 0. Quyết định nền tảng

### Nền tảng duy nhất

`AI_Rice_UX_Prototype_V3_CLICK_POPUP_FINAL.html`

Không thay nền tảng này bằng frontend khác.

Mọi cải tiến phải tích hợp trực tiếp vào V3:

- bản đồ Leaflet;
- sidebar;
- Nhật ký;
- Việc cần làm;
- Phân tích;
- Kiến thức;
- Dữ liệu;
- popup;
- camera;
- upload;
- chọn vị trí;
- AI Adapter;
- Supabase;
- dữ liệu bệnh;
- responsive mobile.

File V3 hiện tại đã có các thành phần trên, nhưng nhiều phần vẫn đang ở mức prototype. Ví dụ `data` là mảng JavaScript trong trang, `saveCheck()` mới ghi một phần dữ liệu vào `inspections`, GPS hiện dùng `getCurrentPosition()`, và AI AUTO có fallback tới mock provider. Đây là các điểm phải nâng cấp trong một lần tái cấu trúc. fileciteturn5file0

---

# 1. Mục tiêu của lần cải tiến này

Không tiếp tục sửa từng lỗi nhỏ.

Thực hiện **một lần tái cấu trúc nền tảng** để V3 trở thành:

```text
WEB CÂY LÚA
= Offline-first
+ Realtime
+ AI optional
+ GPS realtime
+ Bản đồ
+ Cảnh báo
+ Nhật ký
+ Kho dữ liệu
+ Kiến thức bệnh
+ Supabase
+ YOLO Server
+ Cloud production
```

Mục tiêu UX:

> Người dùng luôn có thể mở hệ thống, xem dữ liệu, xem bản đồ, dùng GPS, nhận cảnh báo và tra cứu kiến thức; AI chỉ bổ sung khả năng phân tích khi server AI sẵn sàng.

---

# 2. Nguyên tắc cốt lõi

## 2.1. Server AI không được là điểm chết

Sai:

```text
AI Server OFF
→ Web lỗi
→ Map lỗi
→ Nhật ký lỗi
```

Đúng:

```text
AI Server OFF
→ Map vẫn chạy
→ GPS vẫn chạy
→ Auto-follow vẫn chạy
→ Cảnh báo vẫn chạy
→ Nhật ký vẫn xem được
→ Kiến thức vẫn xem được
→ Dữ liệu local vẫn truy xuất được
→ Chỉ AI mới bị OFFLINE
```

---

# 3. Phân loại trạng thái hệ thống

Không dùng một biến `online`.

Phải tách:

```text
APP_STATUS
GPS_STATUS
AI_STATUS
CLOUD_STATUS
MAP_STATUS
SYNC_STATUS
```

Ví dụ:

```text
🟢 Ứng dụng
🟢 GPS
🔴 AI
🟢 Cloud
🟢 Bản đồ
🟡 Đồng bộ
```

---

# 4. Kiến trúc tổng thể mới

```text
                         INTERNET
                            │
                            ▼
              ai.nongnghiepsangtao.io.vn
                            │
                ┌───────────┴───────────┐
                │                       │
                ▼                       ▼
         STATIC / WEB V3          CLOUD SERVICES
                │                       │
                │                ┌──────┴──────┐
                │                │             │
                │             Supabase      Storage
                │                │
                ▼                ▼
        ┌────────────────────────────────┐
        │       AI RICE V3 CLIENT        │
        │                                │
        │ Map/GPS/Alert                  │
        │ Local DB                       │
        │ History                        │
        │ Knowledge                      │
        │ Sync Queue                     │
        │ AI Service                     │
        └───────────────┬────────────────┘
                        │
                  AI khi cần
                        │
                        ▼
              ┌───────────────────┐
              │   AI SERVER       │
              │                   │
              │ FastAPI           │
              │ YOLOv8            │
              │ WebSocket         │
              │ Preview/BBox      │
              └───────────────────┘
```

---

# 5. Offline-first

## 5.1. Local database

Không tiếp tục dùng localStorage cho toàn bộ lịch sử.

Dùng:

```text
IndexedDB
```

cho dữ liệu có cấu trúc và ảnh/blob cần lưu cục bộ.

IndexedDB phù hợp hơn Web Storage cho lượng dữ liệu lớn, dữ liệu có cấu trúc và có thể lưu Blob/file; nó cũng hỗ trợ ứng dụng hoạt động khi mạng không ổn định hoặc không có mạng. citeturn0search4turn0search9

---

# 6. Local stores

Tạo các store:

```text
app_meta
users
fields
rice_locations
seasons
inspections
ai_results
inspection_images
alerts
alert_events
tasks
knowledge
sync_queue
settings
gps_state
```

---

# 7. Local-first write

Mọi thao tác quan trọng phải ghi local trước:

```text
User action
 ↓
IndexedDB
 ↓
UI cập nhật ngay
 ↓
Sync queue
 ↓
Supabase khi có mạng
```

Không bắt người dùng chờ server/database để thấy dữ liệu vừa nhập.

---

# 8. Sync Engine

Tạo:

```text
SyncService
```

Trạng thái:

```text
pending
syncing
synced
failed
conflict
```

Mỗi thay đổi có:

```js
{
  id,
  entity,
  entity_id,
  operation,
  payload,
  created_at,
  retry_count,
  last_error
}
```

---

# 9. Quy tắc đồng bộ

### Có Internet

```text
local → cloud
cloud → local
```

### Mất Internet

```text
local only
```

### Có Internet lại

```text
sync_queue
→ upload thay đổi
→ nhận thay đổi cloud
→ cập nhật local
```

---

# 10. Không xóa dữ liệu khi sync lỗi

Nếu Supabase lỗi:

```text
CLOUD_STATUS = ERROR
```

nhưng:

```text
APP = hoạt động
LOCAL DATA = hoạt động
```

Record phải giữ ở:

```text
sync_queue
```

---

# 11. Conflict

Mỗi record cần:

```text
updated_at
updated_by
device_id
version
```

Mặc định:

```text
last-write-wins
```

cho metadata đơn giản.

Nhưng với:

- bệnh;
- kết quả AI;
- ảnh;
- lịch sử;

không được âm thầm ghi đè.

Phải giữ version/record history khi cần.

---

# 12. Dữ liệu cloud

Supabase trở thành nguồn cloud chính.

Đề xuất:

```text
profiles
fields
rice_locations
seasons
inspections
inspection_images
ai_results
disease_events
tasks
alerts
sensor_readings
knowledge_articles
sync_audit
```

---

# 13. `fields`

Thông tin ruộng:

```text
id
user_id
name
area
variety
soil_type
water_source
ap
xa
tinh
lat
lng
created_at
updated_at
```

---

# 14. `seasons`

```text
id
field_id
season_name
sowing_date
transplant_date
expected_harvest
growth_stage
status
created_at
updated_at
```

---

# 15. `rice_locations`

Đây là nguồn dữ liệu cho bản đồ/cảnh báo.

```text
id
field_id
name
lat
lng
radius_m
ap
xa
tinh
active
created_at
updated_at
```

Không trộn `rice_locations` với `ai_results`.

---

# 16. `inspections`

Một lần kiểm tra:

```text
id
field_id
season_id
user_id
custom_name
inspection_time
latitude
longitude
gps_accuracy
location_source
growth_stage
notes
ai_status
ai_provider
job_id
starred
created_at
updated_at
```

---

# 17. `ai_results`

Không nhét toàn bộ kết quả vào một field text.

```text
id
inspection_id
disease_id
label_vi
confidence
bbox_json
class_id
model_version
provider
created_at
```

Nếu một ảnh có 5 vùng bệnh:

```text
1 inspection
→ nhiều ai_results
```

---

# 18. `inspection_images`

```text
id
inspection_id
kind
storage_path
local_blob_key
width
height
file_size
created_at
```

`kind`:

```text
original
preview
thumbnail
```

---

# 19. Storage ảnh

Không lưu base64 trong database.

Cloud dùng Supabase Storage.

Supabase Storage hỗ trợ file storage, CDN, quyền truy cập và upload resumable/TUS; resumable upload phù hợp khi file lớn hoặc mạng không ổn định. citeturn0search12turn0search1

Đường dẫn:

```text
users/{user_id}/fields/{field_id}/inspections/{inspection_id}/original.jpg
users/{user_id}/fields/{field_id}/inspections/{inspection_id}/preview.jpg
users/{user_id}/fields/{field_id}/inspections/{inspection_id}/thumb.jpg
```

---

# 20. Ảnh local

Trước khi upload cloud:

```text
camera
 ↓
Blob
 ↓
IndexedDB
 ↓
record local
```

Sau đó mới:

```text
upload Storage
```

---

# 21. AI Service

AI là module tùy chọn:

```text
AIService
```

Không phải dependency của app.

---

# 22. AI status

```text
CHECKING
ONLINE
OFFLINE
BUSY
ERROR
```

---

# 23. Health check

Server phải có:

```text
GET /api/health
```

Trả:

```json
{
  "status": "ok",
  "model_loaded": true,
  "model_version": "best02.pt",
  "device": "cuda",
  "server_time": "...",
  "queue": 0
}
```

Frontend kiểm tra:

- lúc mở app;
- trước khi phân tích;
- sau khi mất kết nối;
- định kỳ vừa phải.

---

# 24. Không chờ AI khi mở app

Sai:

```text
open
→ wait server
→ render
```

Đúng:

```text
open
→ render UI
→ load IndexedDB
→ map
→ GPS
→ alert
→ check AI
→ check cloud
```

---

# 25. AI offline

Khi AI offline:

```text
📷 Kiểm tra ruộng
```

vẫn mở.

Sau khi chụp:

```text
Ảnh đã lưu

🤖 AI hiện offline

[Để chờ phân tích]
[Hủy]
```

Record:

```text
ai_status = pending
```

Không được đổi thành:

```text
Không phát hiện bệnh
```

---

# 26. Mock AI

Prototype hiện có mock fallback.

Production:

```text
KHÔNG dùng mock
```

Mock chỉ:

```text
development
test
demo
```

---

# 27. PlantNet

Nếu giữ PlantNet:

```text
provider = plantnet
```

phải hiển thị rõ.

Không được gọi kết quả PlantNet là:

```text
YOLO Cây Lúa
```

---

# 28. YOLO

YOLOv8 server hiện đã có:

- FastAPI;
- `/analyze_mobile`;
- `/preview/...`;
- `/ws`;
- lưu ảnh original;
- lưu preview có bbox;
- broadcast kết quả qua WebSocket. fileciteturn7file1L1-L10 fileciteturn7file3L1-L8

Giữ kiến trúc đó nhưng chuẩn hóa API production.

---

# 29. Preview YOLO

`preview_url` phải là ảnh thật do YOLO annotate.

Không vẽ bbox giả trên frontend.

---

# 30. WebSocket

Dùng cho:

```text
AI result
```

Không dùng WebSocket AI làm cơ chế duy nhất cho realtime toàn hệ thống.

---

# 31. Realtime cloud

Supabase Realtime có thể gửi thay đổi database qua WebSocket; Postgres Changes hỗ trợ INSERT/UPDATE/DELETE và lọc theo bảng/cột. Supabase hiện khuyến nghị Broadcast cho khả năng mở rộng/bảo mật tốt hơn ở quy mô lớn, còn Postgres Changes đơn giản hơn. citeturn0search3turn0search10

Kiến trúc:

```text
AI server
   ↓
DB
   ↓
Supabase Realtime
   ↓
mọi client
```

---

# 32. Realtime nào dùng cái gì?

## AI WebSocket

Dùng:

```text
job progress
AI detection
preview ready
```

## Supabase Realtime

Dùng:

```text
inspection changed
field changed
alert changed
sensor changed
task changed
```

## GPS

Dùng:

```text
browser Geolocation
```

Không gửi GPS liên tục lên server chỉ để điều khiển bản đồ.

---

# 33. GPS realtime

Hiện V3 dùng:

```js
getCurrentPosition()
```

Nâng thành:

```js
watchPosition()
```

`watchPosition()` gọi callback khi vị trí thay đổi, yêu cầu HTTPS và quyền vị trí của người dùng. citeturn0search0turn0search2

---

# 34. GPS state

```js
{
  status: "active",
  lat,
  lng,
  accuracy,
  heading,
  speed,
  timestamp
}
```

---

# 35. Auto-follow

Bản đồ tự di chuyển theo người dùng khi:

```text
followMode = true
```

Khi người dùng kéo map:

```text
followMode = false
```

Hiện:

```text
↩ Theo vị trí của tôi
```

---

# 36. Cảnh báo vị trí

Không phụ thuộc AI.

Tính khoảng cách trên client:

```text
GPS
 ↓
distance()
 ↓
rice_locations
 ↓
radius_m
 ↓
alert
```

---

# 37. Alert engine

Tạo:

```text
AlertService
```

Loại:

```text
NEAR_FIELD
DISEASE_HISTORY
AI_RESULT
SENSOR_WARNING
TASK_DUE
SYNC_ERROR
SERVER_OFFLINE
```

---

# 38. Cảnh báo gần ruộng

Ví dụ:

```text
🌾 Bạn đang gần Ruộng A3
Khoảng cách: 72 m

⚠️ Khu vực này có 2 lần ghi nhận bệnh gần đây.

[Kiểm tra ruộng]
[Xem lịch sử]
[Đóng]
```

---

# 39. Không spam

Cảnh báo chỉ khi:

```text
outside → inside
```

hoặc đến thời gian nhắc lại.

Lưu:

```text
alert_events
```

---

# 40. Cảnh báo bệnh lịch sử

Không nói:

```text
Ruộng đang bị bệnh
```

nếu chỉ có lịch sử.

Nói:

```text
Khu vực này từng ghi nhận...
```

---

# 41. Sensor/IoT

Đề tài đã xác định kết hợp:

- nhiệt độ;
- độ ẩm;
- pH;
- EC đất;

để hỗ trợ đánh giá tình trạng cây lúa. fileciteturn6file0L1-L5

Vì vậy thiết kế sẵn:

```text
sensor_readings
```

với:

```text
device_id
field_id
temperature
humidity
soil_ph
soil_ec
battery
timestamp
```

---

# 42. Realtime sensor

Nếu ESP32 online:

```text
ESP32
 ↓
API/MQTT/Realtime gateway
 ↓
Supabase
 ↓
Web V3
```

Web cập nhật không reload.

Nếu sensor offline:

```text
last_seen
```

và:

```text
🟡 Sensor mất kết nối
```

Không xóa giá trị cuối cùng.

---

# 43. Thông tin bệnh — nâng cấp thành Knowledge Engine

Không chỉ là mảng:

```js
DISEASES
```

trong HTML.

Tách thành:

```text
Disease Knowledge
```

có version.

---

# 44. Hồ sơ bệnh

Mỗi bệnh:

```text
id
name_vi
name_en
group
causal_agent
vector_or_spread
target_organs
symptoms
favorable_conditions
management
differential
ai_visual_features
severity
growth_stages
sources
updated_at
version
```

---

# 45. Nguồn kiến thức

Kiến thức bệnh phải có nguồn.

Ưu tiên:

1. IRRI Rice Knowledge Bank.
2. Tài liệu kỹ thuật nông nghiệp chính thống.
3. Tài liệu địa phương.
4. Tài liệu nghiên cứu khoa học.

IRRI có tài liệu chẩn đoán bệnh lúa, trong đó mô tả bạc lá và sọc lá vi khuẩn theo triệu chứng thực địa; tài liệu khô vằn cũng nêu triệu chứng, điều kiện thuận lợi và quản lý. citeturn2search16turn2search0

---

# 46. Không dùng AI để tự viết khuyến cáo thuốc

AI nhận dạng:

```text
Bệnh có khả năng là X
```

không đồng nghĩa:

```text
hãy phun thuốc Y
```

Khuyến cáo phải lấy từ knowledge base đã kiểm duyệt.

---

# 47. Chẩn đoán phân biệt

Đây là chức năng quan trọng vì nhiều triệu chứng giống nhau.

Ví dụ IRRI ghi nhận khô vằn có thể giống thối thân hoặc sâu đục thân, và cần đối chiếu tổn thương bẹ/điều kiện thực địa. citeturn2search0

UI:

```text
🤖 AI nhận dạng:
Bệnh khô vằn — 87%

🔎 Cần phân biệt:
• Thối thân
• Sâu đục thân

📌 Nên kiểm tra:
• bẹ lá
• vị trí vết bệnh
• điều kiện ruộng
```

---

# 48. Confidence không phải độ chắc chắn tuyệt đối

Hiển thị:

```text
Confidence: 87%
```

nhưng thêm:

```text
AI hỗ trợ nhận dạng hình ảnh.
Cần đối chiếu triệu chứng và điều kiện ruộng.
```

---

# 49. Bệnh + điều kiện ruộng

Kết quả cuối không nên chỉ là:

```text
ảnh → bệnh
```

Mà:

```text
Ảnh
+
giai đoạn lúa
+
lịch sử ruộng
+
nhiệt độ
+
độ ẩm
+
pH
+
EC
+
thời gian
=
đánh giá tổng hợp
```

Đây phù hợp với hướng nghiên cứu của đề tài: kết hợp YOLOv8 với dữ liệu cảm biến môi trường/đất. fileciteturn6file0L1-L5

---

# 50. Timeline theo thời gian

Mỗi ruộng phải có timeline:

```text
01/09
🟢 Bình thường

08/09
🟡 Theo dõi

15/09
🔴 Đạo ôn 82%

22/09
🔴 Đạo ôn 91%

29/09
🟢 Không phát hiện
```

Có thể xem:

```text
7 ngày
30 ngày
1 vụ
Tất cả
```

---

# 51. Biểu đồ

Tab Phân tích cần dữ liệu thật.

Biểu đồ:

```text
Bệnh theo thời gian
Confidence theo thời gian
Số lần kiểm tra
Số ruộng có vấn đề
Sensor theo thời gian
```

Không hard-code số demo trong production.

---

# 52. Các cửa sổ UI — nguyên tắc

Không mở quá nhiều modal cùng lúc.

Dùng:

```text
Bottom sheet
Side panel
Modal
Toast
Drawer
```

theo ngữ cảnh.

---

# 53. Cửa sổ ưu tiên

## Map

Luôn là nền.

## Panel

Thông tin ruộng/bệnh.

## Bottom sheet mobile

Nhật ký.

## Modal

Tạo kiểm tra.

## Toast

Trạng thái nhanh:

```text
AI online
AI offline
Đã lưu
Đã đồng bộ
GPS mất tín hiệu
```

---

# 54. Quick actions

Trên bản đồ:

```text
📍 Theo tôi
📷 Kiểm tra
🔔 Cảnh báo
🗺️ Layer
```

Không giấu các chức năng quan trọng trong menu sâu.

---

# 55. Context panel

Khi chọn ruộng:

```text
🌾 Ruộng A3

🟢/🟡/🔴 trạng thái

📍 vị trí
🌱 tuổi lúa
🌿 giai đoạn
💧 sensor
🤖 AI
📜 lịch sử

[Kiểm tra]
[Xem lịch sử]
[Xem bệnh]
```

---

# 56. Nhật ký

Card:

```text
[thumbnail]
⭐ Ruộng A3
Bệnh đạo ôn
91%
29/09 08:32

Ấp...
Xã...
TP...

🤖 Đã phân tích
📍 72m
```

---

# 57. Bộ lọc Nhật ký

```text
Tất cả
⭐ Yêu thích
Có bệnh
Theo dõi
Không phát hiện
Chờ AI
Lỗi
```

---

# 58. Sort

```text
Mới nhất
Cũ nhất
Tên A-Z
Confidence cao
Nhiều vùng bệnh
Gần vị trí hiện tại
```

---

# 59. Search

Tìm:

```text
tên ruộng
bệnh
địa chỉ
ấp
xã
tỉnh
mã job
```

---

# 60. Data Explorer

Tab Dữ liệu không chỉ hiển thị số lượng.

Cho phép:

```text
Tìm
Lọc
Sort
Xem chi tiết
Export
```

Export:

```text
CSV
JSON
```

Nếu có quyền.

---

# 61. Truy xuất dữ liệu

Mọi record phải có:

```text
ID
timestamp
field
season
location
image
AI result
provider
model version
sync status
```

Có thể truy ngược:

```text
Ruộng
→ vụ
→ lần kiểm tra
→ ảnh
→ AI
→ bệnh
→ lịch sử
```

---

# 62. Audit

Ghi:

```text
created
updated
deleted
synced
analyzed
failed
```

Không xóa vật lý ngay nếu cần truy vết.

---

# 63. Xóa dữ liệu

UI:

```text
Xóa
```

→ soft delete:

```text
deleted_at
```

Sau thời gian lưu trữ mới cleanup.

---

# 64. Bảo mật

Server hiện có CORS:

```text
allow_origins=["*"]
```

phải sửa khi production.

Chỉ allow origin thật:

```text
https://ai.nongnghiepsangtao.io.vn
```

---

# 65. Secret

Không để:

```text
service_role_key
admin secret
password
```

trong HTML.

Chỉ public/anon key phù hợp mới được phép xuất hiện client.

---

# 66. Preview auth

Endpoint preview hiện yêu cầu user/key qua query string. Đây là thiết kế cần xem lại vì secret trong URL dễ lọt vào history/log/referrer.

Thiết kế production nên chuyển sang:

```text
authenticated request
```

hoặc signed URL có thời hạn.

Không dùng access key dài hạn trong URL ảnh.

---

# 67. Server AI hiện tại

Server hiện:

- bind `0.0.0.0`;
- chạy Uvicorn;
- Cloudflare Tunnel;
- `/analyze_mobile`;
- `/preview`;
- `/ws`;
- lưu original/preview/result theo user. fileciteturn7file1L1-L10 fileciteturn7file0L1-L10

Giữ phần này nhưng bổ sung:

```text
/api/health
/api/jobs/{job_id}
/api/history
/api/locations
```

---

# 68. AI job model

Không xử lý AI theo kiểu request dài duy nhất nếu cần scale.

Tạo:

```text
AI Job
```

```text
queued
processing
completed
failed
cancelled
```

---

# 69. AI job UX

```text
📷 Ảnh
↓
🟡 Đang chờ
↓
🔵 Đang phân tích
↓
🟢 Hoàn tất
```

Nếu lỗi:

```text
🔴 Lỗi
[Thử lại]
```

---

# 70. WebSocket reconnect

Nếu WebSocket mất:

```text
retry:
1s
2s
5s
10s
30s
```

Không reload toàn app.

---

# 71. Cloud realtime reconnect

Supabase realtime mất:

```text
CLOUD_STATUS = reconnecting
```

UI vẫn dùng local.

---

# 72. Map offline

Phân biệt:

### AI server offline

Bản đồ vẫn hoạt động.

### Internet toàn bộ mất

Map nền online có thể không tải được.

Phải cache app shell/dữ liệu vị trí.

Nếu muốn bản đồ nền offline thật thì phải triển khai tile/offline map riêng; không tuyên bố có offline map chỉ vì có service worker.

---

# 73. PWA

Bổ sung:

```text
manifest.json
service-worker.js
```

Service worker có thể cache app shell và tài nguyên cần thiết; chiến lược cache phải được thiết kế rõ ràng vì service worker cho phép fallback khi mạng chập chờn/offline. citeturn1search0turn1search4

Có thể dùng Workbox thay vì tự xây toàn bộ cache logic; web.dev mô tả Workbox là bộ công cụ cấp cao cho Service Worker/Cache Storage. citeturn1search10

---

# 74. Cache policy

## Cache-first

```text
HTML
CSS
JS
icons
knowledge static
```

## Stale-while-revalidate

```text
knowledge data
field metadata
```

## Network-first

```text
realtime records
cloud status
```

## Never cache

```text
secret
admin data
private signed URLs lâu hạn
```

Các chiến lược cache khác nhau phù hợp với mức độ tươi của dữ liệu; service worker cho phép kiểm soát chính xác hơn HTTP cache. citeturn1search0

---

# 75. Cập nhật app

Không để service worker giữ phiên bản cũ quá lâu.

Có:

```text
APP_VERSION
CACHE_VERSION
```

Nếu có bản mới:

```text
🔄 Có phiên bản mới
[Cập nhật]
```

---

# 76. Cỡ cửa sổ / UI thích ứng

V3 đã có responsive.

Nâng cấp:

### Mobile

```text
Map full
Bottom sheet
Quick actions
```

### Tablet

```text
Sidebar + map
```

### Desktop

```text
Sidebar + map + panel
```

---

# 77. Accessibility

Giữ điều chỉnh cỡ chữ.

Thêm:

- aria-label;
- focus;
- keyboard;
- contrast;
- trạng thái không chỉ dựa vào màu.

Ví dụ:

```text
🔴 Có vấn đề
```

không chỉ:

```text
màu đỏ
```

---

# 78. Loading state

Không để màn hình trống.

Hiển thị:

```text
Đang tải dữ liệu...
```

hoặc skeleton.

---

# 79. Empty state

Ví dụ:

```text
📜 Chưa có lần kiểm tra

Hãy chụp ảnh đầu tiên để bắt đầu theo dõi ruộng.
```

---

# 80. Error state

Không dùng:

```text
alert("error")
```

cho mọi thứ.

Dùng toast/panel:

```text
⚠️ Không kết nối được AI.

Bản đồ và dữ liệu của bạn vẫn hoạt động.
```

---

# 81. Offline banner

Khi Internet mất:

```text
🟡 Đang offline — dữ liệu mới sẽ đồng bộ khi có mạng.
```

Không che toàn màn hình.

---

# 82. AI offline banner

Riêng:

```text
🤖 AI Server offline
```

Không nói:

```text
Hệ thống offline
```

vì app vẫn hoạt động.

---

# 83. Cloud offline banner

```text
☁️ Cloud tạm thời không đồng bộ
```

Nhưng dữ liệu local vẫn dùng.

---

# 84. GPS offline/denied

```text
📍 GPS chưa được cấp quyền
```

Bản đồ vẫn dùng.

---

# 85. Knowledge offline

Các hồ sơ bệnh cơ bản phải cache.

Người dùng vẫn có thể:

```text
Tìm bệnh
Xem triệu chứng
Xem điều kiện
Xem chẩn đoán phân biệt
Xem khuyến cáo
```

khi AI server/cloud không có.

---

# 86. Knowledge update

Khi cloud online:

```text
knowledge version
```

Nếu version mới:

```text
download
→ validate
→ replace local
```

Không thay dữ liệu kiến thức đang dùng bằng dữ liệu chưa kiểm tra.

---

# 87. Nguồn bệnh phải được lưu

Mỗi article:

```text
source_name
source_url
source_date
version
review_status
```

Ví dụ IRRI cung cấp tài liệu bệnh và quản lý; đây là nguồn phù hợp để xây lớp kiến thức tham khảo, nhưng nội dung cuối cùng của dự án phải giữ phân biệt giữa thông tin tham khảo và chẩn đoán AI. citeturn2search0turn2search16

---

# 88. Kiến thức không chỉ là bệnh

Mở rộng:

```text
Bệnh
Sâu hại
Rối loạn dinh dưỡng
Ngộ độc
Quản lý nước
Dinh dưỡng
Giống
Giai đoạn sinh trưởng
```

Đề tài hiện cũng xác định các vấn đề dinh dưỡng/môi trường có thể gây biểu hiện giống bệnh; IRRI lưu ý chẳng hạn thiếu N có thể gây vàng/lùn và dễ nhầm với một số thiếu chất khác, cần kết hợp kiểm tra đất/cây khi xác nhận. fileciteturn6file0L1-L5 citeturn2search7

---

# 89. Không chẩn đoán quá mức

AI:

```text
Nhận dạng hình ảnh
```

Knowledge:

```text
Đối chiếu triệu chứng
```

Sensor:

```text
Điều kiện môi trường
```

Human:

```text
Xác nhận thực địa
```

Kết luận nên là:

```text
Khả năng / cần kiểm tra
```

không phải lúc nào cũng:

```text
đã xác định 100%
```

---

# 90. Dashboard thời gian thực

Tab Phân tích:

```text
AI
GPS
Cloud
Sensor
Ruộng
Bệnh
```

Cập nhật realtime.

Ví dụ:

```text
🟢 AI Server
🟢 8 ruộng online
🟡 1 sensor offline
🔴 2 ruộng cần kiểm tra
```

---

# 91. Data freshness

Mỗi dữ liệu hiển thị:

```text
Cập nhật 10 giây trước
Cập nhật 5 phút trước
```

Không để người dùng tưởng dữ liệu realtime nếu thực tế là cache.

---

# 92. Sync indicator trên record

```text
☁️ synced
🟡 pending
🔴 error
```

---

# 93. AI indicator trên record

```text
🤖 analyzed
🟡 pending
🔴 failed
⚪ not analyzed
```

---

# 94. Map marker thông minh

Marker theo trạng thái:

```text
🟢 bình thường
🟡 theo dõi
🔴 có vấn đề
⚪ chưa phân tích
```

Click marker:

```text
Tên ruộng
Trạng thái
Bệnh gần nhất
Lần kiểm tra gần nhất
Khoảng cách hiện tại
```

---

# 95. Cluster

Nếu nhiều ruộng:

```text
marker clustering
```

để không rối bản đồ.

Chỉ dùng khi số marker đủ lớn.

---

# 96. Near-me

Thêm:

```text
Gần tôi
```

Sort ruộng theo:

```text
distance
```

không cần server.

---

# 97. Search địa điểm

Search:

```text
ruộng
ấp
xã
tỉnh
bệnh
```

---

# 98. Tasks

Tab Việc cần làm lấy từ dữ liệu thật:

```text
task
```

Ví dụ:

```text
🔴 Kiểm tra Ruộng A3
🟡 Theo dõi Ruộng B2
🔵 Đồng bộ 3 ảnh
```

---

# 99. Tự sinh task

Có thể tạo task từ:

```text
AI result
sensor threshold
location alert
scheduled inspection
```

Nhưng task phải có nguồn:

```text
source_type
source_id
```

---

# 100. Không biến cảnh báo thành spam

Có:

```text
severity
priority
cooldown
acknowledged
resolved
```

---

# 101. Tìm kiếm và truy xuất

Các index database:

```text
user_id
field_id
season_id
inspection_time
disease_id
ai_status
starred
latitude
longitude
updated_at
```

Để lịch sử lớn vẫn truy xuất nhanh.

---

# 102. Pagination

Không tải toàn bộ lịch sử khi có hàng nghìn record.

Dùng:

```text
limit
cursor
```

hoặc pagination.

---

# 103. Thumbnail

Danh sách Nhật ký chỉ tải:

```text
thumbnail
```

Chỉ tải preview lớn khi mở chi tiết.

Giảm data mobile.

---

# 104. Image compression

Trước upload:

```text
original
thumbnail
preview
```

không tải ảnh khổng lồ nếu không cần.

Nhưng original nếu người dùng chọn lưu phải giữ nguyên/hoặc lưu phiên bản chất lượng phù hợp theo cấu hình.

---

# 105. Realtime không gửi ảnh qua event

Realtime chỉ gửi:

```text
record metadata
```

Ảnh lấy từ Storage.

Không broadcast base64 ảnh qua WebSocket/Supabase.

---

# 106. Security RLS

Supabase phải có Row Level Security.

User chỉ được:

```text
SELECT/INSERT/UPDATE
```

dữ liệu của chính mình theo quyền.

Admin dùng role riêng.

---

# 107. Production CORS

Server hiện đang dùng:

```text
allow_origins=["*"]
```

Phải chuyển production sang origin thực.

---

# 108. Production URL

```text
https://ai.nongnghiepsangtao.io.vn/
```

Frontend:

```text
same-origin
```

API:

```text
/api/...
```

WebSocket:

```text
wss://ai.nongnghiepsangtao.io.vn/ws
```

---

# 109. Không localhost production

Frontend không được chứa:

```text
localhost
127.0.0.1
ws://
http://
```

trừ URL nội bộ thật sự không xuất hiện tới người dùng.

---

# 110. Cloudflare

Cloudflare Tunnel tiếp tục làm lớp public ingress.

Nội bộ có thể:

```text
127.0.0.1:5000
```

nhưng frontend không biết địa chỉ này.

---

# 111. Health dashboard

Cài đặt/diagnostic:

```text
AI Server
Cloud
GPS
Storage
Sync
WebSocket
```

cho người dùng kỹ thuật.

Không làm người dùng bình thường bị ngợp.

---

# 112. Cửa sổ chẩn đoán

Trong Cài đặt:

```text
Trạng thái hệ thống

🌐 Internet       🟢
🤖 AI Server      🟢
☁️ Cloud          🟢
📍 GPS            🟢
🔌 WebSocket      🟢
💾 Local DB       🟢
🔄 Sync Queue     0
```

---

# 113. User mode

### Người dùng bình thường

Chỉ thấy:

```text
AI
GPS
Cloud
```

### Chế độ kỹ thuật

Thấy:

```text
latency
last sync
last AI health
queue
model version
device
```

---

# 114. Model version

Mỗi AI result phải lưu:

```text
model_name
model_version
confidence_threshold
image_size
device
```

Để sau này biết kết quả được tạo bởi model nào.

---

# 115. Audit AI

Khi model thay đổi:

```text
best02.pt
→ best03.pt
```

không được làm mất lịch sử.

Lịch sử vẫn biết:

```text
result này do best02 tạo
```

---

# 116. Test matrix

## Server

- AI online.
- AI offline.
- AI restart.
- AI busy.
- AI error.

## Cloud

- online.
- offline.
- reconnect.
- conflict.

## GPS

- permission granted.
- denied.
- poor accuracy.
- moving.
- stationary.

## Network

- Wi-Fi.
- 4G.
- weak network.
- disconnected.
- reconnect.

## Browser

- Android Chrome.
- iPhone Safari.
- desktop Chrome/Edge.

---

# 117. Test offline

Bắt buộc:

```text
Tắt AI server
→ app vẫn mở
→ map
→ GPS
→ alert
→ history
```

Sau đó:

```text
bật AI server
→ health online
→ pending job
→ phân tích
```

---

# 118. Test mất Internet

```text
tắt Internet
→ app shell vẫn mở
→ IndexedDB vẫn đọc
→ knowledge vẫn đọc
→ locations vẫn đọc
→ alert vẫn chạy nếu GPS còn dữ liệu
```

Không tuyên bố map tiles online vẫn hoạt động nếu chưa cache tile.

---

# 119. Test sync

```text
offline
→ tạo inspection
→ pending

online
→ sync

Supabase
→ record tồn tại

reload
→ record vẫn tồn tại
```

---

# 120. Test realtime

Thiết bị A:

```text
tạo inspection
```

Thiết bị B:

```text
nhận thay đổi
```

Không reload.

---

# 121. Test bệnh

Mở:

```text
Kiến thức
```

Không cần AI server.

Tìm:

```text
đạo ôn
khô vằn
bạc lá
đốm nâu
```

phải hoạt động từ local knowledge cache.

---

# 122. Test cảnh báo

Không cần AI server.

Đi vào:

```text
radius_m
```

→ cảnh báo.

---

# 123. Test ảnh

AI online:

```text
original
preview
thumbnail
```

được lưu.

AI offline:

```text
original local
pending
```

AI online lại:

```text
analyze
preview
sync
```

---

# 124. Test dữ liệu cũ

Không xóa:

```text
localStorage
Supabase inspections
SQLite history
original
preview
```

Phải có migration.

---

# 125. Migration

Chuyển dữ liệu prototype:

```text
data[]
```

vào IndexedDB.

Chuyển Supabase `inspections` cũ vào schema mới.

Không duplicate bằng:

```text
legacy_id
job_id
```

---

# 126. Dữ liệu server hiện tại

Storage hiện đang tách theo user:

```text
data/{user}/original
data/{user}/preview
data/{user}/result
```

và history SQLite theo user. Giữ để migration/backup, nhưng lớp dữ liệu mới phải có một `StorageRepository` để UI không phụ thuộc trực tiếp filesystem. fileciteturn7file0L1-L10 fileciteturn7file5L1-L10

---

# 127. Repository pattern

Frontend:

```text
Repository
 ├── LocalRepository
 ├── SupabaseRepository
 └── SyncRepository
```

UI không gọi trực tiếp:

```text
supabase.from(...)
```

ở khắp nơi.

---

# 128. Service architecture frontend

```text
App
 ├── MapService
 ├── GPSService
 ├── AlertService
 ├── AIService
 ├── StorageService
 ├── SyncService
 ├── RealtimeService
 ├── KnowledgeService
 ├── NotificationService
 └── UIController
```

Tất cả nằm trong cùng nền tảng V3, không phải các app riêng.

---

# 129. Data flow chuẩn

```text
UI
 ↓
Service
 ↓
Repository
 ↓
IndexedDB
 ↓
Sync Queue
 ↓
Supabase
```

AI:

```text
UI
 ↓
AIService
 ↓
AI Server
 ↓
YOLO
 ↓
AI result
 ↓
Repository
 ↓
Local + Cloud
```

---

# 130. Không để UI biết implementation

Ví dụ không:

```js
button.onclick = () =>
  supabase.from("inspections")...
```

Mà:

```js
await InspectionService.create(...)
```

---

# 131. Điều này giúp hệ thống linh hoạt

Khi Supabase đổi:

```text
UI không đổi
```

Khi AI server đổi:

```text
UI không đổi
```

Khi sau này có AI local:

```text
AIService thêm provider
```

không phải viết lại app.

---

# 132. Chuẩn bị AI local trong tương lai

Kiến trúc:

```text
AIService
 ├── YOLOServerProvider
 ├── PlantNetProvider
 └── LocalModelProvider
```

Hiện tại:

```text
YOLOServerProvider
```

là chính.

Sau này có thể thêm model chạy trên điện thoại.

Điều này phù hợp với khoảng trống nghiên cứu mà tài liệu đề tài đã xác định: nhiều hệ thống phụ thuộc server và cần hướng offline/mobile; tài liệu cũng nêu các nghiên cứu đã chứng minh khả năng chạy mô hình trên smartphone. fileciteturn6file1L1-L8 fileciteturn6file3L1-L8

---

# 133. Ưu tiên AI

Production:

```text
1. Cây Lúa YOLO Server
2. Nếu người dùng chủ động chọn provider khác → provider đó
3. Không tự mock
```

---

# 134. UX khi server offline

Không khóa nút kiểm tra.

Nút:

```text
📷 Kiểm tra ruộng
```

vẫn hoạt động.

Sau ảnh:

```text
🟡 Đã lưu ảnh
🤖 AI đang offline
```

---

# 135. Realtime UI

Header:

```text
🌾 AI Rice

📍 GPS ●
🤖 AI ●
☁️ Cloud ●
```

Chấm màu có chữ đi kèm.

---

# 136. Toast thông minh

Ví dụ:

```text
🟢 Đã lưu cục bộ
🟡 Đang chờ đồng bộ
🟢 Đã đồng bộ
🔴 AI server offline
🟢 AI server đã trở lại
```

---

# 137. Notification

Nếu người dùng cho phép:

```text
Bạn đang gần Ruộng A3
```

Nhưng không được phụ thuộc hoàn toàn vào push/background geolocation trên web vì hỗ trợ trình duyệt khác nhau.

---

# 138. GPS privacy

GPS chỉ xin khi cần.

Hiển thị rõ:

```text
Cho phép sử dụng vị trí để:
• theo dõi vị trí của bạn trên bản đồ
• cảnh báo khi đến gần ruộng
```

Geolocation trên web yêu cầu HTTPS và quyền người dùng; chính sách Permissions-Policy cũng có thể ảnh hưởng quyền này. citeturn0search2turn0search8

---

# 139. Không lưu GPS quá mức

Không lưu mọi GPS tick vào cloud.

Mặc định:

```text
GPS realtime → local memory
```

Chỉ lưu:

```text
inspection location
alert event cần thiết
field location
```

Nếu cần track đường đi thì phải có tính năng riêng và người dùng chủ động bật.

---

# 140. Map performance

Không re-render toàn bộ marker mỗi lần GPS đổi.

Chỉ:

```text
userMarker.setLatLng(...)
```

và khi cần:

```text
map.panTo(...)
```

---

# 141. History performance

Không gọi:

```text
render()
```

toàn bộ map mỗi khi sửa một record.

Tách:

```text
renderHistory()
renderMap()
renderPanel()
```

---

# 142. Đây là lỗi kiến trúc cần sửa

Prototype hiện đang có:

```js
render()
```

vừa:

- xóa marker;
- tạo marker;
- lọc data;
- render list.

Khi dữ liệu lớn sẽ không linh hoạt.

Tách thành:

```text
renderMapMarkers()
renderHistoryList()
renderOverview()
```

---

# 143. Map data cache

Chỉ tải:

```text
rice_locations
recent disease status
```

không tải toàn bộ ảnh.

---

# 144. Progressive loading

Mở app:

```text
1. app shell
2. local data
3. map
4. GPS
5. recent records
6. cloud sync
7. realtime
```

---

# 145. Ưu tiên trải nghiệm

Nếu mạng chậm:

```text
người dùng vẫn thấy dữ liệu local ngay
```

không chờ spinner 10 giây.

---

# 146. Offline-first nhưng không giả dữ liệu

Không bao giờ:

```text
offline
→ dùng dữ liệu giả
```

Phải:

```text
offline
→ dữ liệu cache thật
```

Nếu chưa có:

```text
Chưa có dữ liệu
```

---

# 147. Realtime nhưng không phụ thuộc realtime

Realtime mất:

```text
local data vẫn hoạt động
```

Khi realtime trở lại:

```text
resync
```

---

# 148. AI realtime nhưng không phụ thuộc WebSocket

WebSocket mất:

```text
poll job status
```

nếu cần.

Không để WebSocket chết làm mất kết quả AI.

---

# 149. Job recovery

Nếu browser đóng khi AI đang xử lý:

```text
job_id
```

được lưu local.

Khi mở lại:

```text
check job
```

và lấy kết quả nếu server còn.

---

# 150. Server restart recovery

AI server restart:

```text
job incomplete
```

phải có trạng thái:

```text
failed/retry
```

không mất record inspection.

---

# 151. Data retention

Cần cấu hình:

```text
ảnh gốc
preview
log
sensor
```

theo thời gian.

Không tự xóa ảnh người dùng nếu chưa có chính sách.

---

# 152. Backup

Server hiện có filesystem theo user.

Phải có:

```text
backup
restore
```

cho:

```text
database
model
storage metadata
```

---

# 153. Observability

Server:

```text
health
latency
jobs
errors
GPU
CPU
RAM
storage
```

Frontend:

```text
AI latency
sync queue
offline time
GPS accuracy
```

---

# 154. Admin

Admin có dashboard:

```text
Users
Fields
Inspections
AI jobs
Storage
Errors
Sensors
```

---

# 155. Không để admin ảnh hưởng user

AI worker phải có queue giới hạn.

Một user spam upload không được làm treo toàn server.

---

# 156. AI queue

```text
queued
processing
completed
failed
```

Có:

```text
priority
created_at
user_id
```

---

# 157. Quota

Auth hiện có quota/used trong SQLite. Giữ tương thích, nhưng sau này đưa quota cloud vào repository thống nhất. fileciteturn7file4L1-L10

Không trừ quota khi:

```text
AI server offline
```

nếu chưa thực sự chạy AI.

---

# 158. Khi retry

Nếu job thất bại do server:

```text
không tính thành công
```

Quota chỉ tính theo policy rõ ràng.

---

# 159. Kiến thức bệnh realtime

Knowledge không cần realtime từng giây.

Dùng:

```text
version
updated_at
```

và sync khi có bản mới.

---

# 160. Disease source validation

Mỗi knowledge record phải có:

```text
source
reviewed_by
review_date
```

Nếu chưa kiểm duyệt:

```text
Dự thảo
```

---

# 161. Nguồn tham khảo hiện tại

IRRI có tài liệu chẩn đoán bệnh lúa, gồm bạc lá, sọc lá vi khuẩn và nhiều bệnh khác; tài liệu khô vằn cung cấp triệu chứng/điều kiện/biện pháp quản lý. citeturn2search16turn2search0

Không sao chép nguyên văn tài liệu nguồn vào app; xây dữ liệu có cấu trúc và ghi nguồn.

---

# 162. Giao diện bệnh

Khi mở bệnh:

```text
📚 Bệnh đạo ôn

Nhận diện hình ảnh
Triệu chứng
Điều kiện thuận lợi
Bộ phận bị ảnh hưởng
Chẩn đoán phân biệt
Quản lý
Nguồn tham khảo
Cập nhật
```

---

# 163. Disease confidence history

Không chỉ hiển thị confidence hiện tại.

Cho xem:

```text
82%
91%
76%
```

theo thời gian.

---

# 164. Ruộng health timeline

Tổng hợp:

```text
AI
Sensor
Inspection
Alert
Task
```

trên cùng timeline.

---

# 165. Một cửa sổ “Tổng quan ruộng”

Đây là cửa sổ quan trọng nhất.

```text
🌾 Ruộng A3

Trạng thái: 🔴 Cần kiểm tra

📍 Ấp...
🌱 54 ngày
🌿 Làm đòng

🤖 AI gần nhất
Đạo ôn 91%

🌡 29°C
💧 82%
pH 5.6
EC ...

📜 Lịch sử
3 lần kiểm tra

🔔 Cảnh báo
Có ghi nhận bệnh gần đây

[Kiểm tra]
[Nhật ký]
[Kiến thức]
```

---

# 166. Cửa sổ “Kiểm tra nhanh”

Từ map:

```text
📷 Kiểm tra ruộng
```

tự lấy:

```text
GPS
ruộng
vụ
tuổi lúa
```

người dùng chỉ cần:

```text
chụp
→ gửi
```

---

# 167. Không bắt nhập lại dữ liệu

Nếu user đang đứng gần ruộng:

```text
field_id tự nhận diện
```

và:

```text
season
growth stage
```

lấy từ record hiện tại.

Người dùng vẫn có thể sửa.

---

# 168. Cửa sổ “Dữ liệu”

Có:

```text
Tổng record
Đã sync
Chờ sync
Lỗi sync
Ảnh
Dung lượng
```

---

# 169. Cửa sổ “Hệ thống”

Có:

```text
AI
Cloud
GPS
WebSocket
Storage
Sync
```

---

# 170. Chế độ tự động

Mặc định:

```text
Map Auto-follow = ON
AI = AUTO
Sync = AUTO
Realtime = AUTO
```

Nhưng AI AUTO không được mock.

---

# 171. Người dùng có thể tắt

Cài đặt:

```text
Auto-follow
Cảnh báo gần ruộng
Realtime
Auto-sync
AI auto
```

---

# 172. Khi pin yếu

Không chạy GPS quá dày.

Có:

```text
GPS profile:
Eco
Balanced
Precise
```

Mặc định:

```text
Balanced
```

---

# 173. GPS movement filter

Không update map nếu di chuyển quá nhỏ.

Ví dụ logic:

```text
distance < threshold
→ không pan
```

nhưng vẫn có thể cập nhật vị trí nội bộ.

---

# 174. Alert distance

Có thể cảnh báo theo:

```text
50m
100m
200m
500m
```

hoặc từng ruộng.

---

# 175. Sensor thresholds

Không hard-code.

Bảng:

```text
alert_rules
```

với:

```text
field_id
metric
operator
threshold
severity
enabled
```

---

# 176. Sensor + AI

Ví dụ:

```text
AI: khô vằn 80%
+
ẩm độ cao
+
tán rậm
```

→ tạo:

```text
Cần theo dõi
```

Không tự khẳng định bệnh do sensor.

---

# 177. Time series

Sensor lưu:

```text
timestamp
```

và truy xuất theo:

```text
1h
24h
7d
30d
```

---

# 178. Data compression

Sensor không cần ghi quá dày nếu không cần.

Có thể:

```text
raw
→ aggregate
```

theo phút/5 phút.

---

# 179. Realtime sensor UI

Khi có record mới:

```text
chart update
```

không reload.

---

# 180. User notification center

Thêm biểu tượng:

```text
🔔
```

Hiển thị:

```text
AI đã online
Bạn đang gần Ruộng A3
Có kết quả AI mới
3 dữ liệu đang chờ đồng bộ
Sensor mất kết nối
```

---

# 181. Notification history

Lưu:

```text
notifications
```

để không mất thông báo.

---

# 182. Không gửi quá nhiều notification

Có:

```text
priority
cooldown
read
```

---

# 183. Search global

Thanh tìm kiếm V3:

```text
ruộng
bệnh
ấp
xã
tỉnh
job
```

---

# 184. Voice assistant — chuẩn bị kiến trúc

Không cần triển khai ngay.

Nhưng có thể thêm:

```text
AssistantService
```

sau này:

```text
"Ruộng A3 hôm nay thế nào?"
```

→ đọc dữ liệu local/cloud.

---

# 185. AI tư vấn — không trộn với YOLO

Tách:

```text
Vision AI
Knowledge AI
Assistant AI
```

Vision:

```text
ảnh → detection
```

Knowledge:

```text
bệnh → thông tin
```

Assistant:

```text
người dùng → hỏi đáp
```

---

# 186. Dữ liệu cảm biến + bệnh

Không để LLM tự bịa.

Assistant chỉ truy xuất:

```text
knowledge
inspection
sensor
field
```

---

# 187. Future expert support

Kiến trúc có thể thêm:

```text
expert_requests
expert_answers
```

để người dùng gửi ảnh/kết quả cho chuyên gia.

Đây cũng phù hợp với khoảng trống mà tài liệu đề tài nêu về kết nối chuyên gia từ xa và tích hợp AI/IoT. fileciteturn6file1L1-L8

---

# 188. Ưu tiên triển khai

## P0 — Bắt buộc

1. V3 vẫn là nền tảng.
2. IndexedDB.
3. Local-first.
4. Sync queue.
5. AI optional.
6. GPS realtime.
7. Auto-follow.
8. Alert engine.
9. History migration.
10. Preview YOLO.
11. Production domain.
12. Health check.
13. Reconnect.
14. Supabase schema/RLS.

## P1

15. Realtime Supabase.
16. Sensor.
17. Timeline.
18. Dashboard.
19. PWA.
20. Notification center.

## P2

21. AI local.
22. Voice.
23. Expert support.

---

# 189. Không làm P2 trước P0

Không thêm chatbot/voice nếu:

```text
history chưa ổn
sync chưa ổn
AI offline chưa ổn
GPS chưa ổn
```

---

# 190. Tiêu chí “hoàn thành lần cải tiến”

### Nền tảng

- [ ] V3 vẫn là UI chính.
- [ ] Không viết frontend thay thế.
- [ ] Không mất map.
- [ ] Không mất popup.
- [ ] Không mất tabs.

### Offline

- [ ] App mở khi AI offline.
- [ ] IndexedDB hoạt động.
- [ ] History đọc local.
- [ ] Knowledge đọc local.
- [ ] Locations đọc local.
- [ ] Sync queue hoạt động.

### AI

- [ ] Health.
- [ ] Online/offline.
- [ ] YOLO.
- [ ] bbox.
- [ ] preview.
- [ ] pending.
- [ ] retry.
- [ ] job recovery.
- [ ] không mock production.

### GPS

- [ ] watchPosition.
- [ ] marker.
- [ ] auto-follow.
- [ ] pause khi kéo.
- [ ] return-to-me.
- [ ] accuracy.

### Alert

- [ ] near field.
- [ ] cooldown.
- [ ] history.
- [ ] sensor-ready.

### Data

- [ ] fields.
- [ ] seasons.
- [ ] locations.
- [ ] inspections.
- [ ] images.
- [ai_results.
- [ ] sensor.
- [ ] tasks.
- [ ] knowledge.
- [ ] sync audit.

### Realtime

- [ ] Supabase.
- [ ] reconnect.
- [ ] local fallback.

### Production

- [ ] HTTPS.
- [ ] WSS.
- [ ] no localhost frontend.
- [ ] CORS restricted.
- [ ] RLS.
- [ ] signed/private image access.

---

# 191. Lệnh MASTER cho OpenCode

```text
ĐÂY LÀ YÊU CẦU TÁI CẤU TRÚC TỔNG THỂ.

NỀN TẢNG DUY NHẤT:
AI_Rice_UX_Prototype_V3_CLICK_POPUP_FINAL.html

KHÔNG viết frontend mới.
KHÔNG thay UI V3.
KHÔNG xóa chức năng cũ.

Hãy đọc toàn bộ:
- camera.html / UX V3
- server.py
- auth_simple.py
- storage_user.py
- history_log.py
- GUI
- config
- test
- project tree
- các tài liệu đề tài Cây Lúa

Sau đó thực hiện MỘT LẦN tái cấu trúc có hệ thống.

MỤC TIÊU:

1. OFFLINE-FIRST
2. AI SERVER OPTIONAL
3. LOCAL DATA + CLOUD DATA
4. REALTIME
5. GPS REALTIME
6. AUTO-FOLLOW
7. ALERT ENGINE
8. HISTORY
9. KNOWLEDGE ENGINE
10. SENSOR READY
11. PRODUCTION DOMAIN

BẮT BUỘC:

A. UI V3
- giữ nguyên giao diện;
- giữ Leaflet;
- giữ tabs;
- giữ popup;
- giữ camera;
- giữ upload;
- giữ Supabase;
- giữ DISEASES.

B. LOCAL-FIRST
- tạo IndexedDB;
- local repository;
- sync queue;
- không dùng localStorage làm database chính;
- migration data[] cũ;
- không mất dữ liệu.

C. SYNC
- LocalRepository;
- SupabaseRepository;
- SyncService;
- retry;
- conflict;
- synced/pending/error.

D. AI
- AIService;
- YOLO server là provider chính;
- health;
- reconnect;
- job state;
- pending;
- retry;
- preview bbox;
- model version;
- KHÔNG mock production.

E. GPS
- watchPosition;
- marker user;
- auto-follow;
- pause follow khi kéo map;
- return-to-me;
- accuracy.

F. ALERT
- rice_locations;
- radius;
- distance client-side;
- near-field;
- cooldown;
- alert history;
- không spam.

G. DATABASE
Tạo/chuẩn hóa:
profiles
fields
seasons
rice_locations
inspections
inspection_images
ai_results
sensor_readings
tasks
alerts
alert_events
knowledge_articles
sync_audit

H. STORAGE
- original;
- preview;
- thumbnail;
- Supabase Storage;
- resumable upload khi phù hợp;
- không base64 DB.

I. REALTIME
- AI WebSocket cho AI job;
- Supabase Realtime cho database changes;
- reconnect;
- local fallback.

J. KNOWLEDGE
- DISEASES chuyển thành knowledge repository;
- có source;
- version;
- updated_at;
- symptoms;
- differential;
- management;
- ai_visual_features;
- không tự bịa khuyến cáo.

K. SENSOR
- nhiệt độ;
- độ ẩm;
- pH;
- EC;
- timestamp;
- field_id;
- realtime-ready.

L. UI
- AI status;
- GPS status;
- Cloud status;
- Sync status;
- offline banner;
- notification center;
- quick actions;
- context panel;
- timeline;
- filters;
- sort;
- search.

M. PERFORMANCE
- không render toàn bộ app khi GPS đổi;
- không render toàn bộ map khi một record đổi;
- thumbnail cho list;
- preview khi mở;
- pagination;
- indexes.

N. SECURITY
- production CORS;
- RLS;
- không service role key frontend;
- không access key dài hạn trong preview URL;
- signed URL/authenticated image access.

O. PRODUCTION
domain:
https://ai.nongnghiepsangtao.io.vn/

API:
same-origin /api/...

WS:
wss://ai.nongnghiepsangtao.io.vn/ws

Không hard-code localhost trong production frontend.

P. PWA
- manifest;
- service worker;
- app shell cache;
- knowledge cache;
- offline fallback;
- update version.

Q. TEST
Phải test:
1. AI online
2. AI offline
3. AI restart
4. Internet offline
5. Internet reconnect
6. GPS granted
7. GPS denied
8. GPS poor accuracy
9. auto-follow
10. map drag
11. near-field alert
12. alert cooldown
13. local save
14. cloud sync
15. realtime
16. history migration
17. preview
18. bbox
19. mobile
20. production domain

QUAN TRỌNG:

Không được chỉ tạo kế hoạch.

PHẢI:
- sửa code;
- tạo module;
- migrate schema;
- test;
- tự sửa lỗi.

Nhưng không được viết lại V3.

Cuối cùng xuất báo cáo:
1. kiến trúc mới;
2. file đã sửa;
3. file mới;
4. database schema;
5. migration;
6. offline behavior;
7. AI online/offline behavior;
8. GPS behavior;
9. alert behavior;
10. realtime behavior;
11. production deployment;
12. test result;
13. lỗi còn lại.

Nếu một chức năng chưa thể triển khai an toàn, đánh dấu rõ `TODO`, không giả vờ hoàn thành.
```

---

# 192. Kết luận

Đây không nên được coi là “thêm vài tính năng”.

Đây là bước chuyển V3 từ:

```text
Prototype giao diện
```

thành:

```text
Field-ready platform
```

với nguyên tắc:

```text
                    V3
                     │
       ┌─────────────┼─────────────┐
       ▼             ▼             ▼
     LOCAL          CLOUD          AI
       │             │             │
   IndexedDB      Supabase       YOLO
       │             │             │
       └─────────────┼─────────────┘
                     ▼
              SYNC / REALTIME
                     │
       ┌─────────────┼─────────────┐
       ▼             ▼             ▼
      MAP           GPS           ALERT
       │             │             │
       └─────────────┼─────────────┘
                     ▼
                 NHẬT KÝ
                     │
                     ▼
                KIẾN THỨC
```

**Kết quả mong muốn:** server AI có thể tắt mà người dùng vẫn dùng được Cây Lúa; mạng chập chờn không làm mất dữ liệu; khi server/cloud trở lại thì dữ liệu tự đồng bộ; khi AI hoạt động thì kết quả YOLO nhập lại đúng vào lịch sử/bản đồ/timeline.

Đây cũng phù hợp với chính khoảng trống mà hồ sơ đề tài đã xác định: cần ứng dụng thân thiện, có khả năng offline, lưu lịch sử ảnh, theo dõi tiến triển, tích hợp IoT và hỗ trợ dữ liệu thực địa Việt Nam. fileciteturn6file1L1-L8
