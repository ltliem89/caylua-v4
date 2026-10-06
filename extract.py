import io
with io.open('C:\\Users\\ltlie\\Documents\\GIT-DA\\10.Caylua-4.0\\AI_Rice_UX_Prototype_V3_CLICK_POPUP_FINAL.html', 'r', encoding='utf-8') as f:
    html = f.read()

# find all scripts
import re
scripts = re.findall(r'<script>(.*?)</script>', html, re.DOTALL)
with io.open('C:\\Users\\ltlie\\Documents\\GIT-DA\\10.Caylua-4.0\\test.js', 'w', encoding='utf-8') as fw:
    for s in scripts:
        fw.write(s)
