import re

# Đọc nội dung HTML hiện tại
with open("AI_Rice_UX_Prototype_V3_CLICK_POPUP_FINAL.html", "r", encoding="utf-8") as f:
    html = f.read()

# Đọc nội dung các function bị mất từ test.js
with open("test.js", "r", encoding="utf-8") as f:
    test_js = f.read()

# Trích xuất đoạn từ function closeCheck đến cuối file test.js
match = re.search(r'(function closeCheck\(\).*?)$', test_js, flags=re.DOTALL)
if match:
    missing_code = match.group(1)
    
    # Ở html hiện tại, tìm "function uuidv4()"
    # Ta sẽ chèn missing_code vào trước function uuidv4()
    
    # Kiểm tra xem closeCheck đã có chưa, nếu có thì loại bỏ để không bị trùng
    if "function closeCheck()" in html:
        # html = html.replace("function closeCheck()", missing_code + "\nfunction closeCheck()")
        # Wait, closeCheck is already at the end of new_savecheck.
        html = html.replace("function closeCheck(){\n", "")
        html = html.replace("function closeCheck() {\n", "")
        html = html.replace("function closeCheck()", "") # remove all existing closeCheck
        
    html = html.replace("function uuidv4() {", missing_code + "\n\nfunction uuidv4() {")
    
    # Clean up double closeCheck if any
    
    with open("AI_Rice_UX_Prototype_V3_CLICK_POPUP_FINAL.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("Khôi phục functions thành công.")
else:
    print("Không tìm thấy functions cần khôi phục trong test.js")
