# AI RICE / CÂY LÚA — KẾ HOẠCH TÍCH HỢP TRÊN NỀN TẢNG UX V3

## 1. Quyết định kiến trúc

**Nền tảng gốc duy nhất là:**

`AI_Rice_UX_Prototype_V3_CLICK_POPUP_FINAL.html`

Không được thay giao diện này bằng một app khác.

Không được xây một frontend mới song song rồi bỏ giao diện hiện tại.

Tất cả tính năng mới phải được **tích hợp vào cấu trúc UX V3 hiện có**.

File hiện tại đã có sẵn:

- bố cục sidebar + bản đồ;
- Nhật ký;
- Việc cần làm;
- Phân tích;
- Kiến thức;
- Dữ liệu;
- Leaflet;
- popup chi tiết;
- chọn vị trí trên bản đồ;
- marker kéo được;
- camera;
- upload ảnh;
- tuổi lúa;
- giai đoạn;
- ghi chú;
- AI Adapter;
- chế độ AI AUTO/Server/PlantNet/Local;
- Supabase;
- danh mục bệnh;
- khuyến cáo;
- chẩn đoán phân biệt;
- cỡ chữ;
- responsive mobile.

Các thành phần này phải được **giữ lại và nâng cấp**, không được xóa chỉ để làm kiến trúc mới.

Nguồn kiểm tra trực tiếp: file UX V3 hiện có cấu trúc tab `Nhật ký / Việc cần làm / Phân tích / Kiến thức / Dữ liệu`, bản đồ Leaflet, camera/upload và AI Adapter. fileciteturn5file0

---

# 2. Những gì đã có và phải giữ

## Giao diện

Giữ:

```text
🌾 AI Rice
Bản đồ sức khỏe ruộng lúa

🔍 Tìm ruộng, bệnh...
🗺️ Map
⚙️ Cài đặt

📋 Nhật ký
🎯 Việc cần làm
📊 Phân tích
📚 Kiến thức
🗄️ Dữ liệu
```

Không đổi layout nếu không cần.

---

# 3. Bản đồ hiện tại là nền tảng

Bản đồ Leaflet hiện tại phải tiếp tục là bản đồ chính.

Đã có:

```js
const map=L.map('map')
```

và layer:

- bản đồ đường;
- ảnh vệ tinh.

Giữ:

```text
🛣️
🛰️
📍
```

và thêm chức năng GPS/Auto-follow vào chính bản đồ này.

Không thay Leaflet bằng hệ thống bản đồ khác trừ khi có lý do kỹ thuật rõ ràng.

---

# 4. Tích hợp GPS vào bản đồ hiện tại

Hiện tại UX V3 đã có:

```js
locate()
```

nhưng đang dùng:

```js
navigator.geolocation.getCurrentPosition()
```

Chuyển thành cơ chế theo dõi liên tục:

```js
navigator.geolocation.watchPosition(...)
```

Tạo:

```js
GPSService
```

nhưng service này chỉ là module JS bên trong cùng file/app.

Không tạo app GPS riêng.

Dữ liệu:

```js
{
  lat,
  lng,
  accuracy,
  heading,
  speed,
  timestamp
}
```

---

# 5. Auto-follow

Tích hợp trực tiếp vào bản đồ hiện tại.

Nút:

```text
📍 Theo tôi
```

Có thể dùng nút `📍` hiện tại làm nút Auto-follow.

Trạng thái:

```text
📍 Theo tôi: ON
📍 Theo tôi: OFF
```

Khi ON:

```text
GPS thay đổi
→ marker người dùng cập nhật
→ map tự di chuyển theo người
```

Không cần AI server.

---

# 6. Không giành quyền khi người dùng kéo bản đồ

Khi Auto-follow đang bật:

```text
Người dùng kéo bản đồ
        ↓
tạm dừng Auto-follow
        ↓
hiện nút:
"↩ Theo vị trí của tôi"
```

Người dùng bấm nút:

```text
Auto-follow ON
→ map quay lại vị trí hiện tại
```

Không để bản đồ liên tục giật về GPS khi người dùng đang xem một vị trí khác.

