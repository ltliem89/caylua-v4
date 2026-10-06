# AI RICE — GIAO NHIỆM VỤ TỔNG THỂ: TÁI THIẾT KẾ BẢN ĐỒ KHẢO SÁT THỰC ĐỊA

## 1. MỤC TIÊU NHIỆM VỤ

Rà soát và nâng cấp TOÀN BỘ dự án AI Rice để **BẢN ĐỒ trở thành màn hình trung tâm của sản phẩm**, phục vụ đúng nghiệp vụ:

> Người dùng cầm điện thoại đi ngoài đồng → GPS xác định vị trí → bấm quét/chụp → ảnh được lưu Supabase Storage → AI/YOLO xử lý → kết quả quay về Supabase → điểm khảo sát trên bản đồ cập nhật realtime → người dùng tiếp tục di chuyển đến điểm tiếp theo.

Không được biến dự án thành một ứng dụng bản đồ độc lập. Phải giữ **V3/HTML hiện có làm nền giao diện**, sau đó tái cấu trúc UX quanh `Map + Survey + AI + Journal`.

---

# 2. TÀI LIỆU/CODE BẮT BUỘC PHẢI ĐỌC TRƯỚC KHI SỬA

Đọc toàn bộ các file hiện có trong project, tối thiểu:

- `camera.html`
- `server.py`
- `start_all.py`
- `auth_simple.py`
- `storage_user.py`
- `gui.py`
- toàn bộ file JS/CSS đang được `camera.html` sử dụng
- `AI_RICE_01_SERVER.txt`
- `AI_RICE_02_GUI.txt`
- `AI_RICE_03_STORAGE.txt`
- `AI_RICE_04_TEST.txt`
- `AI_RICE_05_CONFIG.txt`
- `project_tree.txt`
- các file Markdown đặc tả AI Rice đã có
- các file Supabase/schema/config nếu tồn tại

Không được tự ý tạo kiến trúc mới khi trong project đã có module tương đương.

---

# 3. NGUYÊN TẮC KHÔNG ĐƯỢC VI PHẠM

## 3.1 Giữ V3 làm nền

Không xóa giao diện V3 hiện có chỉ để thay bằng một template khác.

Phải giữ:
- phong cách UI hiện tại;
- camera/chụp ảnh;
- lịch sử;
- thư viện bệnh;
- thống kê;
- viewer;
- trạng thái WebSocket/server;
- các chức năng AI đang chạy được.

Nhưng được phép **tái bố trí** để Map + Survey trở thành trung tâm.

## 3.2 Không mock dữ liệu production

Không dùng:
- marker giả;
- GPS giả;
- kết quả AI giả;
- dữ liệu Supabase giả;
- timeout giả để tạo cảm giác realtime.

Nếu backend chưa có API cần thiết:
1. phát hiện chính xác thiếu gì;
2. tạo adapter/API cần thiết;
3. ghi rõ thay đổi;
4. test thật.

## 3.3 Không làm mất chức năng AI hiện tại

YOLO hiện có phải tiếp tục hoạt động.

Server hiện tại đã có:
- FastAPI;
- YOLO;
- upload ảnh;
- preview;
- history;
- WebSocket;
- xác thực user.

Không được thay thế bừa bằng một server khác.

## 3.4 Supabase là nguồn dữ liệu cloud chính

Dữ liệu khảo sát phải được thiết kế để đi theo:

`IndexedDB → Sync Queue → Supabase → AI Server → Supabase → Realtime → UI`

Không lấy `localStorage` làm database chính.

---

# 4. KIẾN TRÚC UX MỚI

## Màn hình chính

```text
┌───────────────────────────────────────┐
│ 🌾 AI RICE       GPS ●  Mạng ●  AI ● │
├───────────────────────────────────────┤
│ 🔎 Tìm ruộng / điểm       ⚙️         │
│                                       │
│              BẢN ĐỒ                   │
│                                       │
│     🔴        🟢        🟡           │
│                 📍                    │
│                    📍                 │
│                                       │
│                          ◎            │
│                    Về vị trí tôi      │
├───────────────────────────────────────┤
│ Ruộng hiện tại                        │
│ 27 điểm • 9 bệnh • 5 chờ AI          │
├───────────────────────────────────────┤
│          📷 QUÉT ĐIỂM NÀY             │
├───────────────────────────────────────┤
│ 🗺 Bản đồ │ 📷 Quét │ 📖 Nhật ký │ ☰ │
└───────────────────────────────────────┘
```

