import re

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

new_logic = """
        if (navigator.onLine) {
            if (!user) {
                // Fallback: Direct AI for guest/prototype testing
                st.textContent = '⏳ Đang gửi trực tiếp ảnh cho AI Server (Chế độ Khách)...';
                const context = { latitude: selectedPos.lat, longitude: selectedPos.lng, location_source: selectedPos.source };
                
                let aiResult = null;
                try {
                    aiResult = await analyzeRice(file, context);
                    st.style.background = '#f0fdf4'; st.style.color = '#166534';
                    st.innerHTML = '✅ <b>AI Hoàn tất</b><br>Bệnh: ' + aiResult.disease;
                    
                    const record = {
                        f: 'Vị trí khảo sát mới (Guest)', 
                        s: aiResult.disease.includes('Không') ? 'green' : 'red', 
                        d: aiResult.disease, 
                        id: aiResult.id, 
                        c: (aiResult.confidence*100).toFixed(0)+'%', 
                        a: document.getElementById('age').value || '—', 
                        g: 'Chưa rõ', 
                        t: new Date().toISOString(), 
                        lat: selectedPos.lat, 
                        lng: selectedPos.lng, 
                        job_id: aiResult.job_id, 
                        location_source: selectedPos.source, 
                        provider: aiResult.provider
                    };
                    data.unshift(record);
                    render();
                } catch(e) {
                    st.style.background = '#fef3c7'; st.style.color = '#92400e';
                    st.innerHTML = '⚠️ <b>Lỗi kết nối AI:</b> ' + e.message;
                }
                
            } else {
                // Online Flow (Supabase Architecture)
                st.textContent = '⏳ Đang tạo Session & Point...';
"""

html = html.replace("""
        if (navigator.onLine && user) {
            // Online Flow
            st.textContent = '⏳ Đang tạo Session & Point...';""", new_logic)

# Replace the closing brace for the original if block
html = html.replace("""
            data.unshift(record);
            render();
            
        } else {""", """
            data.unshift(record);
            render();
            }
            
        } else {""")

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)