---

# 7. Marker người dùng

Thêm marker riêng:

```text
🔵 Bạn
```

Không dùng chung marker với ruộng.

Ví dụ:

```text
🔵 Người dùng
🌾 Ruộng A
🌾 Ruộng B
🔴 Điểm có vấn đề
```

---

# 8. Vị trí ruộng/cây lúa

Tách dữ liệu vị trí khỏi dữ liệu kết quả AI.

Object:

```js
{
  id,
  name,
  lat,
  lng,
  ap,
  xa,
  tinh,
  radius_m,
  active
}
```

Ví dụ:

```js
{
  id: "field-A3",
  name: "Ruộng A3",
  lat: 10.052,
  lng: 105.735,
  ap: "Tân Hòa",
  xa: "Mỹ Khánh",
  tinh: "Cần Thơ",
  radius_m: 100,
  active: true
}
```

---

# 9. Cảnh báo đến gần ruộng

Chức năng này chạy **độc lập với AI server**.

Luồng:

```text
GPS người dùng
       ↓
tính khoảng cách
       ↓
Rice Locations
       ↓
distance <= radius_m
       ↓
🔔 Cảnh báo
```

Ví dụ:

```text
🌾 Bạn đang gần Ruộng A3

Khoảng cách: 72 m
Khu vực: Ấp Tân Hòa, Xã Mỹ Khánh, Cần Thơ

📷 Kiểm tra ruộng
```

---

# 10. Tính khoảng cách trên client

Không gọi FastAPI cho từng GPS update.

Dùng tính toán khoảng cách trên trình duyệt.

Ví dụ Haversine.

Điều này đảm bảo:

```text
AI Server OFF
→ cảnh báo vị trí vẫn hoạt động.
```

---

# 11. Chống cảnh báo lặp

Không cảnh báo mỗi lần GPS thay đổi.

Chỉ cảnh báo khi:

```text
ngoài vùng
   ↓
vào vùng
```

Có thể lưu:

```js
alertState
```

và thời gian nhắc lại.

Mặc định:

```text
Không spam.
```

---

# 12. GPS accuracy

Nếu:

```text
accuracy quá lớn
```

không được báo khoảng cách chính xác.

Ví dụ:

```text
GPS ±500 m
```

thì không được nói:

```text
Bạn cách ruộng 40 m
```

Thay bằng:

```text
⚠️ GPS chưa đủ chính xác để cảnh báo vị trí.
```

---

# 13. AI SERVER LÀ MODULE TÙY CHỌN

Nền tảng vẫn là UX V3.

AI server chỉ cung cấp:

```text
AIService
```

Không được để AI server là dependency bắt buộc để render app.

Luồng:

```text
Mở web
 ↓
UI
 ↓
Map
 ↓
GPS
 ↓
Alert
 ↓
sau đó kiểm tra AI
```

Không:

```text
chờ server AI
 ↓
mới mở app
```

---

# 14. Trạng thái AI

Thêm trên giao diện:

```text
🤖 AI: ONLINE
```

hoặc:

```text
🤖 AI: OFFLINE
```

Không được dùng trạng thái AI để khóa:

- map;
- GPS;
- alert;
- history;
- knowledge;
- data cục bộ.

---

# 15. Khi AI server ONLINE

Nút:

```text
📷 Kiểm tra ruộng
```

giữ nguyên.

Luồng:

```text
chụp/chọn ảnh
 ↓
chọn vị trí
 ↓
AI server
 ↓
FastAPI
 ↓
YOLOv8
 ↓
bbox
 ↓
preview ảnh detect
 ↓
kết quả
 ↓
Supabase/history
 ↓
bản đồ + Nhật ký
```

---

# 16. Khi AI server OFFLINE

Không được báo:

```text
Không phát hiện bệnh
```

Đó là sai.

Phải báo:

```text
🤖 Máy chủ AI hiện offline.

Ảnh đã được lưu vào danh sách chờ.
Bạn có thể phân tích lại khi máy chủ hoạt động.
```

Record:

```js
ai_status: "pending"
```