Bản đồ phải chiếm phần lớn màn hình điện thoại.

---

# 5. HỆ THỐNG BẢN ĐỒ

## 5.1 Map engine

Dùng map engine phù hợp với project hiện tại.

Ưu tiên:
- Leaflet nếu project đang dùng Leaflet;
- MapLibre nếu project đã có hoặc cần vector map;
- không đổi engine nếu việc đổi không mang lại lợi ích rõ ràng.

Phải hỗ trợ:
- zoom;
- pan;
- locate;
- marker;
- popup;
- polyline;
- clustering nếu nhiều điểm;
- layer control;
- fullscreen;
- responsive mobile.

## 5.2 GPS

Triển khai thật bằng:

`navigator.geolocation.watchPosition()`

Mỗi GPS record có:

```text
latitude
longitude
accuracy
altitude
heading
speed
timestamp
```

Phải xử lý:
- GPS chưa bật;
- permission denied;
- GPS yếu;
- accuracy quá lớn;
- mất GPS;
- GPS quay lại;
- thiết bị di chuyển;
- người dùng kéo bản đồ.

### Quy tắc auto-follow

- Khi đang khảo sát: có thể auto-follow.
- Khi người dùng kéo bản đồ: tạm ngừng auto-follow.
- Hiện nút `Về vị trí tôi`.
- Bấm nút → quay về GPS hiện tại và bật lại follow.
- Không tự giật bản đồ liên tục khi người dùng đang xem điểm khác.

---

# 6. MARKER

Mỗi `survey_point` là một marker.

Trạng thái:

```text
🟢 Không phát hiện
🔴 Có bệnh
🟡 Chờ AI
🔵 Đang xử lý
⚠️ Lỗi AI
🟣 Chưa đồng bộ
```

Không chỉ dùng màu; phải có icon/shape hoặc nhãn để người dùng dễ phân biệt.

Marker phải chứa:
- survey_point_id;
- thời gian;
- GPS;
- accuracy;
- field_id;
- trạng thái AI;
- bệnh;
- confidence;
- số ảnh.

---

# 7. POPUP CHI TIẾT ĐIỂM

Chạm marker phải mở popup/card:

```text
📍 Điểm khảo sát #12

Ruộng: Ruộng A
14:32 — 06/10/2026
GPS ±6 m

🔴 Bệnh đạo ôn
Confidence 91%

Ảnh: 2
AI: Hoàn thành
☁ Supabase: Đã đồng bộ

[ Xem ảnh ]
[ Chi tiết bệnh ]
[ Mở nhật ký ]
[ Đặt ưu tiên ]
```

Nếu chưa có kết quả:

```text
🟡 Đang chờ AI
Ảnh đã tải lên
Đang xử lý...
```

Nếu offline:

```text
🟣 Chưa đồng bộ
Sẽ tự đồng bộ khi có mạng
```

---

# 8. CHẾ ĐỘ KHẢO SÁT

Có nút lớn:

`▶ BẮT ĐẦU KHẢO SÁT`

Khi bắt đầu:

```text
survey_session
```

được tạo.

Trong session hiển thị:

```text
Đang khảo sát
Ruộng A
00:32:15

Điểm: 27
Có bệnh: 9
Không bệnh: 13
Chờ AI: 5
Lỗi: 0
```

Nút chính:

`📷 QUÉT ĐIỂM NÀY`

Mỗi lần quét:
1. lấy GPS hiện tại;
2. tạo survey_point;
3. mở camera;
4. chụp ảnh;
5. lưu local trước;
6. upload Supabase;
7. tạo AI job;
8. nhận AI result;
9. cập nhật marker;
10. ghi nhật ký.

---

