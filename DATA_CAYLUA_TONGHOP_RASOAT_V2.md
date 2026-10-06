# Dữ liệu bệnh và rối loạn trên cây lúa — bản rà soát V2

## Mục đích
Bản này được xây dựng lại từ dữ liệu gốc, sau đó chuẩn hóa theo tài liệu chẩn đoán bệnh lúa của International Rice Research Institute (IRRI) và các tài liệu chuyên ngành. IRRI có tài liệu tổng hợp khoảng 80 bệnh hại lúa, gồm nhóm nấm, vi khuẩn, virus/phytoplasma và tuyến trùng; tài liệu chẩn đoán bệnh phổ biến cũng liệt kê đạo ôn, khô vằn, đốm nâu, thối bẹ, lúa von, than giả, bạc lá, sọc lá vi khuẩn, tungro, vàng lùn/lúa cỏ và lùn xoắn lá. 

**Lưu ý quan trọng cho AI nhận dạng ảnh:** “bệnh” và “rối loạn sinh lý/dinh dưỡng” không nên trộn thành một nhãn bệnh duy nhất. Các rối loạn như ngộ độc hữu cơ, ngộ độc sắt và thiếu Zn có thể có hình thái giống bệnh; nên giữ chúng thành nhóm riêng và, nếu có thể, dùng thêm dữ liệu ruộng/đất để xác nhận.

## Các chỉnh sửa quan trọng so với bản gốc
1. Tách **vàng lùn (grassy stunt)** và **lùn xoắn lá (ragged stunt)** thành hai bệnh riêng; cả hai đều liên quan rầy nâu nhưng là hai bệnh virus khác nhau.
2. Sửa tác nhân bạc lá thành **Xanthomonas oryzae pv. oryzae** và sọc lá vi khuẩn thành **Xanthomonas oryzae pv. oryzicola**.
3. Bổ sung các bệnh quan trọng còn thiếu: **đốm nâu, thối bẹ, thối thân, than giả, tungro**.
4. Với bệnh virus, ghi rõ **virus + môi giới truyền bệnh**, không mô tả chung là “virus truyền qua rầy”.
5. Không coi thuốc BVTV là “thuốc điều trị” theo nghĩa chữa khỏi mọi bệnh. Với virus không có thuốc chữa cây đã nhiễm; biện pháp chính là quản lý vector, nguồn bệnh và thời vụ.
6. Phần “ngộ độc hữu cơ” được chỉnh lại: không gán CH₄ đơn độc là tác nhân gây độc; điều kiện yếm khí và các sản phẩm phân hủy như H₂S/acid hữu cơ mới là cách mô tả phù hợp hơn.
7. Bổ sung trường **differential** (chẩn đoán phân biệt) và **ai_visual_features** để phù hợp trực tiếp với dự án nhận dạng bệnh bằng YOLO/AI.

## Danh mục nhãn đề xuất cho bộ dữ liệu ảnh