---

# 17. Không dùng Mock AI trong production

File hiện tại có:

```js
mockProvider
```

và AUTO hiện tại có fallback:

```text
Server
→ PlantNet
→ Mock
```

Đây là điểm phải sửa.

## Production

Không được tự động biến:

```text
AI Server offline
```

thành:

```text
Bệnh đạo ôn 91%
```

từ mock.

Mock chỉ được phép:

```text
development/test
```

và phải có cờ rõ ràng.

---

# 18. PlantNet

PlantNet hiện có trong prototype.

Không được coi PlantNet là YOLO Cây Lúa.

Nếu giữ:

```text
PlantNet
```

phải hiển thị rõ:

```text
Nguồn nhận diện: PlantNet
```

và không giả vờ đó là kết quả YOLO.

Trong production, ưu tiên:

```text
CAY LUA YOLOv8
```

Khi YOLO offline:

```text
AI offline / pending
```

trừ khi người dùng chủ động chọn một provider khác.

---

# 19. AI Adapter hiện tại

Giữ ý tưởng:

```js
analyzeRice(file, context)
```

nhưng sửa thành:

```text
AI Adapter
 ├── CAYLUA YOLO Server
 ├── PlantNet (tùy chọn)
 └── Mock (chỉ development)
```

AI Adapter phải trả:

```js
{
  status,
  provider,
  job_id,
  disease,
  confidence,
  preview_url,
  detections
}
```

---

# 20. Server URL

Prototype hiện đang có:

```js
baseUrl: "http://localhost:8000"
```

Đây chỉ được xem là development.

Production không được hard-code localhost.

Ưu tiên:

```js
/api/...
```

và:

```text
wss://ai.nongnghiepsangtao.io.vn/ws
```

Nếu FastAPI dùng cùng domain.

---

# 21. Production domain

Dùng:

```text
https://ai.nongnghiepsangtao.io.vn/
```

Đây là domain thật của hệ thống.

Không đổi nền tảng.

Cloudflare Tunnel/Reverse Proxy chỉ là hạ tầng phía sau.

---

# 22. YOLO preview

Khi server trả:

```text
preview_url
```

phải lưu URL này trong record.

Viewer phải mở chính ảnh đó.

Không lấy ảnh gốc rồi vẽ box giả ở frontend.

---

# 23. Nhật ký nâng cấp

Nền tảng hiện tại có `data`.

Nâng record thành:

```js
{
  id,
  db_id,
  job_id,

  field_name,
  custom_name,

  disease_id,
  disease_name,

  status_color,
  ai_status,

  confidence,

  age_days,
  growth_stage,

  latitude,
  longitude,

  ap,
  xa,
  tinh,

  location_source,

  preview_url,
  original_url,

  ai_provider,

  starred,

  created_at
}
```

---

# 24. Tên người dùng

Cho phép sửa:

```text
Tên ruộng / tên lần kiểm tra
```

Ví dụ:

```text
Ruộng A3 - Hè Thu
```

Không xóa `field_name` cũ.

---

# 25. Địa chỉ

Hiển thị:

```text
Ấp
Xã
Tỉnh/Thành phố
```

trong popup và Nhật ký.

Không tự đoán địa chỉ nếu chưa có dữ liệu.

---

# 26. Sao

Thêm:

```text
☆ / ⭐
```

Vào card Nhật ký.

Record starred đứng đầu.

---

# 27. Sort

Thêm thanh:

```text
Sắp xếp:
[ Mới nhất ▼ ]
```

Các lựa chọn:

```text
Mới nhất
Cũ nhất
Tên A-Z
Confidence cao nhất
Nhiều vùng bệnh nhất
```

Starred luôn ưu tiên trước.

---

# 28. Ảnh trong Nhật ký

Prototype hiện đang dùng:

```html
<div class="thumb">🌾</div>
```

Phải thay bằng thumbnail thật nếu record có:

```text
preview_url
```

Ví dụ:

```html
<img src="preview_url">
```

Nếu chưa có ảnh:

```text
🌾
```

---

# 29. Popup chi tiết

