# TỔNG QUAN CẢI TIẾN ĐỀ TÀI AI RICE THEO HƯỚNG SẢN PHẨM MỚI

## 1. Định hướng cải tiến tổng thể

Đề tài hiện tại đã có nền tảng AI nhận diện bệnh/sâu trên cây lúa bằng hình ảnh, sử dụng YOLOv8 và hệ thống server FastAPI. Hướng cải tiến không tập trung vào việc chỉ tăng số lượng bệnh hoặc chỉ chạy theo độ chính xác mô hình.

Định hướng mới là chuyển từ:

> **“Chụp ảnh → AI nhận diện bệnh”**

sang:

> **“Bản đồ sức khỏe ruộng lúa theo vị trí và thời gian”**

Trong sản phẩm mới, kết quả AI chỉ là một thành phần. Giá trị chính nằm ở việc liên kết:

- Hình ảnh cây lúa.
- Vị trí GPS.
- Thời gian chụp.
- Tuổi/giai đoạn sinh trưởng của lúa.
- Kết quả nhận diện bệnh.
- Lịch sử kiểm tra tại từng vị trí.
- Các khuyến cáo phù hợp.
- Trạng thái khu vực cần kiểm tra tiếp theo.

Mục tiêu là tạo ra một hệ thống giúp người trồng lúa hoặc cán bộ hợp tác xã biết **đã kiểm tra ở đâu, tình trạng tại đó như thế nào, khi nào cần quay lại và cần kiểm tra gì tiếp theo**.

---

# 2. Sản phẩm mới: Bản đồ sức khỏe ruộng lúa

Sản phẩm chính sẽ là một website trực tuyến, dự kiến triển khai trên Vercel.

Website là giao diện trung tâm để người dùng:

- Xem bản đồ ruộng lúa.
- Xem vị trí đã kiểm tra.
- Chụp ảnh mới.
- Lưu ảnh cùng GPS và thời gian.
- Theo dõi tuổi/giai đoạn của lúa.
- Xem lịch sử từng vị trí.
- Xem bệnh đã phát hiện.
- Nhận khuyến cáo cơ bản.
- Biết khu vực nào cần kiểm tra tiếp.

Google Maps được sử dụng như lớp bản đồ trực quan. Dữ liệu về ruộng, ảnh và kết quả không nằm trực tiếp trong Google Maps mà được quản lý trong hệ thống dữ liệu của sản phẩm.

---

# 3. Mỗi lần chụp tạo thành một bản ghi kiểm tra

Một bức ảnh không còn chỉ là một file ảnh.

Mỗi lần chụp sẽ tạo một bản ghi gồm:

```text
ID lần chụp
Ảnh
Latitude
Longitude
Thời gian
Vụ lúa
Ngày gieo
Tuổi lúa
Giai đoạn sinh trưởng
Người kiểm tra
Trạng thái phân tích
Kết quả AI
Mức độ bệnh
Độ tin cậy
```

Ví dụ:

```text
IMG-000125

Ảnh: rice_000125.jpg
Vị trí: 10.xxxxxx, 105.xxxxxx
Thời gian: 27/09/2026 08:32
Tuổi lúa: 57 ngày
Giai đoạn: ...
Bệnh: Đạo ôn
Mức độ: ...
Confidence: ...
```

Nhờ đó, khi hệ thống đọc dữ liệu, nó biết chính xác:

> **Ảnh nào – chụp ở đâu – lúc nào – lúa bao nhiêu ngày – kết quả gì.**

---

# 4. Bản đồ hiển thị tình trạng ruộng

Mỗi vị trí kiểm tra được thể hiện trên bản đồ bằng marker.

Có thể sử dụng màu để biểu diễn trạng thái:

- 🟢 Xanh: đã kiểm tra, chưa phát hiện vấn đề đáng chú ý.
- 🟡 Vàng: cần theo dõi hoặc kiểm tra lại.
- 🔴 Đỏ: đã phát hiện bệnh/cần chú ý.