# 9. LUỒNG DỮ LIỆU CHUẨN

```text
GPS
 ↓
survey_session
 ↓
survey_point
 ↓
survey_image
 ↓
Supabase Storage
 ↓
AI Server / YOLO
 ↓
ai_result
 ↓
Supabase
 ↓
Realtime
 ↓
Map Marker
 ↓
Journal / Statistics / Alert
```

---

# 10. SUPABASE STORAGE

Nếu bucket đã tồn tại thì dùng bucket hiện tại.

Nếu chưa có, chuẩn hóa:

```text
survey-images
```

Path đề xuất:

```text
{user_id}/{survey_session_id}/{survey_point_id}/{image_id}/original.jpg
{user_id}/{survey_session_id}/{survey_point_id}/{image_id}/preview.jpg
```

Không đưa service-role key vào frontend.

---

# 11. DATABASE

Không tạo bảng trùng với bảng đã tồn tại.

Nếu project chưa có tương đương, cần có nhóm dữ liệu:

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

Quan hệ:

```text
profiles
   │
   └── fields
          │
          └── survey_sessions
                  │
                  └── survey_points
                          │
                          ├── survey_images
                          │       └── ai_results
                          │
                          └── gps
```

---

# 12. REALTIME

Supabase Realtime phải cập nhật tối thiểu:

- survey_points;
- survey_images;
- ai_results;
- alerts;
- sensor_readings nếu module sensor đang hoạt động.

Ví dụ:

```text
AI Server hoàn thành
        ↓
UPDATE ai_results
        ↓
Supabase Realtime
        ↓
V3 nhận event
        ↓
Marker đổi từ 🟡 → 🔴
        ↓
Popup cập nhật
        ↓
Thống kê cập nhật
```

Không reload toàn trang để cập nhật kết quả.

---

# 13. OFFLINE-FIRST

Ngoài đồng có thể mất mạng.

Phải hỗ trợ:

```text
Không mạng
   ↓
GPS vẫn chạy
   ↓
chụp ảnh
   ↓
IndexedDB
   ↓
Sync Queue
   ↓
marker 🟣
   ↓
có mạng
   ↓
upload Supabase
   ↓
AI
   ↓
marker cập nhật
```

Phải tránh mất ảnh khi:
- đóng trình duyệt;
- reload;
- mất mạng;
- mất điện;
- mạng chập chờn.

---

# 14. NHẬT KÝ

Nhật ký không còn chỉ là gallery ảnh.

Mỗi record phải gắn với:

```text
survey_session
survey_point
GPS
field
image
AI result
timestamp
sync status
```

Cho phép:
- xem ảnh bbox;
- xem bệnh;
- confidence;
- xem vị trí trên bản đồ;
- xem thời gian;
- tên điểm;
- tên tùy chỉnh;
- Ấp/Xã/Tỉnh nếu có;
- đánh dấu ưu tiên;
- lọc bệnh;
- lọc thời gian;
- lọc ruộng;
- lọc trạng thái AI.

---

# 15. LAYER BẢN ĐỒ

Phải có panel bật/tắt:

```text
☑ Vị trí tôi
☑ Điểm khảo sát
☑ Có bệnh
☑ Không bệnh
☑ Chờ AI
☑ Tuyến đường khảo sát
☐ Heatmap bệnh
☐ Cảnh báo
☐ Sensor
```

---

# 16. BỘ LỌC

Bộ lọc nhanh:

```text
Tất cả
Có bệnh
Không bệnh
Chờ AI
Lỗi
Chưa đồng bộ
```

Bộ lọc bệnh:

```text
Bệnh bạc lá
Sâu ăn lá
Châu chấu
Lùn cỏ
Sâu cuốn lá
Ngộ độc hữu cơ
Đạo ôn
Đốm vằn
Sâu đục thân
Sọc vi khuẩn
Tungro
```

Phải lấy danh sách bệnh từ nguồn hiện có, không hard-code nếu backend đã có disease catalog.

---

# 17. HEATMAP

Nếu dữ liệu đủ:

- heatmap mật độ điểm có bệnh;
- heatmap theo từng bệnh;
- chọn khoảng thời gian;
- chọn ruộng;
- bật/tắt.

