# CAY LÚA -- MD ĐẶC TẢ CẢI TIẾN

## Giao diện V3 + AI Adapter linh hoạt + API miễn phí + YOLOv8 dự phòng

**Phiên bản:** 1.0\
**Mục tiêu:** Ứng dụng CAY LÚA phải chạy được ngay cả khi chưa có server
riêng; khi server/YOLOv8 của nhóm được bật, hệ thống tự ưu tiên mô hình
của nhóm mà không phải sửa lại giao diện.

------------------------------------------------------------------------

# 1. MỤC TIÊU TỔNG THỂ

CAY LÚA được thiết kế theo nguyên tắc:

> **Giao diện cố định -- nguồn AI linh hoạt.**

Người dùng chỉ cần:

``` text
📍 Chọn vị trí
   ↓
📷 Chụp / Upload ảnh
   ↓
🤖 Phân tích
   ↓
🦠 Bệnh
🌿 Màu lá
🌱 Tuổi lúa
📊 Thông tin sức khỏe
   ↓
🗺️ Lưu vị trí + lịch sử
```

Người dùng **không cần biết** kết quả đang được xử lý bởi:

-   YOLOv8 của CAY LÚA;
-   Pl@ntNet;
-   model local;
-   hoặc provider AI khác.

------------------------------------------------------------------------

# 2. YÊU CẦU QUAN TRỌNG NHẤT

## 2.1 Không bắt buộc server

Hiện tại nhóm chưa chạy `server.py`.

Vì vậy:

``` text
Mở HTML
→ ứng dụng vẫn phải sử dụng được
```

Không được thiết kế kiểu:

``` text
HTML
 ↓
/analyze_mobile
 ↓
server bắt buộc phải chạy
```

Nếu server không chạy, người dùng vẫn phải có đường phân tích AI dự
phòng.

------------------------------------------------------------------------

# 3. KIẾN TRÚC AI ADAPTER

Frontend không gọi trực tiếp từng AI provider.

Chỉ gọi:

``` javascript
AI.analyze(image, context)
```

AI Adapter chịu trách nhiệm chọn nguồn AI.

``` text
                    FRONTEND
                       │
                       ▼
                 AI ADAPTER
                       │
             ┌─────────┼─────────┐
             ▼         ▼         ▼
          SERVER      API       LOCAL
          YOLOv8    Pl@ntNet    Model
             │         │         │
             └─────────┼─────────┘
                       ▼
                  NORMALIZER
                       ▼
                KẾT QUẢ CHUẨN
```

------------------------------------------------------------------------

# 4. CÁC CHẾ ĐỘ AI

## 4.1 AUTO -- mặc định

``` javascript
AI_MODE = "auto";
```

Thứ tự:

``` text
1. Kiểm tra CAY LÚA Server
        ↓
   Nếu hoạt động → YOLOv8
        ↓
   Nếu không → API miễn phí
        ↓
   Nếu API lỗi → model local nếu có
        ↓
   Nếu tất cả lỗi → lưu ảnh chờ phân tích
```

Đây là chế độ mặc định.

------------------------------------------------------------------------

## 4.2 SERVER

``` javascript
AI_MODE = "server";
```

Chỉ dùng server CAY LÚA.

Nếu server không chạy:

``` text
⚠️ Máy chủ AI CAY LÚA chưa hoạt động.
```

Không tự chuyển provider khác.

------------------------------------------------------------------------

## 4.3 API

``` javascript
AI_MODE = "api";
```

Chỉ sử dụng API được cấu hình.

------------------------------------------------------------------------

## 4.4 LOCAL

``` javascript
AI_MODE = "local";
```

Dùng model chạy ngay trên thiết bị/trình duyệt nếu sau này nhóm triển
khai.

------------------------------------------------------------------------

# 5. CẤU HÌNH

Tạo một cấu hình duy nhất:

``` javascript
const CAYLUA_CONFIG = {
    aiMode: "auto",

    server: {
        enabled: true,
        baseUrl: "",
        healthPath: "/health",
        analyzePath: "/analyze_mobile",
        timeoutMs: 3500
    },

    plantnet: {
        enabled: true,
        apiKey: "",
        diseaseEndpoint:
          "https://my-api.plantnet.org/v2/diseases/identify"
    },

    local: {
        enabled: false
    }
};
```