| ID | Nhãn tiếng Việt | Nhóm | Tác nhân |
|---|---|---|---|
| `fungal_dao_on` | Bệnh đạo ôn | Nấm | Pyricularia oryzae |
| `fungal_kho_van` | Bệnh khô vằn | Nấm | Rhizoctonia solani |
| `fungal_brown_spot` | Bệnh đốm nâu | Nấm | Bipolaris oryzae |
| `fungal_sheath_rot` | Bệnh thối bẹ | Nấm | Sarocladium oryzae |
| `fungal_stem_rot` | Bệnh thối thân | Nấm | Sclerotium oryzae |
| `fungal_bakanae` | Bệnh lúa von | Nấm | Fusarium fujikuroi |
| `fungal_false_smut` | Bệnh lem lép hạt giả than (bệnh than giả) | Nấm | Ustilaginoidea virens |
| `bacterial_bac_la` | Bệnh bạc lá (cháy bìa lá) | Vi khuẩn | Xanthomonas oryzae pv. oryzae |
| `bacterial_leaf_streak` | Bệnh sọc lá vi khuẩn | Vi khuẩn | Xanthomonas oryzae pv. oryzicola |
| `viral_grassy_stunt` | Bệnh vàng lùn (lúa cỏ) | Virus | Rice grassy stunt virus (RGSV) |
| `viral_ragged_stunt` | Bệnh lùn xoắn lá | Virus | Rice ragged stunt virus (RRSV) |
| `viral_srbsv` | Bệnh lùn sọc đen phương Nam | Virus | Southern rice black-streaked dwarf virus (SRBSDV) |
| `viral_tungro` | Bệnh vàng lá vàng lùn (Tungro) | Virus | Rice tungro bacilliform virus (RTBV) + Rice tungro spherical virus (RTSV) |
| `physio_organic_toxicity` | Ngộ độc hữu cơ / nghẹt rễ | Rối loạn sinh lý | điều kiện yếm khí và sản phẩm phân hủy hữu cơ; H₂S và các acid hữu cơ có thể góp phần gây độc |
| `physio_iron_toxicity` | Ngộ độc sắt (phèn sắt) | Rối loạn sinh lý | Fe²⁺ hòa tan cao trong điều kiện đất ngập, thường liên quan đất phèn/đất có Fe cao |
| `physio_zinc_deficiency` | Thiếu kẽm (Zn) | Rối loạn dinh dưỡng | cung cấp Zn trong đất thấp hoặc điều kiện đất làm giảm khả năng hấp thu Zn |

## Dữ liệu chi tiết chuẩn hóa