Khi người dùng nhấn vào marker, không nên hiển thị hàng loạt ảnh rời rạc trên bản đồ.

Thay vào đó, marker mở ra **hồ sơ của vị trí**.

Ví dụ:

```text
KHU VỰC A3

Tuổi lúa: 57 ngày
Giai đoạn: ...

Kết quả gần nhất:
Bệnh đạo ôn
Mức độ: ...

Lần kiểm tra:
20/09
24/09
27/09

[ Xem ảnh ]
[ Xem lịch sử ]
[ Chụp kiểm tra mới ]
```

---

# 5. Lịch sử theo từng vị trí

Một điểm trên bản đồ có thể được kiểm tra nhiều lần.

Thay vì tạo nhiều marker chồng lên nhau, dữ liệu được tổ chức thành một chuỗi lịch sử:

```text
📍 A3
│
├── 20/09 → Kiểm tra → Bình thường
│
├── 24/09 → Kiểm tra → Nghi ngờ
│
└── 27/09 → Kiểm tra → Đạo ôn
```

Cách tổ chức này giống một “hồ sơ sức khỏe” của khu vực ruộng.

Người dùng có thể biết tình trạng thay đổi như thế nào theo thời gian.

---

# 6. Theo dõi người dùng khi đi kiểm tra

Có thể xây dựng một chế độ:

## Cảnh báo vị trí

Người dùng có quyền bật/tắt.

### Khi bật

Điện thoại sử dụng vị trí để phát hiện khi người dùng đi gần một điểm đã được kiểm tra.

Ví dụ:

> 📳 Bạn đang gần khu vực đã từng phát hiện bệnh đạo ôn.

Người dùng có thể chụp ảnh lại để kiểm tra tiếp.

### Khi tắt

Hệ thống không cần liên tục cảnh báo vị trí.

Khi mở ứng dụng, người dùng vẫn có thể xem các điểm trên bản đồ và chủ động chọn nơi cần kiểm tra.

---

# 7. Quản lý tuổi/giai đoạn cây lúa

Không nhất thiết phải huấn luyện AI để đoán chính xác số ngày tuổi của lúa từ một bức ảnh.

Ở phiên bản hiện tại, phương án thực tế là:

## Phương án 1: Người dùng nhập ngày gieo

Ví dụ:

```text
Ngày gieo: 01/08/2026
```

Hệ thống tự tính:

```text
Ngày hiện tại - Ngày gieo
= Tuổi lúa
```

## Phương án 2: Người dùng nhập trực tiếp tuổi lúa

Ví dụ:

```text
Tuổi lúa: 57 ngày
```

Sau đó hệ thống lưu tuổi này cùng với bản ghi ảnh.

Đây là cách phù hợp vì người trồng thường biết ngày gieo hoặc tuổi ruộng của mình.

---

# 8. Có thể nghiên cứu AI xác định tuổi/giai đoạn trong tương lai

Việc xác định tuổi/giai đoạn sinh trưởng từ ảnh có thể được nghiên cứu sau.

Trước khi huấn luyện, cần khảo sát:

- Có công trình hoặc mô hình sẵn có không?
- Mô hình xác định chính xác số ngày tuổi hay chỉ phân loại giai đoạn?
- Có dataset phù hợp không?
- Dataset có ảnh chụp ngoài đồng bằng điện thoại không?
- Độ chính xác thực tế như thế nào?

Nếu chưa có dữ liệu phù hợp, không cần ép dự án phải làm chức năng này.

Chức năng nhập tuổi/ngày gieo vẫn đủ để sản phẩm hoạt động.

---

# 9. Tuổi lúa được liên kết với kết quả bệnh

Điểm quan trọng không phải là “AI biết tuổi lúa” bằng mọi giá.

Điểm quan trọng là:

> **Kết quả bệnh phải được đặt trong bối cảnh tuổi/giai đoạn của cây lúa.**

Ví dụ:

```text
Ảnh
+
GPS
+
Thời gian
+
Tuổi lúa
+
Kết quả bệnh
```

sẽ tạo thành một bản ghi có ý nghĩa hơn:

```text
📍 A3
🌾 57 ngày tuổi
🦠 Đạo ôn
🕐 27/09/2026
```

Sau đó hệ thống có thể tra cứu các thông tin phù hợp với giai đoạn đó.

---

# 10. Knowledge Base và ma trận kiến thức

Không nên để AI tự suy nghĩ toàn bộ khuyến cáo.

Nhóm nên xây dựng một **kho dữ liệu kiến thức về cây lúa**.

Có thể tổ chức theo các trường:

```text
Tuổi/giai đoạn
Bệnh
Mức độ
Triệu chứng
Nội dung cần kiểm tra
Khu vực cần kiểm tra
Khuyến cáo
Điều kiện áp dụng
Nguồn tài liệu
```

Ví dụ về logic:

```text
TUỔI LÚA
+
GIAI ĐOẠN
+
BỆNH
+
MỨC ĐỘ
        ↓
RULE ENGINE
        ↓
KHUYẾN CÁO
```

Ví dụ:

```text
IF
Tuổi lúa = giai đoạn X
AND
Bệnh = Đạo ôn
AND
Mức độ = nhẹ

THEN
Hiển thị nhóm thông tin phù hợp
+
Đề nghị kiểm tra lại lá
+
Đề nghị kiểm tra khu vực xung quanh
```

Những trường hợp đã có quy tắc có thể xử lý **không cần gọi AI**.

---

# 11. Mục tiêu sử dụng AI ít nhất có thể

Kiến trúc ưu tiên:

```text
DATABASE
+
KNOWLEDGE BASE
+
RULE ENGINE
+
YOLOv8
+
AI nâng cao (tùy chọn)
```

Trong đó:

### Database
Lưu toàn bộ dữ liệu.

### Knowledge Base
Lưu kiến thức đã nghiên cứu.

### Rule Engine
Xử lý những trường hợp đã biết.

### YOLOv8
Phân tích ảnh khi cần nhận diện bệnh.

### AI nâng cao
Chỉ dùng khi cần tổng hợp hoặc giải thích những trường hợp phức tạp.

Mục tiêu:

> **Không có AI nâng cao thì hệ thống vẫn hoạt động.**

---

# 12. Kiến trúc hoạt động khi có hoặc không có server

Website Vercel là giao diện chính.

FastAPI + YOLO là AI Engine.

```text
                    VERCEL
              AI RICE WEB APP
                     │
        ┌────────────┼────────────┐
        ▼            ▼            ▼
      MAP          CAMERA       TUỔI LÚA
        │            │            │
        └────────────┼────────────┘
                     ▼
                  DATABASE
                     │
               Có server không?
                 /         \
               Có           Chưa
               │              │
               ▼              ▼
          FastAPI/YOLO     Lưu chờ
               │              │
               ▼              │
           Kết quả ◄───────────┘
```

Nếu FastAPI đang tắt:

- Web vẫn mở.
- Bản đồ vẫn hoạt động.
- Dữ liệu đã lưu vẫn xem được.
- Ảnh mới vẫn có thể được lưu.
- GPS và thời gian vẫn được lưu.
- Ảnh chờ được đánh dấu “chưa phân tích”.

Khi server hoạt động:

- Website kiểm tra trạng thái server.
- Gửi các ảnh đang chờ.
- FastAPI nhận ảnh.
- YOLO phân tích.
- Kết quả được lưu trở lại hồ sơ vị trí.

Đây là cơ chế **lưu trước – phân tích sau**.

---

# 13. Quản lý vòng đời của dữ liệu theo vụ lúa

Dữ liệu không nên tồn tại vĩnh viễn trên bản đồ hoạt động.

