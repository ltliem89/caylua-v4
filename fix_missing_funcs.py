import re

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Implement checkAIHealth, syncQueue if missing
js_code = """
window.checkAIHealth = async function() {
    try {
        let url = (typeof Config !== 'undefined' ? Config.AI_SERVER_URL : null) || CAYLUA_CONFIG.server.baseUrl;
        let res = await fetch(url + '/health', { signal: AbortSignal.timeout(3000) });
        if(res.ok) {
            window.AppState = window.AppState || {};
            window.AppState.ai = 'online';
        } else {
            window.AppState = window.AppState || {};
            window.AppState.ai = 'offline';
        }
    } catch(e) {
        window.AppState = window.AppState || {};
        window.AppState.ai = 'offline';
    }
}

window.syncQueue = function() {
    if(typeof SyncService !== 'undefined') SyncService.processQueue();
}

window.testServer = async function() {
    try {
        let url = (typeof Config !== 'undefined' ? Config.AI_SERVER_URL : null) || CAYLUA_CONFIG.server.baseUrl;
        alert("Đang kiểm tra kết nối đến: " + url);
        let res = await fetch(url + '/health', { signal: AbortSignal.timeout(5000) });
        if(res.ok) {
            alert("✅ Server AI Đang Hoạt Động Tốt! Sẵn sàng xử lý ảnh.");
        } else {
            alert("⚠️ Server phản hồi lỗi: " + res.status);
        }
    } catch(e) {
        alert("❌ Server Offline hoặc không thể kết nối: " + e.message + "\\n\\nHãy chắc chắn server đã được bật.");
    }
}
"""

if 'window.checkAIHealth =' not in html:
    html = html.replace('// Bootstrap', js_code + '\n// Bootstrap')

# Add testServer button to tools
if 'testServer()' not in html:
    html = html.replace('<button onclick="startTractorSim()"', '<button onclick="testServer()" title="Kiểm tra kết nối Server" style="background:#fef08a">📡</button><button onclick="startTractorSim()"')

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
