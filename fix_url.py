import io

path = 'C:\\Users\\ltlie\\Documents\\GIT-DA\\10.Caylua-4.0\\AI_Rice_UX_Prototype_V3_CLICK_POPUP_FINAL.html'
with io.open(path, 'r', encoding='utf-8') as f:
    html = f.read()

html = html.replace('baseUrl: "https://ai.nongnghiepsangtao.io.vn"', 'baseUrl: "http://localhost:8000"')
html = html.replace('placeholder="URL (vd: https://ai.nongnghiepsangtao.io.vn)"', 'placeholder="URL (vd: http://localhost:8000)"')

with io.open(path, 'w', encoding='utf-8') as f:
    f.write(html)
print('Reverted URL')