Không tạo heatmap nếu dữ liệu chưa đủ để tránh gây hiểu nhầm.

---

# 18. TUYẾN ĐƯỜNG KHẢO SÁT

Lưu GPS track trong session.

Hiển thị:

```text
GPS 01 ─ GPS 02 ─ GPS 03 ─ GPS 04
```

Cho phép:
- xem tuyến;
- xem tổng quãng đường;
- thời gian khảo sát;
- số điểm;
- mật độ khảo sát;
- điểm có bệnh.

---

# 19. DASHBOARD TRÊN BẢN ĐỒ

Một bottom sheet nhỏ:

```text
RUỘNG A

27 điểm
18 đã AI
5 chờ AI
4 lỗi/đồng bộ

🔴 9 điểm bệnh
🟢 9 điểm không bệnh

Bệnh nổi bật:
Đạo ôn 6
Bạc lá 2
Đốm vằn 1
```

Bottom sheet phải có thể kéo lên/xuống.

---

# 20. TÌM KIẾM

Tìm:
- ruộng;
- điểm khảo sát;
- bệnh;
- ngày;
- tên điểm;
- địa danh nếu dữ liệu có.

Chọn kết quả → map fly-to điểm.

---

# 21. THỐNG KÊ KHÔNG ĐƯỢC TÁCH KHỎI BẢN ĐỒ

Các KPI phải liên kết ngược tới marker.

Ví dụ:

`9 điểm có bệnh`

→ bấm vào → map chỉ hiển thị 9 điểm bệnh.

`Đạo ôn 6`

→ bấm → map lọc 6 điểm đạo ôn.

---

# 22. CẢNH BÁO

Nếu backend đã có alerts:

Marker cảnh báo:

```text
⚠️
```

Popup:

```text
CẢNH BÁO

Khu vực có mật độ bệnh cao.

9 điểm bệnh / 27 điểm
Đạo ôn chiếm ưu thế

[ Xem khu vực ]
[ Xem khuyến nghị ]
```

Không tự đưa ra khuyến cáo nông học vượt quá dữ liệu/knowledge base hiện có.

---

# 23. SENSOR / IOT

Nếu sensor đã có trong project:

Sensor marker:

```text
🌡 28.4°C
💧 82%
🌱 ...
```

Cho phép liên kết:

```text
survey_point
      +
sensor_reading
      ↓
environment-disease analysis
```

Nhưng không để sensor làm rối giao diện khảo sát chính.

---

# 24. MOBILE UX

Ưu tiên điện thoại.

Bắt buộc:
- nút lớn;
- dễ bấm khi đang đứng ngoài ruộng;
- không dùng chữ quá nhỏ;
- bottom sheet;
- camera mở nhanh;
- GPS status luôn nhìn thấy;
- mạng/offline status luôn nhìn thấy;
- không yêu cầu người dùng thao tác nhiều bước.

Nút quan trọng nhất:

`📷 QUÉT ĐIỂM NÀY`

phải luôn dễ tìm.

---

# 25. DESKTOP UX

Trên máy tính:

```text
┌──────────────┬──────────────────────────────┐
│ Bộ lọc       │                              │
│ Ruộng        │             MAP              │
│ Bệnh         │                              │
│ Session      │                              │
│              │                              │
├──────────────┤                              │
│ Thống kê     │                              │
└──────────────┴──────────────────────────────┘
```

Click marker → panel chi tiết bên phải.

---

# 26. TRẠNG THÁI HỆ THỐNG

Header:

```text
GPS ●
Mạng ●
Supabase ●
AI ●
Realtime ●
```

Mỗi trạng thái có tooltip chi tiết.

Ví dụ:

```text
GPS: ±6 m
Supabase: Connected
AI: Online
Realtime: Connected
Offline Queue: 2
```

---

# 27. BẢO MẬT

Bắt buộc:

- Supabase Auth nếu đã triển khai;
- RLS;
- Storage policy;
- user chỉ xem dữ liệu của mình;
- không service-role key trong browser;
- HTTPS;
- WSS;
- validate upload;
- giới hạn kích thước ảnh;
- không để lộ đường dẫn file private;
- token preview phải có kiểm soát quyền.