Không rải URL và API key ở nhiều vị trí trong HTML.

------------------------------------------------------------------------

# 6. KIỂM TRA SERVER

Trong `AUTO`, frontend thực hiện:

``` text
GET /health
```

Nếu server trả:

``` text
200
```

→ dùng YOLOv8 CAY LÚA.

Nếu:

``` text
timeout
connection refused
network error
```

→ chuyển provider tiếp theo.

Không được để lỗi server làm hỏng giao diện.

------------------------------------------------------------------------

# 7. PL@NTNET API

## 7.1 Vai trò

Pl@ntNet là **provider dự phòng/đối chiếu**, không thay thế YOLOv8 của
nhóm.

Pl@ntNet có:

``` text
POST /v2/diseases/identify
```

và:

``` text
GET /v2/diseases
```

`/v2/diseases` phải được dùng để kiểm tra phạm vi bệnh/loài được hỗ trợ
trước khi triển khai chính thức.

Tài liệu chính thức của Pl@ntNet cho biết disease identification hiện
chỉ hỗ trợ một danh sách giới hạn loài và bệnh.

------------------------------------------------------------------------

# 8. QUOTA API

Gói Free hiện có:

``` text
500 identification / ngày
```

CAY LÚA phải có cơ chế:

``` text
API quota
   ↓
Nếu còn → gọi API
Nếu hết → dùng provider khác
```

Không tạo nhiều tài khoản để vượt quota.

Nếu dự án thuộc mục đích giáo dục/khoa học phi lợi nhuận, có thể liên hệ
Pl@ntNet để xin hạn mức phù hợp.

------------------------------------------------------------------------

# 9. BẢO MẬT API KEY

## Không làm

``` javascript
const API_KEY = "secret...";
```

trong HTML công khai.

## Ưu tiên

``` text
Frontend
   ↓
CAY LÚA proxy/server
   ↓
Pl@ntNet
```

## Demo local

Có thể cấu hình client-side theo cơ chế được Pl@ntNet cho phép, với
authorized domains và API key được chủ động expose.

Tuy nhiên bản triển khai công khai phải ưu tiên backend proxy.

------------------------------------------------------------------------

# 10. NORMALIZER

Mọi provider phải trả về cùng một cấu trúc.

``` json
{
  "status": "success",
  "provider": "caylua-yolov8",
  "diseases": [
    {
      "name": "Đạo ôn",
      "confidence": 0.91,
      "class_id": 6
    }
  ],
  "processing_ms": 850,
  "message": ""
}
```

Pl@ntNet cũng phải được chuyển về cấu trúc này.

Nhờ đó UI không cần biết provider nào đang chạy.

------------------------------------------------------------------------

# 11. KẾT HỢP HAI AI

Nếu server có sẵn:

``` text
Ảnh
 ├── YOLOv8
 │      ↓
 │   Đạo ôn 91%
 │
 └── Pl@ntNet
        ↓
     Đạo ôn 84%
```

Kết quả:

``` text
🦠 Đạo ôn

CAY LÚA YOLOv8: 91%
API đối chiếu: 84%

✓ Hai hệ thống cùng nhận diện
```

------------------------------------------------------------------------

# 12. KHÔNG ĐƯỢC CỘNG CONFIDENCE

Không làm:

``` text
91% + 84% = 175%
```

và không tự tạo:

``` text
confidence = 87.5%
```

chỉ bằng cách lấy trung bình.

Confidence của hai model có thể không được hiệu chuẩn trên cùng tập dữ
liệu.

Nếu muốn xây bộ hợp nhất sau này, phải đánh giá trên một test set chung
và hiệu chuẩn riêng.

------------------------------------------------------------------------

# 13. KHI HAI AI KHÁC NHAU

Ví dụ:

``` text
YOLO:
Đạo ôn – 76%

Pl@ntNet:
Đốm nâu – 71%
```

Không tự chọn một bệnh làm "đúng".

Hiển thị:

``` text
⚠️ KẾT QUẢ CHƯA THỐNG NHẤT

AI CAY LÚA:
Đạo ôn – 76%

AI đối chiếu:
Đốm nâu – 71%

📷 Nên chụp lại ảnh rõ hơn
hoặc kiểm tra thêm với cán bộ kỹ thuật.
```

