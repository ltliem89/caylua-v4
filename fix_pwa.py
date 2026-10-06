import io
import re

path = 'C:\\Users\\ltlie\\Documents\\GIT-DA\\10.Caylua-4.0\\AI_Rice_UX_Prototype_V3_CLICK_POPUP_FINAL.html'
with io.open(path, 'r', encoding='utf-8') as f:
    html = f.read()

# Add manifest
if 'manifest.json' not in html:
    html = html.replace('<title>', '<link rel="manifest" href="./manifest.json">\n<title>')

# Register service worker in the JS
sw_registration = """
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('./sw.js').then(reg => {
      console.log('SW registered!', reg);
    }).catch(err => console.log('SW registration failed', err));
  });
}
"""
if 'serviceWorker.register' not in html:
    html = html.replace('// Bootstrap', sw_registration + '\n// Bootstrap')

with io.open(path, 'w', encoding='utf-8') as f:
    f.write(html)
print('PWA elements injected')