Mỗi ruộng có một **vụ lúa**.

```text
Ngày gieo
    ↓
Sinh trưởng
    ↓
Phát hiện/kiểm tra
    ↓
Theo dõi
    ↓
Thu hoạch
    ↓
Đóng vụ
```

Khi vụ kết thúc:

- Không tiếp tục cảnh báo điểm cũ trên bản đồ hoạt động.
- Dữ liệu được chuyển sang kho lưu trữ.
- Vụ mới tạo bộ dữ liệu mới.
- Vị trí có thể được sử dụng lại cho vụ mới.

Không nhất thiết phải xóa dữ liệu cũ ngay.

Có thể lưu:

```text
ACTIVE DATA
→ Vụ hiện tại

ARCHIVE DATA
→ Các vụ trước
```

Sau này có thể dùng dữ liệu cũ để nghiên cứu và cải thiện mô hình.

---

# 14. Dữ liệu cũ trở thành nguồn cải tiến

Dữ liệu cũ không chỉ để lưu lịch sử.

Các bản ghi có thể được phân tích để biết:

- AI nhận diện đúng ở đâu.
- AI nhận diện sai ở đâu.
- Bệnh nào còn yếu.
- Điều kiện ánh sáng nào gây lỗi.
- Góc chụp nào gây lỗi.
- Khoảng cách chụp nào gây lỗi.
- Trường hợp bệnh nào dễ nhầm.

Có thể lập một bảng cải tiến:

| Bệnh | Trường hợp đúng | Trường hợp sai | Nguyên nhân | Dữ liệu cần bổ sung | Hướng cải tiến |
|---|---:|---:|---|---|---|
| Đạo ôn | ... | ... | ... | Ảnh ... | ... |
| Bạc lá | ... | ... | ... | Ảnh ... | ... |
| Sâu cuốn lá | ... | ... | ... | Ảnh ... | ... |

Điểm quan trọng:

> **Không cần tuyên bố mô hình đạt 100%.**

Mục tiêu khoa học là biết mô hình còn sai ở đâu và có phương án cải tiến.

---

# 15. Chu trình cải tiến lâu dài

```text
SỬ DỤNG HỆ THỐNG
       ↓
THU THẬP ẢNH THỰC TẾ
       ↓
GHI NHẬN KẾT QUẢ VÀ LỖI
       ↓
CHỌN DỮ LIỆU KHÓ
       ↓
BỔ SUNG DATASET
       ↓
HUẤN LUYỆN YOLO MỚI
       ↓
ĐÁNH GIÁ
       ↓
ĐƯA MÔ HÌNH MỚI VÀO HỆ THỐNG
       ↓
TIẾP TỤC THU THẬP
```

Như vậy hệ thống có khả năng phát triển qua nhiều vụ lúa.

---

# 16. Điểm mới của sản phẩm

Không nên lấy tuyên bố:

> “AI nhận diện bệnh lúa là công nghệ chưa từng có.”

Nhận diện bệnh cây bằng AI là hướng đã có nhiều nghiên cứu và sản phẩm.

Điểm cần tập trung là **cách tích hợp các thành phần thành một sản phẩm quản lý ruộng lúa theo không gian và thời gian**.

Khung sản phẩm:

```text
📍 VỊ TRÍ
+
🕐 THỜI GIAN
+
🌾 TUỔI/GIAI ĐOẠN
+
📷 ẢNH
+
🤖 KẾT QUẢ AI
+
📚 KNOWLEDGE BASE
+
📋 KHUYẾN CÁO
+
🔄 LỊCH SỬ
```

Từ đó tạo thành:

> **Bản đồ sức khỏe ruộng lúa theo không gian và thời gian.**

Đây là hướng sản phẩm mà nhóm có thể tiếp tục phát triển ngay cả khi mô hình nhận diện bệnh còn được cải thiện.

---

# 17. Phiên bản cần làm trước