------------------------------------------------------------------------

# 14. KHI CONFIDENCE THẤP

Ví dụ:

``` text
YOLO = 42%
```

Hiển thị:

``` text
⚠️ Chưa đủ chắc chắn

Ảnh có thể:
- quá xa;
- thiếu sáng;
- lá bị che;
- triệu chứng chưa rõ.

[📷 Chụp lại]
[📁 Chọn ảnh khác]
```

Không ép AI phải trả một bệnh khi không đủ bằng chứng.

------------------------------------------------------------------------

# 15. GIAO DIỆN V3

Giữ nguyên phong cách giao diện V3:

-   sidebar;
-   bản đồ Leaflet;
-   tìm kiếm;
-   tab;
-   lịch sử;
-   modal kiểm tra;
-   camera;
-   upload;
-   kiến thức bệnh.

Không thiết kế lại toàn bộ.

Chỉ bổ sung lớp AI Adapter và kết quả sức khỏe.

------------------------------------------------------------------------

# 16. CLICK BẢN ĐỒ

Người dùng click bất kỳ vị trí nào:

``` text
Map click
 ↓
Marker
 ↓
Popup
```

Popup:

``` text
┌────────────────────────────┐
│ 📍 Vị trí ruộng đã chọn    │
│                            │
│ Lat: 10.xxxxxx             │
│ Lng: 105.xxxxxx            │
│                            │
│ [📁 Up ảnh]                │
│ [📷 Chụp ảnh]              │
└────────────────────────────┘
```

Không yêu cầu người dùng phải bấm một nút khác trước khi click.

Marker có thể kéo để chỉnh vị trí.

------------------------------------------------------------------------

# 17. UPLOAD ẢNH

Khi bấm:

``` text
📁 Up ảnh
```

mở thư viện điện thoại.

Khi bấm:

``` text
📷 Chụp ảnh
```

mở camera.

Ảnh sau khi chọn được đưa vào:

``` javascript
AI.analyze(file, context)
```

------------------------------------------------------------------------

# 18. CONTEXT GỬI CHO AI

``` json
{
  "latitude": 10.0452,
  "longitude": 105.7469,
  "location_source": "map",
  "sowing_date": "2026-08-25",
  "crop_variety": "OM5451",
  "growth_stage": null
}
```

Provider không cần sử dụng toàn bộ context, nhưng hệ thống phải lưu
context cùng kết quả.

------------------------------------------------------------------------

# 19. MÀU LÁ -- KHÔNG CẦN API

Màu lá được xử lý độc lập bằng Computer Vision.

``` text
Ảnh
 ↓
Tách vùng lá
 ↓
HSV / Lab
 ↓
Phân loại màu
```

Kết quả:

``` json
{
  "green_pct": 72.4,
  "yellow_pct": 20.8,
  "brown_pct": 6.8,
  "dominant_color": "green_yellow"
}
```

Hiển thị:

``` text
🌿 MÀU LÁ

🟢 Xanh       72%
🟡 Vàng       21%
🟤 Nâu         7%
```

Không dùng màu lá đơn độc để kết luận bệnh.

------------------------------------------------------------------------

# 20. TUỔI LÚA -- KHÔNG CẦN API

Người dùng nhập:

``` text
Ngày gieo/cấy
```

Hệ thống tính:

``` text
age_days =
ngày kiểm tra - ngày gieo/cấy
```

Ví dụ:

``` text
25/08/2026
→
29/09/2026
=
35 ngày
```

Nếu chưa nhập:

``` text
🌱 Tuổi lúa: Chưa xác định

[Nhập ngày gieo]
```

Không cho AI tự bịa tuổi lúa từ một ảnh nếu không có dữ liệu lịch
gieo/cấy.

------------------------------------------------------------------------

# 21. GIAI ĐOẠN SINH TRƯỞNG

Tách riêng khỏi tuổi.

Có thể có:

``` text
Mạ
Đẻ nhánh
Làm đòng
Trổ
Chín
```

Nguồn:

``` text
1. Người dùng nhập
2. Rule theo giống + tuổi
3. Model AI riêng trong tương lai
```

Không bắt buộc phải có ngay phiên bản đầu.