Giữ panel:

```text
#panel
```

Nhưng bổ sung:

```text
ảnh detect
tên
bệnh
confidence
AI status
vị trí
Ấp/Xã/Tỉnh
GPS
thời gian
⭐
```

Nếu có bệnh:

```text
Khuyến cáo
Chẩn đoán phân biệt
Đặc trưng hình ảnh
```

vẫn giữ nguyên.

---

# 30. Tab Kiến thức

Giữ nguyên `DISEASES`.

Không xóa dữ liệu bệnh hiện tại.

Tiếp tục dùng:

```text
name_vi
name_en
group
causal_agent
symptoms
favorable_conditions
management
differential
ai_visual_features
```

Đây là nguồn kiến thức trực tiếp của UX V3.

---

# 31. Tab Phân tích

Giữ tab hiện tại.

Nhưng số liệu phải dần lấy từ dữ liệu thật:

```text
inspections
ai_results
rice_locations
```

Không để số liệu demo cố định:

```text
156
98
21
```

khi chuyển production.

---

# 32. Tab Dữ liệu

Giữ.

Dùng để hiển thị tình trạng:

```text
inspection records
ảnh
hồ sơ bệnh
AI status
sync status
```

Có thể thêm:

```text
🟢 Cloud synced
🟡 Pending sync
🔴 Sync error
```

---

# 33. Supabase

Prototype đã khởi tạo Supabase và bảng:

```text
inspections
```

Tiếp tục sử dụng nền tảng này.

Nhưng phải mở rộng schema để lưu:

```text
profiles
fields
rice_locations
seasons
inspections
inspection_images
ai_results
alerts
```

Không lưu ảnh base64 trong database.

Ảnh nên lưu Storage.

---

# 34. Đồng bộ offline

Đề xuất:

```text
Browser
 ↓
Local cache
 ↓
Supabase
```

Khi có mạng:

```text
sync
```

Khi mất mạng:

```text
local queue
```

AI server offline không đồng nghĩa Supabase offline.

Đây là hai trạng thái khác nhau.

---

# 35. Ba trạng thái cần tách

Không dùng một biến `online`.

Phải có:

```text
APP
GPS
AI
CLOUD
```

Ví dụ:

```text
🟢 APP
🟢 GPS
🔴 AI
🟢 CLOUD
```

hoặc:

```text
🟢 APP
🟢 GPS
🟢 AI
🔴 CLOUD
```

Trong trường hợp thứ hai:

- AI vẫn có thể phân tích;
- record phải lưu local;
- sync cloud sau.

---

# 36. Luồng hoàn chỉnh

## Người dùng đi ngoài ruộng

```text
Mở:
https://ai.nongnghiepsangtao.io.vn/

↓
Map mở ngay

↓
GPS xin quyền

↓
🔵 marker người dùng

↓
Auto-follow

↓
đi gần Ruộng A3

↓
🔔 cảnh báo

"Bạn đang gần Ruộng A3 - 72m"

↓
bấm:
📷 Kiểm tra ruộng

↓
chụp ảnh

↓
AI ONLINE?

Có:
  ↓
  YOLO

Không:
  ↓
  lưu pending
```

---

# 37. Nếu AI server chết

Ứng dụng vẫn phải:

```text
mở được
map được
GPS được
follow được
cảnh báo được
xem lịch sử được
xem kiến thức được
xem dữ liệu cục bộ được
```

Chỉ:

```text
AI = OFFLINE
```

---

# 38. Nếu AI server bật lại

Không tự ý chạy toàn bộ ảnh pending ngay nếu có thể gây tải lớn.

Hiển thị:

```text
🤖 AI đã kết nối

3 ảnh đang chờ phân tích

[Phân tích tất cả]
```

Người dùng quyết định.

---

# 39. PWA

Có thể bổ sung:

```text
manifest.json
service-worker.js
```

nhưng phải tích hợp vào UX V3.

Không xây PWA thành frontend mới.

Cache:

- HTML;
- CSS;
- JS;
- disease knowledge;
- cấu hình UI;
- dữ liệu vị trí cần thiết.

