import io

path = 'C:\\Users\\ltlie\\Documents\\GIT-DA\\10.Caylua-4.0\\AI_Rice_UX_Prototype_V3_CLICK_POPUP_FINAL.html'
with io.open(path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Update baseUrl to production URL
html = html.replace('baseUrl: "http://localhost:8000"', 'baseUrl: "https://ai.nongnghiepsangtao.io.vn"')
html = html.replace('placeholder="URL (vd: http://localhost:8000)"', 'placeholder="URL (vd: https://ai.nongnghiepsangtao.io.vn)"')

# 2. Add 'Test Connection' button in Settings
test_btn = '''<button onclick="checkAIHealth().then(() => alert('Trạng thái AI hiện tại: ' + AppState.ai))" style="padding:5px 10px; border-radius:5px; border:1px solid #ddd; background:#f0fdf4; margin-top:5px;">🔄 Kiểm tra kết nối AI</button>'''
if 'Kiểm tra kết nối AI' not in html:
    html = html.replace('</p>\n    <b>🖥️ Server CAY LÚA</b>', '</p>\n    <div style="display:flex; justify-content:space-between; align-items:center;"><b>🖥️ Server CAY LÚA</b>' + test_btn + '</div>')

# 3. Auto-submit on change
# Change onchange="showCheck()" to onchange="showCheck(); setTimeout(saveCheck, 300)"
html = html.replace('onchange="showCheck()"', 'onchange="showCheck(); setTimeout(saveCheck, 300)"')

# Disable or rename the manual button since it's auto-submitting
html = html.replace('<button class="save" onclick="saveCheck()">🔍 Phân tích & Lưu</button>', '<button class="save" onclick="saveCheck()" style="display:none">🔍 Phân tích & Lưu</button>')
html = html.replace('<label>Ngày tuổi lúa (nếu biết)</label>', '<label>Ngày tuổi lúa (nếu biết) - Tự động phân tích sau 0.3s...</label>')


with io.open(path, 'w', encoding='utf-8') as f:
    f.write(html)
print('Updated HTML successfully!')