------------------------------------------------------------------------

# 22. PHIẾU SỨC KHỎE LÚA

Sau khi phân tích:

``` text
┌────────────────────────────────┐
│ 🌾 PHIẾU SỨC KHỎE LÚA          │
├────────────────────────────────┤
│                                │
│ 🦠 Bệnh: Đạo ôn               │
│ 🎯 Độ tin cậy: 91%             │
│ 🤖 Nguồn: CAY LÚA YOLOv8       │
│                                │
│ 🌿 Màu lá: Xanh vàng           │
│ 🟢 Xanh: 72%                   │
│ 🟡 Vàng: 21%                   │
│                                │
│ 🌱 Tuổi lúa: 35 ngày           │
│ 🌾 Giai đoạn: Đẻ nhánh        │
│                                │
│ 📍 Vị trí                      │
│ 10.xxxxxx, 105.xxxxxx          │
└────────────────────────────────┘
```

------------------------------------------------------------------------

# 23. KHÔNG DÙNG THUẬT NGỮ KHÓ VỚI NHÀ NÔNG

Màn hình chính:

``` text
🦠 Phát hiện: Đạo ôn
📊 Mức cảnh báo: Trung bình
🌱 Tuổi lúa: 35 ngày
🌿 Màu lá: Xanh vàng
```

Không đưa ngay:

``` text
mAP
IoU
class_id
NMS
precision
recall
```

Các thông số kỹ thuật đặt trong:

``` text
[Chi tiết AI]
```

------------------------------------------------------------------------

# 24. CHI TIẾT AI

Dành cho nhóm nghiên cứu/cán bộ kỹ thuật:

``` text
Model:
YOLOv8

Provider:
CAY LÚA Server

Class ID:
6

Confidence:
91.2%

Processing:
850 ms

Preview:
ảnh annotate

API đối chiếu:
Pl@ntNet – 84%
```

------------------------------------------------------------------------

# 25. LƯU LỊCH SỬ

Mỗi lần kiểm tra:

``` json
{
  "timestamp": "...",
  "latitude": 10.0452,
  "longitude": 105.7469,
  "image": "...",
  "provider": "caylua-yolov8",
  "disease": "Đạo ôn",
  "confidence": 0.91,
  "plantnet_confidence": 0.84,
  "age_days": 35,
  "leaf_color": {
    "green": 72,
    "yellow": 21,
    "brown": 7
  }
}
```

------------------------------------------------------------------------

# 26. BẢN ĐỒ BỆNH

Marker có thể biểu diễn tình trạng:

``` text
🟢 Bình thường
🟡 Chưa chắc chắn
🟠 Có vấn đề
🔴 Mức cảnh báo cao
```

Click marker:

``` text
📍 Ruộng A

🦠 Đạo ôn
🎯 91%
🌿 Xanh vàng
🌱 35 ngày

📅 29/09/2026

[Xem chi tiết]
```

------------------------------------------------------------------------

# 27. KHI KHÔNG CÓ AI

Nếu:

``` text
Server: OFF
API: OFF
Local model: OFF
```

không được làm ứng dụng trắng màn hình.

Thay vào đó:

``` text
⚠️ Hiện chưa có nguồn AI khả dụng.

Ảnh và vị trí vẫn được lưu.

[Phân tích lại khi có AI]
```

Record chuyển thành:

``` text
status = "pending_ai"
```

------------------------------------------------------------------------

# 28. HÀNG ĐỢI PHÂN TÍCH

``` text
📦 CHỜ PHÂN TÍCH

Ảnh 001
📍 10.xxxxxx, 105.xxxxxx
⏳ Chờ AI

Ảnh 002
📍 10.xxxxxx, 105.xxxxxx
⏳ Chờ AI
```

Khi provider hoạt động:

``` text
pending_ai
 ↓
AI.analyze()
 ↓
completed
```

------------------------------------------------------------------------

# 29. OFFLINE

Trong tương lai:

``` text
Không Internet
      ↓
Chụp ảnh
      ↓
Lưu:
- ảnh
- GPS
- ngày giờ
- ngày gieo
      ↓
pending_ai
      ↓
Có Internet
      ↓
Tự đồng bộ
```

Nếu local model có thể chạy trên thiết bị:

``` text
offline
 ↓
local AI
 ↓
kết quả ngay
```

------------------------------------------------------------------------

# 30. PROVIDER INTERFACE

Mọi provider phải có API nội bộ:

``` javascript
{
    name,
    healthCheck(),
    analyze(image, context)
}
```

Ví dụ:

``` javascript
const plantnetProvider = {
    name: "plantnet",

    async healthCheck() {
        // kiểm tra khả dụng
    },

    async analyze(image, context) {
        // gọi disease API
    }
};
```

Server provider:

``` javascript
const cayluaProvider = {
    name: "caylua-yolov8",

    async healthCheck() {
        // GET /health
    },

    async analyze(image, context) {
        // POST /analyze_mobile
    }
};
```

------------------------------------------------------------------------

# 31. AUTO ROUTER

``` javascript
async function analyzeRice(image, context) {

    if (AI_MODE === "server") {
        return cayluaProvider.analyze(image, context);
    }

    if (AI_MODE === "api") {
        return plantnetProvider.analyze(image, context);
    }

    if (AI_MODE === "local") {
        return localProvider.analyze(image, context);
    }

    // AUTO
    if (await cayluaProvider.healthCheck()) {
        return cayluaProvider.analyze(image, context);
    }

    if (await plantnetProvider.healthCheck()) {
        return plantnetProvider.analyze(image, context);
    }

    if (localProvider.enabled &&
        await localProvider.healthCheck()) {
        return localProvider.analyze(image, context);
    }

    return {
        status: "pending_ai",
        provider: null
    };
}
```

------------------------------------------------------------------------

# 32. TIMEOUT

Không chờ API vô hạn.

Đề xuất:

``` text
Server health:
3.5 giây

API:
10–15 giây

Toàn bộ AI:
20 giây
```

Nếu timeout:

``` text
→ provider tiếp theo
```

------------------------------------------------------------------------

# 33. LOG

Ghi:

``` text
timestamp
provider
success/fail
latency
error
```

Ví dụ:

``` text
29/09 10:25
caylua-yolov8
FAIL
connection refused

29/09 10:25
plantnet
SUCCESS
2.4s
```

Không ghi API key.

------------------------------------------------------------------------

# 34. CACHE

Để giảm gọi API:

``` text
hash ảnh
   ↓
đã phân tích?
   ↓
Có → dùng kết quả cache
Không → gọi AI
```

Không dùng cache vô thời hạn nếu mục tiêu là theo dõi bệnh thay đổi.

Cache nên gắn với:

``` text
image_hash
model/provider
model_version
```

------------------------------------------------------------------------

# 35. KIỂM SOÁT QUOTA

Trước khi gọi API:

``` text
quota_remaining?
```

Nếu không biết quota thực tế:

``` text
API call
 ↓
429 / quota error
 ↓
disable provider tạm thời
 ↓
provider tiếp theo
```

------------------------------------------------------------------------

# 36. KHÔNG ĐỂ API NGOÀI LÀM MẤT DỮ LIỆU

Nếu Pl@ntNet lỗi:

``` text
Ảnh vẫn lưu
GPS vẫn lưu
Ngày gieo vẫn lưu
```

Chỉ:

``` text
AI result = pending/error
```

------------------------------------------------------------------------

# 37. BẢO VỆ DỮ LIỆU

Không gửi cho provider ngoài những dữ liệu không cần thiết.

Pl@ntNet chủ yếu nhận ảnh phục vụ nhận dạng.

Không gửi:

-   thông tin cá nhân không cần thiết;
-   dữ liệu tài khoản;
-   ghi chú riêng tư;

trừ khi provider thực sự yêu cầu và người dùng đồng ý.

------------------------------------------------------------------------

# 38. GIAO DIỆN TRẠNG THÁI AI

Hiển thị nguồn AI ở mức đơn giản:

``` text
🤖 AI CAY LÚA
● Đang hoạt động
```

hoặc:

``` text
🔎 AI dự phòng
● Pl@ntNet
```

hoặc:

``` text
⚠️ Chưa có AI
Ảnh đã được lưu chờ phân tích
```

------------------------------------------------------------------------

# 39. TRANG CẤU HÌNH KỸ THUẬT

Chỉ dành cho admin/nhóm:

