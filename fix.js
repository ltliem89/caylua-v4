const fs = require('fs');
let html = fs.readFileSync('index.html', 'utf8');

// The problematic string starts with "alert(\"❌ Server Offline"
let idx = html.indexOf('alert("❌ Server Offline');
if (idx !== -1) {
    let endIdx = html.indexOf(');', idx);
    let original = html.substring(idx, endIdx + 2);
    console.log("Found:\n" + original);
    
    let fixed = 'alert(`❌ Server Offline hoặc không thể kết nối: ${e.message}\\n\\nHãy chắc chắn server đã được bật và đúng địa chỉ.`);';
    html = html.replace(original, fixed);
    
    fs.writeFileSync('index.html', html, 'utf8');
    console.log("Fixed.");
} else {
    console.log("Not found.");
}