---

# 28. TƯƠNG THÍCH SERVER AI HIỆN TẠI

Không phá các endpoint đang hoạt động.

Đặc biệt kiểm tra và giữ tương thích với:

```text
/analyze_mobile
/api/ai/predict
/api/image-history
/preview-token/{user_id}/{name}
/preview/{user_id}/{name}
/ws
/api/report
/api/disease-images/manifest
/api/disease-images/{image_id}
/api/disease-images/{image_id}/metadata
```

Nếu cần endpoint mới cho survey/Supabase:

```text
/api/survey/*
```

thì thiết kế rõ ràng và ghi vào tài liệu API.

---

# 29. CÁC VẤN ĐỀ PHẢI RÀ SOÁT

## Bắt buộc kiểm tra

### A. GPS
- permission;
- `watchPosition`;
- accuracy;
- mất GPS;
- auto-follow.

### B. Bản đồ
- marker;
- popup;
- cluster;
- layer;
- filter;
- route;
- heatmap.

### C. Camera
- capture;
- preview;
- retake;
- upload;
- offline.

### D. AI
- job;
- processing;
- result;
- bbox;
- confidence;
- model version.

### E. Supabase
- auth;
- storage;
- database;
- RLS;
- realtime.

### F. Offline
- IndexedDB;
- queue;
- retry;
- idempotency;
- recovery sau reload.

### G. Nhật ký
- map ↔ journal;
- image ↔ point;
- disease ↔ marker.

### H. Production
- domain;
- HTTPS;
- API same-origin;
- WSS;
- CORS;
- PWA.

---

# 30. ĐẶC BIỆT: KHÔNG ĐƯỢC LÀM MẤT BẢN ĐỒ

Sau mỗi lần sửa:

1. mở trang;
2. bản đồ phải render;
3. GPS phải hoạt động;
4. marker phải render;
5. popup phải mở;
6. camera phải mở;
7. AI phải nhận ảnh;
8. kết quả AI phải quay về marker;
9. reload không làm mất dữ liệu;
10. offline không làm mất khảo sát.

Nếu sửa một module làm hỏng module khác → sửa tiếp, không bỏ chức năng cũ.

---

# 31. TEST CASE BẮT BUỘC

## TEST 01 — GPS

- mở điện thoại;
- cấp quyền GPS;
- xác định vị trí;
- map hiển thị vị trí;
- accuracy hiển thị.

## TEST 02 — 5 điểm khảo sát

Tạo thật:

```text
Point 1
Point 2
Point 3
Point 4
Point 5
```

Mỗi point có GPS khác nhau.

## TEST 03 — AI

Chụp ảnh thật.

Kiểm tra:

```text
Storage
→ AI
→ result
→ marker
→ journal
```

## TEST 04 — Offline

- tắt mạng;
- tạo 3 điểm;
- chụp 3 ảnh;
- reload;
- kiểm tra còn dữ liệu;
- bật mạng;
- queue tự đồng bộ.

## TEST 05 — Realtime

Thiết bị A tạo kết quả.

Thiết bị B đang mở bản đồ.

B phải nhận marker/result mà không reload.

## TEST 06 — Popup

Marker → popup → ảnh → disease → journal.

## TEST 07 — Filter

Có bệnh → chỉ hiện marker bệnh.

## TEST 08 — Route

Session → hiển thị đường đi.

## TEST 09 — Security

User A không được xem dữ liệu User B.

## TEST 10 — Production

Test trực tiếp trên:

`https://ai.nongnghiepsangtao.io.vn/`

Không chỉ test localhost.

---

# 32. TIÊU CHÍ HOÀN THÀNH

Chỉ được kết luận DONE khi:

