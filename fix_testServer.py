import re

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

new_func = """window.testServer = async function() {
    try {
        let url = (typeof Config !== 'undefined' ? Config.AI_SERVER_URL : null) || CAYLUA_CONFIG.server.baseUrl;
        let newUrl = prompt("Đang kết nối AI Server tại:\\n" + url + "\\n\\nBạn có muốn đổi URL Server không? (Nhập URL mới hoặc để nguyên)", url);
        if(newUrl !== null && newUrl !== url) {
            if(typeof Config !== 'undefined') Config.setConfig(Config.SUPABASE_URL, Config.SUPABASE_ANON_KEY, newUrl);
            CAYLUA_CONFIG.server.baseUrl = newUrl;
            url = newUrl;
        }
        if(newUrl === null) return; // user cancelled
        
        alert("Đang kiểm tra kết nối đến: " + url);
        let res = await fetch(url + '/health', { signal: AbortSignal.timeout(5000) });
        if(res.ok) {
            alert("✅ Server AI Đang Hoạt Động Tốt! Sẵn sàng xử lý ảnh.");
        } else {
            alert("⚠️ Server phản hồi lỗi: " + res.status);
        }
    } catch(e) {
        alert("❌ Server Offline hoặc không thể kết nối: " + e.message + "\\n\\nHãy chắc chắn server đã được bật và đúng địa chỉ.");
    }
}"""

html = re.sub(r'window\.testServer = async function\(\)\s*\{.*?\n\}\n', new_func + '\n', html, flags=re.DOTALL)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