``` text
AI MODE
(•) AUTO
( ) SERVER
( ) API
( ) LOCAL

CAY LÚA SERVER
URL: __________
Status: ● Online

Pl@ntNet
Status: ● Enabled

Local model
Status: ○ Not installed
```

Nhà nông không cần nhìn trang này.

------------------------------------------------------------------------

# 40. LỘ TRÌNH TRIỂN KHAI

## Giai đoạn 1 -- ngay lập tức

``` text
V3
 ↓
AI Adapter
 ↓
AUTO
 ↓
Pl@ntNet API
```

Mục tiêu:

> Mở HTML vẫn có thể kiểm tra AI mà chưa chạy server.

## Giai đoạn 2

``` text
AUTO
 ↓
Server health
 ↓
YOLOv8 nếu server có
 ↓
Pl@ntNet fallback
```

## Giai đoạn 3

``` text
YOLO + Pl@ntNet
 ↓
đối chiếu
```

## Giai đoạn 4

``` text
OpenCV màu lá
+
tuổi lúa
+
giai đoạn
```

## Giai đoạn 5

``` text
bản đồ bệnh
+
lịch sử
+
cảnh báo
```

## Giai đoạn 6

``` text
local/offline AI
```

------------------------------------------------------------------------

# 41. KIỂM THỬ BẮT BUỘC

## Test 1

Server OFF, API ON.

Kỳ vọng:

``` text
→ API được sử dụng
```

## Test 2

Server ON, API ON.

Kỳ vọng:

``` text
→ YOLOv8 được ưu tiên
```

## Test 3

Server OFF, API OFF.

Kỳ vọng:

``` text
→ Ảnh được lưu pending
→ UI không lỗi
```

## Test 4

Server ON nhưng timeout.

Kỳ vọng:

``` text
→ chuyển API
```

## Test 5

API trả 429.

Kỳ vọng:

``` text
→ provider bị bỏ qua
→ provider khác được thử
```

## Test 6

Hai AI khác kết quả.

Kỳ vọng:

``` text
→ không tự kết luận
→ hiển thị cảnh báo không thống nhất
```

## Test 7

Ảnh xấu.

Kỳ vọng:

``` text
→ confidence thấp
→ yêu cầu chụp lại
```

------------------------------------------------------------------------

# 42. TIÊU CHÍ THÀNH CÔNG

CAY LÚA đạt yêu cầu khi:

-   [ ] Mở HTML không cần server vẫn chạy được giao diện.
-   [ ] Click bản đồ hiển thị popup.
-   [ ] Popup hiển thị tọa độ.
-   [ ] Upload ảnh từ popup.
-   [ ] AUTO tự kiểm tra nguồn AI.
-   [ ] Server có thì ưu tiên YOLO.
-   [ ] Server không có thì dùng API.
-   [ ] API lỗi không làm ứng dụng hỏng.
-   [ ] Ảnh vẫn được lưu khi chưa có AI.
-   [ ] Màu lá có thể phân tích độc lập.
-   [ ] Tuổi lúa tính từ ngày gieo/cấy.
-   [ ] Kết quả có nguồn AI.
-   [ ] Lưu lịch sử + vị trí.
-   [ ] API key không lộ trong bản triển khai chính thức.

------------------------------------------------------------------------

# 43. NGUYÊN TẮC CUỐI CÙNG

CAY LÚA không được xây dựng theo tư duy:

> "Ứng dụng phụ thuộc vào một model."

Mà:

> **"Ứng dụng phụ thuộc vào một chuẩn kết quả AI; model/API có thể thay
> đổi."**

``` text
                 CAY LÚA
                    │
              Giao diện V3
                    │
                AI Adapter
                    │
        ┌───────────┼───────────┐
        │           │           │
      YOLO        API         LOCAL
     server     miễn phí       AI
        │           │           │
        └───────────┼───────────┘
                    │
              Normalizer
                    │
                    ▼
             KẾT QUẢ CHUẨN
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
      🦠 Bệnh     🌿 Màu      🌱 Tuổi
                    │
                    ▼
              📊 SỨC KHỎE LÚA
                    │
                    ▼
              🗺️ LỊCH SỬ RUỘNG
```

**Đây là MD kiến trúc nền để dùng khi sửa HTML và server về sau.**
