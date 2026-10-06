const express = require('express');
const cors = require('cors');

const app = express();
const port = 3000;

// Middleware để parse JSON và cho phép Cross-Origin (CORS)
app.use(express.json());
app.use(cors());

// Tạo API endpoint (POST request)
app.post('/api/tinh-tong', (req, res) => {
    // 1. Nhận dữ liệu từ web
    const soA = req.body.soA;
    const soB = req.body.soB;

    // 2. Xử lý dữ liệu
    const tong = soA + soB;
    const thongBao = `Server đã nhận ${soA} và ${soB}. Tổng là: ${tong}`;

    // 3. Gửi kết quả về cho web
    res.json({ 
        thanhCong: true, 
        ketQua: tong,
        tinNhan: thongBao
    });
});

app.listen(port, () => {
    console.log(`Server đang chạy tại http://localhost:${port}`);
});