---

# 40. Responsive

Giữ responsive hiện tại:

```css
@media(max-width:850px)
```

Không phá layout điện thoại.

Đặc biệt:

- nút Kiểm tra ruộng;
- panel;
- bottom sheet;
- GPS;
- Auto-follow;
- Nhật ký.

---

# 41. Quy tắc không phá nền tảng

OpenCode tuyệt đối không:

- viết lại UI từ đầu;
- thay Leaflet nếu không cần;
- xóa tab;
- xóa DISEASES;
- xóa Supabase;
- xóa popup;
- xóa map;
- xóa camera;
- xóa upload;
- xóa AI Adapter;
- xóa PlantNet;
- xóa các field hiện tại;
- xóa dữ liệu hiện tại.

Chỉ refactor khi cần để tích hợp chức năng.

---

# 42. Những phần cần sửa ngay trong file nền tảng

### A. `server.baseUrl`

Hiện:

```text
http://localhost:8000
```

→ production dùng relative API/domain thật.

### B. `mockProvider`

→ chỉ development/test.

### C. `getCurrentPosition`

→ chuyển sang `watchPosition`.

### D. `locate()`

→ trở thành Auto-follow controller.

### E. `data`

→ nâng thành history schema đầy đủ.

### F. thumbnail

→ dùng `preview_url`.

### G. `saveCheck()`

→ hỗ trợ AI online/offline + pending.

### H. `render()`

→ thêm star/sort/filter/status.

### I. Supabase

→ mở rộng schema.

### J. status UI

→ AI/GPS/Cloud tách riêng.

---

# 43. Thứ tự triển khai

Không làm tất cả cùng lúc.

## Bước 1 — Giữ UI V3 chạy

Test:

```text
Map
Tabs
Popup
Camera
Upload
Knowledge
Supabase
```

## Bước 2 — Tách AI optional

```text
AI ONLINE/OFFLINE
```

## Bước 3 — GPS realtime

```text
watchPosition
```

## Bước 4 — Auto-follow

## Bước 5 — Cảnh báo khoảng cách

## Bước 6 — Nhật ký nâng cấp

## Bước 7 — Preview YOLO

## Bước 8 — Supabase schema

## Bước 9 — Production domain

## Bước 10 — PWA/cache

---

# 44. Bộ test bắt buộc

### Test nền tảng

- [ ] UI mở.
- [ ] Map mở.
- [ ] Tab hoạt động.
- [ ] Popup hoạt động.
- [ ] Knowledge hoạt động.
- [ ] Supabase không làm trắng trang.

### Test GPS

- [ ] GPS cho phép.
- [ ] GPS từ chối.
- [ ] GPS update liên tục.
- [ ] marker người dùng.
- [ ] Auto-follow.
- [ ] kéo map → pause.
- [ ] quay lại Auto.

### Test cảnh báo

- [ ] ngoài bán kính → không báo.
- [ ] vào bán kính → báo.
- [ ] không spam.
- [ ] ra rồi vào lại → báo lại theo rule.
- [ ] GPS accuracy thấp → không cảnh báo sai.

### Test AI online

- [ ] upload.
- [ ] YOLO.
- [ ] bbox.
- [ ] preview.
- [ ] history.
- [ ] Supabase.

### Test AI offline

- [ ] UI vẫn chạy.
- [ ] map vẫn chạy.
- [ ] GPS vẫn chạy.
- [ ] alert vẫn chạy.
- [ ] upload không báo “không bệnh”.
- [ ] record = pending.

### Test AI online trở lại

- [ ] status chuyển online.
- [ ] pending hiển thị.
- [ ] user có thể phân tích.

### Test production

- [ ] HTTPS.
- [ ] WSS.
- [ ] không localhost frontend.
- [ ] domain hoạt động.
- [ ] mobile hoạt động.

---

# 45. Lệnh giao cho OpenCode