Không nên cố hoàn thiện tất cả chức năng cùng lúc.

## Phạm vi phiên bản hiện tại

### Bắt buộc

1. Web AI Rice mới.
2. Bản đồ.
3. GPS.
4. Chụp ảnh.
5. Lưu ảnh.
6. Lưu tọa độ.
7. Lưu thời gian.
8. Nhập ngày gieo hoặc tuổi lúa.
9. Tính tuổi lúa.
10. Gửi ảnh đến FastAPI khi server sẵn sàng.
11. YOLO nhận diện bệnh.
12. Lưu kết quả vào vị trí.
13. Hiển thị marker trên bản đồ.
14. Nhấn marker để xem hồ sơ.
15. Lưu lịch sử các lần kiểm tra.

### Có thể làm tiếp

- Cảnh báo khi đi gần vị trí.
- Khu vực cần kiểm tra.
- Khuyến cáo theo tuổi/giai đoạn.
- Quản lý cán bộ kiểm tra.
- Tuyến đường kiểm tra.
- Dashboard cho hợp tác xã.

### Hướng phát triển tương lai

- AI xác định giai đoạn sinh trưởng từ ảnh.
- Phân tích diễn biến bệnh.
- Dự báo nguy cơ.
- Kết hợp thời tiết.
- Kết hợp cảm biến.
- Tự động chọn dữ liệu khó để huấn luyện.
- So sánh nhiều vụ lúa.
- Hệ thống học từ dữ liệu thực tế.

---

# 18. Khung sản phẩm cuối cùng

```text
                         🌾 AI RICE
                 BẢN ĐỒ SỨC KHỎE RUỘNG LÚA
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
     🗺️ BẢN ĐỒ              📷 KIỂM TRA          🌱 VỤ LÚA
        │                     │                     │
        │                 Ảnh + GPS              Ngày gieo
        │                 + thời gian                │
        │                     │                       ▼
        │                     ▼                  Tuổi lúa
        │                  FastAPI                    │
        │                     │                       │
        │                   YOLOv8                    │
        │                     │                       │
        └─────────────────────┼───────────────────────┘
                              ▼
                       📍 HỒ SƠ VỊ TRÍ
                              │
                 ┌────────────┼────────────┐
                 ▼            ▼            ▼
              Bệnh         Lịch sử      Tuổi lúa
                 │            │            │
                 └────────────┼────────────┘
                              ▼
                       📚 KNOWLEDGE BASE
                              │
                              ▼
                         RULE ENGINE
                              │
                              ▼
                     📋 KHUYẾN CÁO
                              │
                              ▼
                   📍 KHU VỰC CẦN KIỂM TRA
                              │
                              ▼
                         📷 CHỤP LẠI
                              │
                              └────→ LỊCH SỬ
```

# 19. Kết luận định hướng

Đề tài được chuyển từ một hệ thống **nhận diện bệnh trên ảnh** thành một **sản phẩm quản lý và giám sát sức khỏe ruộng lúa theo vị trí, thời gian và giai đoạn sinh trưởng**.

Giá trị cốt lõi không nằm ở việc tuyên bố mô hình AI hoàn hảo. Giá trị nằm ở việc:

> **Mỗi lần kiểm tra tạo ra một dấu vết có vị trí, thời gian, tuổi lúa, ảnh và kết quả. Các dấu vết được liên kết thành lịch sử của từng khu vực trên bản đồ. Từ lịch sử và kho kiến thức, hệ thống xác định thông tin cần hiển thị và khu vực cần kiểm tra tiếp theo.**

Mô hình AI có thể tiếp tục được cải thiện qua dữ liệu thực tế mà không làm thay đổi khung sản phẩm.

Đây là nền tảng để sau này mở rộng sang phân tích giai đoạn sinh trưởng, thời tiết, dự báo nguy cơ, dữ liệu cảm biến và các mô hình AI nâng cao.
