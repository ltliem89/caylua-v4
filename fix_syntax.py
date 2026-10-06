import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace any newlines inside string concatenations that break JS
# Wait, this might be tricky with regex. Let's find specific ones.

pattern = r'alert\("❌ Server Offline hoặc không thể kết nối: "\s*\+\s*e\.message\s*\+\s*"[\s\S]*?\(Bạn đang ở trạng thái AI Mode: "\s*\+\s*CAYLUA_CONFIG\.aiMode\s*\+\s*"\)"\);'
# Actually, I'll just remove all literal newlines that are directly inside strings by finding lines that start with unclosed strings.
# But it's safer to just fix this specific one.

content = re.sub(
    r'alert\("❌ Server Offline hoặc không thể kết nối: "\s*\+\s*e\.message\s*\+\s*"\s*\(Bạn đang ở trạng thái AI Mode: "\s*\+\s*CAYLUA_CONFIG\.aiMode\s*\+\s*"\)"\);',
    r'alert(`❌ Server Offline hoặc không thể kết nối: ${e.message}\n(Bạn đang ở trạng thái AI Mode: ${CAYLUA_CONFIG.aiMode})`);',
    content
)

# And another one in shareToZalo?
content = content.replace('`🌾 BÁO CÁO BỆNH CÂY LÚA - AI RICE 4.0\\n` +', '`🌾 BÁO CÁO BỆNH CÂY LÚA - AI RICE 4.0\\n` +') # that one uses backticks so it's fine.

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("Done")