```text
NỀN TẢNG DUY NHẤT CỦA DỰ ÁN LÀ:

AI_Rice_UX_Prototype_V3_CLICK_POPUP_FINAL.html

Hãy đọc và giữ nguyên nền tảng UX này.

KHÔNG tạo frontend mới.
KHÔNG viết lại giao diện.
KHÔNG bỏ Leaflet.
KHÔNG bỏ các tab.
KHÔNG bỏ popup.
KHÔNG bỏ camera/upload.
KHÔNG bỏ DISEASES.
KHÔNG bỏ Supabase.
KHÔNG bỏ AI Adapter.

Mục tiêu là tích hợp các chức năng mới vào chính nền tảng hiện tại.

PHẢI thực hiện:

1. Giữ nguyên UI V3.
2. Tách AI thành AIService optional.
3. AI server online thì phân tích YOLO.
4. AI server offline thì web vẫn hoạt động.
5. Khi AI offline:
   - Map chạy.
   - GPS chạy.
   - Auto-follow chạy.
   - Cảnh báo khoảng cách chạy.
   - Nhật ký cũ chạy.
   - Kiến thức chạy.
   - Không giả lập kết quả AI trong production.
6. Chuyển GPS từ getCurrentPosition sang watchPosition.
7. Tạo marker người dùng.
8. Tạo Auto-follow.
9. User kéo map thì pause follow.
10. Có nút quay lại vị trí người dùng.
11. Tạo rice_locations.
12. Tính khoảng cách client-side.
13. Cảnh báo khi vào radius_m.
14. Chống cảnh báo lặp.
15. Kiểm tra GPS accuracy.
16. Nâng cấp Nhật ký.
17. Thêm custom_name.
18. Thêm Ấp/Xã/Tỉnh.
19. Thêm preview_url.
20. Hiển thị ảnh YOLO bbox thật.
21. Thêm starred.
22. Starred lên đầu.
23. Thêm sort/filter.
24. Thêm ai_status pending/analyzed/failed.
25. Nếu AI offline, ảnh có thể lưu pending.
26. Không được coi pending là không bệnh.
27. Giữ PlantNet nhưng phải phân biệt provider.
28. Mock chỉ development.
29. Production domain:
   https://ai.nongnghiepsangtao.io.vn/
30. Không hard-code localhost trong frontend production.
31. WebSocket production dùng WSS.
32. Giữ Supabase.
33. Mở rộng database hợp lý.
34. Dùng Storage cho ảnh.
35. Có local queue nếu cloud/AI tạm thời không khả dụng.
36. Không để AI lỗi làm chết bản đồ/GPS/cảnh báo.

QUAN TRỌNG:

Phải sửa trực tiếp code hiện tại.
Không chỉ lập kế hoạch.

Sau mỗi nhóm thay đổi phải chạy test.

Nếu phát hiện lỗi thì tự sửa.

Cuối cùng báo:

- file đã sửa;
- chức năng đã tích hợp;
- chức năng cũ đã bảo toàn;
- test đã chạy;
- localhost nào còn lại và vì sao;
- production URL;
- trạng thái AI online/offline;
- trạng thái GPS;
- trạng thái Supabase;
- lỗi còn tồn tại nếu có.

Nếu một chức năng chưa thể hoàn thiện thì không được giả vờ đã hoàn thành.
```

---

# 46. Kết luận

**UX V3 là sản phẩm chính.**

Các thành phần khác chỉ là dịch vụ tích hợp:

```text
                 AI RICE UX V3
                      │
       ┌──────────────┼──────────────┐
       │              │              │
       ▼              ▼              ▼
     Leaflet          GPS          Supabase
       │              │              │
       ▼              ▼              ▼
    Bản đồ        Auto-follow       Cloud
       │              │
       └──────┬───────┘
              ▼
          Cảnh báo
              │
              ▼
        Kiểm tra ruộng
              │
              ▼
         AI Service
              │
        ┌─────┴─────┐
        ▼           ▼
     YOLOv8      Provider khác
        │
        ▼
   Preview + bbox
        │
        ▼
      Nhật ký
```

Đây là hướng đúng với yêu cầu: **không thay “cái này” bằng hệ thống khác; lấy chính UX V3 làm lõi rồi ghép từng tính năng vào.**