```json
[
  {
    "id": "fungal_dao_on",
    "name_vi": "Bệnh đạo ôn",
    "name_en": "Rice blast",
    "group": "Nấm",
    "causal_agent": "Pyricularia oryzae",
    "target_organs": [
      "lá",
      "đốt thân",
      "cổ bông",
      "bông/hạt"
    ],
    "symptoms": [
      "Lá có đốm hình thoi/mắt én, tâm xám trắng đến xám tro, mép nâu đỏ hoặc nâu sẫm; các vết có thể liên kết làm cháy lá.",
      "Đạo ôn cổ bông làm vùng cổ bông/gié bệnh nâu đen, bông phía trên có thể trắng bạc và hạt lép.",
      "Có thể xuất hiện đạo ôn đốt ở các đốt thân."
    ],
    "favorable_conditions": [
      "ẩm độ cao, thời tiết mát/ẩm, sương kéo dài",
      "bón thừa đạm và ruộng quá rậm"
    ],
    "management": [
      "dùng giống sạch bệnh và giống có tính kháng phù hợp",
      "bón đạm cân đối, tránh thừa N; quản lý mật độ và dinh dưỡng hợp lý",
      "theo dõi đặc biệt giai đoạn đẻ nhánh–làm đòng và trổ; xử lý thuốc BVTV chỉ theo nhãn thuốc và hướng dẫn địa phương"
    ],
    "differential": [
      "đốm nâu",
      "cháy lá do nguyên nhân dinh dưỡng"
    ],
    "ai_visual_features": [
      "đốm hình thoi",
      "tâm xám",
      "viền nâu",
      "đạo ôn cổ bông"
    ]
  },
  {
    "id": "fungal_kho_van",
    "name_vi": "Bệnh khô vằn",
    "name_en": "Sheath blight",
    "group": "Nấm",
    "causal_agent": "Rhizoctonia solani",
    "target_organs": [
      "bẹ lá",
      "lá",
      "gốc thân"
    ],
    "symptoms": [
      "Vết bệnh hình bầu dục/ellip trên bẹ lá, thường bắt đầu gần mặt nước hoặc sát đất; màu xanh xám, sau đó trắng xám với mép nâu.",
      "Vết bệnh lan lên bẹ và lá phía trên, có thể lan sang các dảnh lân cận; cây bị nặng giảm diện tích lá hữu hiệu."
    ],
    "favorable_conditions": [
      "nhiệt độ khoảng 28–32°C",
      "ẩm độ tán cao",
      "ruộng gieo/cấy dày, bón nhiều đạm"
    ],
    "management": [
      "gieo/cấy với mật độ hợp lý, giữ tán thông thoáng",
      "bón dinh dưỡng cân đối, tránh thừa đạm",
      "quản lý cỏ dại và tàn dư; điều tiết nước phù hợp",
      "thuốc BVTV chỉ sử dụng theo đăng ký và nhãn tại địa phương"
    ],
    "differential": [
      "thối thân",
      "sâu đục thân"
    ],
    "ai_visual_features": [
      "vết oval trên bẹ",
      "tâm xám trắng",
      "mép nâu",
      "lan từ bẹ lên lá"
    ]
  },
  {
    "id": "fungal_brown_spot",
    "name_vi": "Bệnh đốm nâu",
    "name_en": "Brown spot",
    "group": "Nấm",
    "causal_agent": "Bipolaris oryzae",
    "target_organs": [
      "lá",
      "vỏ trấu",
      "hạt"
    ],
    "symptoms": [
      "Đốm tròn hoặc bầu dục màu nâu trên lá; thường có tâm nhạt hơn và có thể có quầng vàng.",
      "Có thể gây đốm/discoloration trên hạt và làm giảm chất lượng hạt trong trường hợp nặng."
    ],
    "favorable_conditions": [
      "cây sinh trưởng kém hoặc thiếu dinh dưỡng, đặc biệt stress dinh dưỡng",
      "ẩm độ cao và thời tiết thuận lợi cho bệnh"
    ],
    "management": [
      "dùng hạt giống sạch và xử lý hạt khi cần",
      "bón dinh dưỡng cân đối, tránh để cây suy kiệt",
      "quản lý nước và đồng ruộng hợp lý"
    ],
    "differential": [
      "đạo ôn lá",
      "đốm sọc nâu"
    ],
    "ai_visual_features": [
      "đốm nâu tròn/bầu dục",
      "nhiều đốm trên phiến lá",
      "đốm trên hạt"
    ]
  },
  {
    "id": "fungal_sheath_rot",
    "name_vi": "Bệnh thối bẹ",
    "name_en": "Sheath rot",
    "group": "Nấm",
    "causal_agent": "Sarocladium oryzae",
    "target_organs": [
      "bẹ lá",
      "lá cờ",
      "cổ bông"
    ],
    "symptoms": [
      "Vết bệnh hình bầu dục hoặc không đều, màu nâu xám trên bẹ lá, thường ở bẹ phía trên.",
      "Bẹ bệnh có thể thối, lá cờ bị ảnh hưởng; bông có thể trổ không hoàn toàn và hạt lép khi bệnh nặng."
    ],
    "favorable_conditions": [
      "ẩm độ cao",
      "tổn thương bẹ và điều kiện tán rậm"
    ],
    "management": [
      "dùng hạt giống sạch, vệ sinh đồng ruộng",
      "quản lý mật độ và dinh dưỡng hợp lý",
      "kiểm soát sâu gây tổn thương và quản lý bệnh theo khuyến cáo địa phương"
    ],
    "differential": [
      "khô vằn",
      "thối thân"
    ],
    "ai_visual_features": [
      "vết nâu trên bẹ trên",
      "lá cờ bị ảnh hưởng",
      "bẹ thối"
    ]
  },
  {
    "id": "fungal_stem_rot",
    "name_vi": "Bệnh thối thân",
    "name_en": "Stem rot",
    "group": "Nấm",
    "causal_agent": "Sclerotium oryzae",
    "target_organs": [
      "thân",
      "bẹ lá",
      "gốc"
    ],
    "symptoms": [
      "Vết bệnh màu đen/nâu trên bẹ và thân, thường gần mực nước; có thể làm thân yếu, đổ ngã.",
      "Mô bên trong thân bị tổn thương; có thể hình thành hạch nấm nhỏ màu đen."
    ],
    "favorable_conditions": [
      "ruộng ngập kéo dài",
      "tàn dư bệnh tồn tại trong ruộng"
    ],
    "management": [
      "quản lý nước và dinh dưỡng hợp lý",
      "quản lý tàn dư sau thu hoạch và cỏ dại ký chủ",
      "không lạm dụng đạm"
    ],
    "differential": [
      "khô vằn",
      "thối bẹ"
    ],
    "ai_visual_features": [
      "tổn thương thân/bẹ gần mực nước",
      "đốm đen nâu",
      "thân yếu/đổ"
    ]
  },
  {
    "id": "fungal_bakanae",
    "name_vi": "Bệnh lúa von",
    "name_en": "Bakanae",
    "group": "Nấm",
    "causal_agent": "Fusarium fujikuroi",
    "target_organs": [
      "cây mạ",
      "thân",
      "rễ"
    ],
    "symptoms": [
      "Cây bệnh thường vươn cao bất thường, thân mảnh, lá hẹp; màu xanh nhạt/vàng nhạt.",
      "Rễ và gốc có thể bị thối; cây bệnh có thể chết hoặc khô trước trổ. Một số cây sống sót vẫn cao bất thường."
    ],
    "favorable_conditions": [
      "nguồn hạt giống nhiễm bệnh",
      "điều kiện thuận lợi cho nấm trong giai đoạn hạt giống/mạ"
    ],
    "management": [
      "ưu tiên hạt giống sạch bệnh",
      "xử lý hạt giống theo quy trình/thuốc được đăng ký",
      "loại bỏ cây bệnh rõ ràng khỏi ruộng/mạ, vệ sinh nguồn giống"
    ],
    "differential": [
      "cây vươn do điều kiện sinh trưởng",
      "thiếu dinh dưỡng"
    ],
    "ai_visual_features": [
      "cây cao vống bất thường",
      "thân mảnh",
      "lá hẹp",
      "cây bệnh nổi bật so với quần thể"
    ]
  },
  {
    "id": "fungal_false_smut",
    "name_vi": "Bệnh lem lép hạt giả than (bệnh than giả)",
    "name_en": "False smut",
    "group": "Nấm",
    "causal_agent": "Ustilaginoidea virens",
    "target_organs": [
      "hạt",
      "bông"
    ],
    "symptoms": [
      "Một số hạt bị thay thế bởi khối bào tử dạng cầu, ban đầu vàng cam rồi chuyển xanh ô-liu đến xanh nâu.",
      "Thường dễ nhận biết ở giai đoạn trổ–chín khi các khối than giả nổi bật trên bông."
    ],
    "favorable_conditions": [
      "ẩm độ cao quanh thời kỳ trổ",
      "điều kiện ruộng và dinh dưỡng thuận lợi cho bệnh"
    ],
    "management": [
      "dùng hạt giống sạch",
      "quản lý dinh dưỡng, đặc biệt tránh bón đạm quá mức",
      "theo dõi giai đoạn làm đòng–trổ và áp dụng thuốc được đăng ký nếu cần"
    ],
    "differential": [
      "lem lép hạt do nấm khác",
      "hạt bị côn trùng gây hại"
    ],
    "ai_visual_features": [
      "khối cầu trên hạt",
      "màu vàng cam/xanh ô-liu",
      "tập trung trên bông"
    ]
  },
  {
    "id": "bacterial_bac_la",
    "name_vi": "Bệnh bạc lá (cháy bìa lá)",
    "name_en": "Bacterial leaf blight",
    "group": "Vi khuẩn",
    "causal_agent": "Xanthomonas oryzae pv. oryzae",
    "vector_or_spread": "nước, mưa gió và vết thương trên cây; vi khuẩn có thể lan theo dịch tiết",
    "target_organs": [
      "lá",
      "mạch dẫn"
    ],
    "symptoms": [
      "Vết bệnh thường bắt đầu từ mép hoặc chóp lá, lan dọc theo mép và gân lá; mô bệnh vàng úa rồi trắng xám/nâu nhạt khi khô.",
      "Khi ẩm có thể quan sát dịch vi khuẩn ở mép/vết bệnh. Cây non bị nhiễm nặng có thể héo nhanh (kresek)."
    ],
    "favorable_conditions": [
      "mưa gió, ẩm độ cao",
      "ruộng thừa đạm và cây có vết thương"
    ],
    "management": [
      "dùng giống có tính kháng phù hợp và hạt giống sạch",
      "bón đạm cân đối, tránh thừa N",
      "hạn chế gây vết thương và lây lan cơ giới khi ruộng ướt",
      "không xem thuốc kháng sinh/diệt khuẩn là biện pháp thay thế quản lý tổng hợp; chỉ dùng sản phẩm được đăng ký và theo nhãn"
    ],
    "differential": [
      "đạo ôn lá",
      "cháy lá do thiếu dinh dưỡng"
    ],
    "ai_visual_features": [
      "bắt đầu từ mép/chóp lá",
      "vệt dài theo mép/gân",
      "lá cháy trắng xám"
    ]
  },
  {
    "id": "bacterial_leaf_streak",
    "name_vi": "Bệnh sọc lá vi khuẩn",
    "name_en": "Bacterial leaf streak",
    "group": "Vi khuẩn",
    "causal_agent": "Xanthomonas oryzae pv. oryzicola",
    "target_organs": [
      "lá"
    ],
    "symptoms": [
      "Các sọc hẹp, trong mờ đến vàng nâu chạy theo mô lá; nhiều vết có thể hợp lại.",
      "Trong điều kiện ẩm, có thể thấy giọt dịch vi khuẩn trên bề mặt lá."
    ],
    "favorable_conditions": [
      "nhiệt độ/ẩm độ cao",
      "mưa và gió tạo điều kiện lan truyền"
    ],
    "management": [
      "hạt giống sạch, vệ sinh đồng ruộng",
      "bón phân cân đối",
      "tránh thao tác gây xây xát lá khi ruộng ướt"
    ],
    "differential": [
      "bạc lá",
      "đốm nâu"
    ],
    "ai_visual_features": [
      "sọc hẹp",
      "mờ trong",
      "chạy dọc lá",
      "dịch vi khuẩn khi ẩm"
    ]
  },
  {
    "id": "viral_grassy_stunt",
    "name_vi": "Bệnh vàng lùn (lúa cỏ)",
    "name_en": "Grassy stunt",
    "group": "Virus",
    "causal_agent": "Rice grassy stunt virus (RGSV)",
    "vector_or_spread": "Rầy nâu Nilaparvata lugens",
    "target_organs": [
      "toàn cây",
      "lá"
    ],
    "symptoms": [
      "Cây lùn, đẻ nhánh nhiều, hình thái bụi; lá thường vàng từ lá già và cây suy yếu.",
      "Triệu chứng quần thể không đồng đều; bệnh gắn chặt với sự hiện diện và di chuyển của rầy nâu."
    ],
    "favorable_conditions": [
      "nguồn rầy nâu mang virus",
      "gieo trồng liên tục tạo cầu xanh cho rầy và virus"
    ],
    "management": [
      "không có thuốc chữa cây đã nhiễm virus",
      "quản lý rầy nâu theo IPM và hướng dẫn địa phương",
      "gieo sạ đồng loạt, né rầy theo lịch địa phương; loại bỏ nguồn cây bệnh khi phù hợp"
    ],
    "differential": [
      "thiếu đạm",
      "ngộ độc hoặc bệnh rễ gây vàng lùn"
    ],
    "ai_visual_features": [
      "lùn",
      "đẻ nhánh nhiều",
      "vàng lá",
      "bụi cây dạng cỏ"
    ]
  },
  {
    "id": "viral_ragged_stunt",
    "name_vi": "Bệnh lùn xoắn lá",
    "name_en": "Ragged stunt",
    "group": "Virus",
    "causal_agent": "Rice ragged stunt virus (RRSV)",
    "vector_or_spread": "Rầy nâu Nilaparvata lugens",
    "target_organs": [
      "toàn cây",
      "lá"
    ],
    "symptoms": [
      "Cây lùn, lá xoắn hoặc biến dạng; mép lá có thể rách/xẻ tua, gân lá có thể sưng.",
      "Cây đẻ nhánh bất thường và sinh trưởng kém; triệu chứng có thể xuất hiện thành ổ trong ruộng."
    ],
    "favorable_conditions": [
      "rầy nâu mang virus",
      "ruộng có nguồn bệnh và lúa gối vụ"
    ],
    "management": [
      "không có thuốc chữa cây đã nhiễm virus",
      "quản lý rầy nâu theo IPM; vệ sinh đồng ruộng và né rầy",
      "không giữ lúa chét làm cầu nối giữa các vụ"
    ],
    "differential": [
      "tổn thương cơ giới",
      "sâu hại gây rách lá",
      "vàng lùn"
    ],
    "ai_visual_features": [
      "lùn",
      "lá xoắn",
      "mép lá rách/xẻ",
      "gân lá sưng"
    ]
  },
  {
    "id": "viral_srbsv",
    "name_vi": "Bệnh lùn sọc đen phương Nam",
    "name_en": "Southern rice black-streaked dwarf",
    "group": "Virus",
    "causal_agent": "Southern rice black-streaked dwarf virus (SRBSDV)",
    "vector_or_spread": "Rầy lưng trắng Sogatella furcifera",
    "target_organs": [
      "toàn cây",
      "thân",
      "lá"
    ],
    "symptoms": [
      "Cây lùn, lá xanh đậm; gân lá có thể sưng và xuất hiện các u/sọc màu nâu đen ở mặt dưới bẹ/gân hoặc thân.",
      "Bệnh thường tạo ổ cây lùn trong ruộng và làm giảm sinh trưởng, trổ kém."
    ],
    "favorable_conditions": [
      "nguồn rầy lưng trắng mang virus",
      "ruộng có cầu xanh và mật độ vector cao"
    ],
    "management": [
      "không có thuốc chữa cây đã nhiễm",
      "quản lý rầy lưng trắng theo IPM",
      "gieo sạ né thời điểm vector cao theo khuyến cáo địa phương; loại bỏ cây bệnh khi phù hợp"
    ],
    "differential": [
      "lùn xoắn lá",
      "thiếu dinh dưỡng"
    ],
    "ai_visual_features": [
      "cây lùn",
      "lá xanh đậm",
      "sọc/u đen ở gân hoặc bẹ"
    ]
  },
  {
    "id": "viral_tungro",
    "name_vi": "Bệnh vàng lá vàng lùn (Tungro)",
    "name_en": "Rice tungro",
    "group": "Virus",
    "causal_agent": "Rice tungro bacilliform virus (RTBV) + Rice tungro spherical virus (RTSV)",
    "vector_or_spread": "rầy xanh/leafhopper, đặc biệt Nephotettix spp.",
    "target_organs": [
      "lá",
      "toàn cây"
    ],
    "symptoms": [
      "Cây lúa thấp hơn bình thường, lá vàng đến vàng cam, đẻ nhánh giảm; bệnh nặng làm trổ muộn hoặc hạt lép.",
      "Màu vàng thường bắt đầu ở chóp lá và lan xuống; mức độ phụ thuộc giống và tổ hợp virus."
    ],
    "favorable_conditions": [
      "vector rầy xanh hiện diện và có nguồn virus",
      "lúa liên tục tạo nguồn ký chủ"
    ],
    "management": [
      "dùng giống phù hợp và giống sạch",
      "quản lý rầy xanh/vector theo IPM",
      "vệ sinh đồng ruộng và đồng bộ thời vụ"
    ],
    "differential": [
      "thiếu đạm",
      "vàng lùn do RGSV"
    ],
    "ai_visual_features": [
      "vàng lá",
      "lùn",
      "giảm đẻ nhánh",
      "triệu chứng toàn cây"
    ]
  },
  {
    "id": "physio_organic_toxicity",
    "name_vi": "Ngộ độc hữu cơ / nghẹt rễ",
    "name_en": "Organic matter toxicity / root suffocation",
    "group": "Rối loạn sinh lý",
    "causal_agent": "điều kiện yếm khí và sản phẩm phân hủy hữu cơ; H₂S và các acid hữu cơ có thể góp phần gây độc",
    "target_organs": [
      "rễ",
      "toàn cây"
    ],
    "symptoms": [
      "Rễ kém phát triển, thâm đen hoặc có mùi bất thường; cây sinh trưởng chậm, đẻ nhánh kém, lá vàng/đỏ tùy mức độ.",
      "Không nên chẩn đoán chỉ dựa vào lá; cần kiểm tra rễ, nước, tàn dư hữu cơ và điều kiện đất."
    ],
    "favorable_conditions": [
      "rơm rạ/hữu cơ phân hủy mạnh trong đất ngập",
      "thoát nước và thông khí đất kém"
    ],
    "management": [
      "quản lý rơm rạ trước gieo sạ, tránh vùi lượng hữu cơ lớn ngay sát thời điểm gieo nếu điều kiện không phù hợp",
      "điều tiết nước, tạo điều kiện thông khí và phục hồi rễ",
      "bón dinh dưỡng cân đối; chỉ bổ sung chất cải tạo theo kết quả đánh giá đất"
    ],
    "differential": [
      "thối rễ do nấm",
      "thiếu dinh dưỡng",
      "ngộ độc Fe"
    ],
    "ai_visual_features": [
      "vàng lúa thành mảng",
      "rễ đen/kém phát triển",
      "điều kiện ruộng ngập và nhiều hữu cơ"
    ]
  },
  {
    "id": "physio_iron_toxicity",
    "name_vi": "Ngộ độc sắt (phèn sắt)",
    "name_en": "Iron toxicity",
    "group": "Rối loạn sinh lý",
    "causal_agent": "Fe²⁺ hòa tan cao trong điều kiện đất ngập, thường liên quan đất phèn/đất có Fe cao",
    "target_organs": [
      "rễ",
      "lá"
    ],
    "symptoms": [
      "Rễ có thể phủ lớp màu nâu đen do Fe oxy hóa ở bề mặt; cây sinh trưởng kém.",
      "Lá già có thể chuyển màu đồng/đỏ nâu và cây đẻ nhánh kém trong trường hợp nặng."
    ],
    "favorable_conditions": [
      "đất phèn, đất giàu sắt",
      "ngập kéo dài và điều kiện làm tăng Fe²⁺ hòa tan"
    ],
    "management": [
      "quản lý nước và cải thiện điều kiện đất phù hợp",
      "bón vôi/chất cải tạo theo phân tích đất và khuyến cáo kỹ thuật",
      "bón dinh dưỡng cân đối, chọn giống thích hợp vùng đất phèn"
    ],
    "differential": [
      "ngộ độc hữu cơ",
      "thiếu dinh dưỡng",
      "bệnh rễ"
    ],
    "ai_visual_features": [
      "lá đồng/đỏ nâu",
      "rễ phủ nâu đen",
      "ruộng đất phèn"
    ]
  },
  {
    "id": "physio_zinc_deficiency",
    "name_vi": "Thiếu kẽm (Zn)",
    "name_en": "Zinc deficiency",
    "group": "Rối loạn dinh dưỡng",
    "causal_agent": "cung cấp Zn trong đất thấp hoặc điều kiện đất làm giảm khả năng hấp thu Zn",
    "target_organs": [
      "lá",
      "toàn cây"
    ],
    "symptoms": [
      "Cây lùn, sinh trưởng chậm; có thể xuất hiện các đốm nâu nhỏ trên lá và ruộng mọc không đều.",
      "Triệu chứng có thể giống thiếu dinh dưỡng khác nên cần kết hợp phân tích đất/lá khi cần."
    ],
    "favorable_conditions": [
      "đất có Zn dễ tiêu thấp",
      "điều kiện ngập liên tục có thể làm giảm khả năng hấp thu Zn"
    ],
    "management": [
      "bổ sung Zn theo nhu cầu và kết quả đánh giá đất",
      "bón dinh dưỡng cân đối và quản lý nước hợp lý"
    ],
    "differential": [
      "thiếu N",
      "thiếu Fe",
      "bệnh rễ"
    ],
    "ai_visual_features": [
      "cây lùn",
      "đốm nâu nhỏ",
      "ruộng mọc không đều"
    ]
  }
]
```

## Nguồn đối chiếu chính
- IRRI Rice Diseases Online Resource: tổng hợp 80 bệnh hại lúa và phân loại theo nấm, vi khuẩn, virus/phytoplasma, tuyến trùng.
- IRRI, Diagnostic of Common Diseases of Rice: tài liệu chẩn đoán triệu chứng và tác nhân của các bệnh phổ biến.
- IRRI Rice Knowledge Bank: Sheath Blight và tài liệu quản lý dinh dưỡng/giống.
- Cục Trồng trọt và Bảo vệ thực vật Việt Nam: tài liệu về lùn sọc đen phương Nam và rầy lưng trắng; danh mục thuốc BVTV đăng ký tại Việt Nam.
