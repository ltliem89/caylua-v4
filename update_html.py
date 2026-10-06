import re

with open("AI_Rice_UX_Prototype_V3_CLICK_POPUP_FINAL.html", "r", encoding="utf-8") as f:
    html = f.read()

# Chèn file script vào HTML
if 'src="./v3_services.js"' not in html:
    html = html.replace('<script src="https://unpkg.com/dexie@3.2.4/dist/dexie.js"></script>',
                        '<script src="https://unpkg.com/dexie@3.2.4/dist/dexie.js"></script>\n<script src="./v3_services.js"></script>')

new_savecheck = """
window.saveCheck = async function() {
    const file = document.getElementById('cam').files[0] || document.getElementById('up').files[0];
    if(!file) { alert('Hãy chụp ảnh mới hoặc chọn một ảnh có sẵn trong điện thoại.'); return; }
    if(!selectedPos) { closeCheck(); pickingLocation = true; alert('Chưa có vị trí. Hãy bấm trực tiếp lên bản đồ để chọn vị trí ảnh.'); return; }
    
    const st = document.getElementById('aiStatus');
    st.style.display = 'block'; st.style.background = '#fffbeb'; st.style.color = '#92400e'; 
    st.textContent = '⏳ Đang tạo điểm khảo sát...';
    
    try {
        // Mock ID cho UI nếu chưa auth
        let user = null;
        try {
            if(SupabaseService.client) {
                user = (await SupabaseService.client.auth.getUser()).data.user;
            }
        } catch(e) {}
        
        let session_id = '00000000-0000-0000-0000-000000000000';
        let point_id = '00000000-0000-0000-0000-000000000000';
        let image_id = '00000000-0000-0000-0000-000000000000';
        let user_id = user ? user.id : '00000000-0000-0000-0000-000000000000';
        let field_id = '00000000-0000-0000-0000-000000000000'; // mock field
        
        if (navigator.onLine && user) {
            // Online Flow
            st.textContent = '⏳ Đang tạo Session & Point...';
            const session = await SupabaseService.createSurveySession(field_id);
            session_id = session.id;
            
            const point = await SupabaseService.createSurveyPoint(session_id, field_id, selectedPos.lat, selectedPos.lng, 10.0);
            point_id = point.id;
            
            st.textContent = '⏳ Đang upload ảnh lên Supabase Storage...';
            const path = `${user_id}/${session_id}/${point_id}/original.${file.name.split('.').pop()}`;
            const imgRecord = await SupabaseService.createSurveyImage(session_id, point_id, file, path);
            image_id = imgRecord.id;
            
            const uploadedPath = await StorageService.uploadOriginal(file, user_id, session_id, point_id);
            await SupabaseService.updateImageStatus(image_id, 'uploaded');
            
            st.textContent = '⏳ Đang gửi AI Server phân tích...';
            const signedUrl = await StorageService.getSignedUrl(uploadedPath);
            await SupabaseService.updateImageStatus(image_id, 'ai_pending');
            
            let aiResult = null;
            try {
                aiResult = await AIService.submitImage(point_id, image_id, signedUrl);
                st.style.background = '#f0fdf4'; st.style.color = '#166534';
                st.innerHTML = '✅ <b>AI Hoàn tất</b><br>Bệnh: ' + (aiResult.diseases.length > 0 ? aiResult.diseases[0].name : "Không phát hiện");
            } catch(e) {
                st.style.background = '#fef3c7'; st.style.color = '#92400e';
                st.innerHTML = '⚠️ <b>Lỗi AI, kết quả sẽ cập nhật sau</b>';
                await SupabaseService.updateImageStatus(image_id, 'ai_failed');
            }
            
            // Add marker
            const record = {
                f: 'Vị trí khảo sát mới', 
                s: aiResult && aiResult.diseases.length > 0 ? (aiResult.diseases[0].name.includes('Không') ? 'green' : 'red') : 'gray', 
                d: aiResult && aiResult.diseases.length > 0 ? aiResult.diseases[0].name : 'Đang xử lý', 
                id: aiResult && aiResult.diseases.length > 0 ? aiResult.diseases[0].id : null, 
                c: aiResult && aiResult.diseases.length > 0 ? (aiResult.diseases[0].confidence*100).toFixed(0)+'%' : '—', 
                a: document.getElementById('age').value || '—', 
                g: 'Chưa rõ', 
                t: new Date().toISOString(), 
                lat: selectedPos.lat, 
                lng: selectedPos.lng, 
                job_id: aiResult ? aiResult.job_id : null, 
                location_source: selectedPos.source, 
                provider: 'caylua-yolov8'
            };
            data.unshift(record);
            render();
            
        } else {
            // Offline Flow
            st.textContent = '⏳ Mất mạng - Đang lưu vào Queue...';
            const reader = new FileReader();
            reader.readAsArrayBuffer(file);
            reader.onload = async function() {
                const arrayBuffer = reader.result;
                const payload = {
                    file_name: file.name,
                    mime_type: file.type,
                    user_id: user_id,
                    session_id: session_id,
                    point_id: point_id
                };
                await SyncService.addQueue('survey_image', image_id, 'upload', payload, arrayBuffer);
                
                st.style.background = '#f0fdf4'; st.style.color = '#166534';
                st.innerHTML = '✅ <b>Đã lưu khảo sát trên điện thoại.<br>Sẽ đồng bộ khi có mạng.</b>';
                
                const record = {
                    f: 'Khảo sát Offline', 
                    s: 'gray', 
                    d: 'Chờ đồng bộ', 
                    id: null, 
                    c: '—', 
                    a: document.getElementById('age').value || '—', 
                    g: 'Chưa rõ', 
                    t: new Date().toISOString(), 
                    lat: selectedPos.lat, 
                    lng: selectedPos.lng, 
                    job_id: null, 
                    location_source: selectedPos.source, 
                    provider: 'offline'
                };
                data.unshift(record);
                render();
            };
        }
        
        setTimeout(() => {
            closeCheck();
            st.style.display='none';
        }, 2000);
        
    } catch(err) {
        st.style.background = '#fef2f2'; st.style.color = '#991b1b';
        st.textContent = '❌ Lỗi: ' + err.message;
        console.error(err);
    }
}
"""

# Replace the saveCheck function
html = re.sub(r'async function saveCheck\(\)\s*\{.*?function closeCheck\(\)', new_savecheck + '\nfunction closeCheck()', html, flags=re.DOTALL)
html = re.sub(r'window\.saveCheck = async function\(\)\s*\{.*?function uuidv4', new_savecheck + '\nfunction uuidv4', html, flags=re.DOTALL)


with open("AI_Rice_UX_Prototype_V3_CLICK_POPUP_FINAL.html", "w", encoding="utf-8") as f:
    f.write(html)