- [ ] Map là màn hình trung tâm.
- [ ] Mobile UX tốt.
- [ ] GPS thật.
- [ ] Survey session thật.
- [ ] Survey point thật.
- [ ] Marker realtime.
- [ ] Popup đầy đủ.
- [ ] Camera tích hợp với point.
- [ ] Ảnh lên Supabase Storage.
- [ ] AI YOLO xử lý.
- [ ] AI result về Supabase.
- [ ] Realtime cập nhật map.
- [ ] IndexedDB offline.
- [ ] Sync queue.
- [ ] Journal liên kết map.
- [ ] Filter.
- [ ] Search.
- [ ] Route.
- [ ] Heatmap nếu đủ dữ liệu.
- [ ] Alert.
- [ ] Sensor nếu module đã có.
- [ ] RLS.
- [ ] Storage policy.
- [ ] Không lộ service role key.
- [ ] Production HTTPS/WSS.
- [ ] PWA/mobile.
- [ ] Test 10 nhóm đạt.
- [ ] Không làm mất chức năng V3/AI cũ.

---

# 33. KẾT QUẢ PHẢI BÀN GIAO

AI thực hiện phải bàn giao:

1. Code đã sửa thật.
2. Danh sách file đã sửa.
3. Danh sách file mới.
4. Database migration/SQL nếu cần.
5. Supabase Storage policy nếu cần.
6. RLS policy nếu cần.
7. API mới/thay đổi.
8. Sơ đồ dữ liệu.
9. Test report.
10. Các lỗi còn tồn tại.
11. Hướng dẫn chạy.
12. Hướng dẫn deploy production.
13. Screenshot hoặc mô tả kiểm chứng các màn hình chính.

Không được chỉ trả lời "đã hoàn thành".

---

# 34. ƯU TIÊN TRIỂN KHAI

## P0 — bắt buộc

```text
Map
GPS
Survey Session
Survey Point
Camera
Supabase Storage
AI
Realtime
Journal
Offline
```

## P1

```text
Filter
Search
Route
Dashboard
Alert
Disease layer
```

## P2

```text
Heatmap
Sensor layer
Advanced analytics
Export report
```

---

# 35. LỆNH GIAO CHO AI / OPENCODE

Dán nguyên khối dưới đây vào AI coding agent:

```text
BẠN LÀ LEAD ENGINEER CỦA DỰ ÁN AI RICE.

NHIỆM VỤ:
Rà soát và triển khai toàn bộ đặc tả trong file:
AI_RICE_MAP_MASTER_TASK.md

MỤC TIÊU:
Biến BẢN ĐỒ thành màn hình trung tâm của AI Rice để người dùng cầm điện thoại đi khảo sát ngoài đồng theo chuỗi:

GPS → Survey Point → Camera → Supabase Storage → YOLO AI → Supabase → Realtime → Map → Journal.

BẮT BUỘC:

1. Đọc toàn bộ project trước khi sửa.
2. Đọc camera.html, server.py, start_all.py, auth_simple.py, storage_user.py và toàn bộ JS/CSS/config.
3. Đọc AI_RICE_MAP_MASTER_TASK.md từ đầu đến cuối.
4. Không xóa V3.
5. Không thay thế giao diện bằng template mới nếu không cần thiết.
6. Không dùng mock production.
7. Không tạo database/table trùng với thứ đã tồn tại.
8. Tái sử dụng API/module hiện có khi phù hợp.
9. Nếu thiếu API thì bổ sung API thật.
10. Supabase là cloud data source chính.
11. IndexedDB là local/offline data store.
12. localStorage không được dùng làm database khảo sát chính.
13. Không đưa Supabase service-role key vào frontend.
14. Giữ YOLO/server.py hoạt động.
15. Giữ WebSocket AI hiện có hoạt động.
16. Không làm mất camera, history, disease library, statistics, viewer.
17. Bản đồ phải là trung tâm UX.
18. GPS phải dùng navigator.geolocation.watchPosition().
19. Mỗi survey_point phải gắn GPS.
20. Mỗi ảnh phải gắn survey_point.
21. AI result phải gắn survey_image/survey_point.
22. Marker phải cập nhật theo trạng thái AI.
23. Supabase Realtime phải cập nhật UI mà không reload.
24. Offline phải lưu được GPS + point + ảnh + queue.
25. Khi online phải tự đồng bộ.
26. Phải có idempotency để retry không tạo duplicate.
27. Popup marker phải mở được ảnh, bệnh, confidence, thời gian, GPS và journal.
28. Journal phải liên kết ngược với marker.
29. Filter phải điều khiển marker/layer.
30. Production domain phải hoạt động.

QUY TRÌNH LÀM VIỆC:

PHASE 1:
Audit toàn bộ project.
Tạo file:
AI_RICE_MAP_AUDIT.md

Ghi:
- file nào liên quan;
- kiến trúc hiện tại;
- map hiện tại;
- GPS hiện tại;
- AI hiện tại;
- Supabase hiện tại;
- WebSocket;
- storage;
- auth;
- điểm thiếu;
- điểm xung đột;
- file sẽ sửa.

PHASE 2:
Thiết kế schema/adapter.
Không duplicate schema.
Nếu cần migration thì tạo migration rõ ràng.

PHASE 3:
Triển khai Map + GPS.

PHASE 4:
Triển khai Survey Session + Survey Point.

PHASE 5:
Nối Camera → Storage → AI.

PHASE 6:
Nối AI Result → Supabase → Realtime → Map.

PHASE 7:
Triển khai IndexedDB + Sync Queue + Offline.

PHASE 8:
Nối Journal/Statistics/Alert.

PHASE 9:
Responsive mobile + desktop.

PHASE 10:
Test toàn bộ.

SAU KHI XÂY DỰNG KẾ HOẠCH:
KHÔNG DỪNG Ở VIỆC VIẾT KẾ HOẠCH.
PHẢI TỰ ĐỘNG TIẾP TỤC THỰC HIỆN TỪNG PHASE.

Nếu gặp lỗi:
- đọc code liên quan;
- tìm nguyên nhân;
- sửa;
- chạy lại test;
- không né lỗi bằng mock.

Nếu một yêu cầu không thể thực hiện do backend/Supabase hiện tại thiếu thành phần:
- xác định chính xác thành phần thiếu;
- tạo migration/API/adapter cần thiết nếu có thể;
- nếu cần thông tin bí mật hoặc quyền truy cập thì ghi rõ BLOCKER;
- không giả vờ đã hoàn thành.

TEST BẮT BUỘC:
- GPS thật.
- 5 survey points.
- 5 ảnh.
- AI thật.
- Supabase Storage thật.
- Realtime thật.
- offline 3 điểm.
- reload khi offline.
- sync sau khi online.
- marker/filter/popup.
- user A/B security.
- production URL.

SAU CÙNG:
Tạo:
AI_RICE_MAP_IMPLEMENTATION_REPORT.md

Báo cáo:
- đã làm gì;
- file sửa;
- file mới;
- migration;
- API;
- test;
- kết quả;
- lỗi còn lại;
- blocker;
- hướng deploy.

KHÔNG ĐƯỢC KẾT LUẬN "DONE" NẾU CHƯA KIỂM TRA THỰC TẾ.
```

---

# 36. ĐỊNH NGHĨA THÀNH CÔNG

AI Rice sau khi hoàn thành phải đạt trải nghiệm:

```text
MỞ AI RICE
     ↓
BẢN ĐỒ
     ↓
GPS XÁC ĐỊNH VỊ TRÍ
     ↓
BẮT ĐẦU KHẢO SÁT
     ↓
ĐI ĐẾN ĐIỂM
     ↓
QUÉT ĐIỂM
     ↓
CHỤP ẢNH
     ↓
LƯU SUPABASE
     ↓
YOLO
     ↓
KẾT QUẢ
     ↓
MARKER ĐỔI MÀU
     ↓
XEM BỆNH / CONFIDENCE / ẢNH
     ↓
ĐIỂM TIẾP THEO
     ↓
...
     ↓
KẾT THÚC KHẢO SÁT
     ↓
BẢN ĐỒ TOÀN BỘ RUỘNG
     ↓
NHẬT KÝ + THỐNG KÊ + CẢNH BÁO
```

Đây là chuẩn UX/kiến trúc mục tiêu của bản đồ AI Rice.
