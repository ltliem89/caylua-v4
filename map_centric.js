// map_centric.js
// Overrides UI functions to make Map the central interaction point, integrating Supabase, GPS watch, and Offline sync.

window.GPS_Follow = true;
window.userGPSPos = null;
window.gpsMarker = null;
window.survey_session_id = localStorage.getItem('survey_session_id') || null;

// 1. Khởi tạo
async function initMapCentricApp() {
    console.log("Khởi tạo Map Centric App...");
    
    // Đảm bảo Supabase Init
    if (typeof SupabaseService.init === 'function') SupabaseService.init();

    // Auth Check
    let user = null;
    try {
        if(SupabaseService.client) {
            const authData = await SupabaseService.client.auth.getUser();
            if(authData.data && authData.data.user) {
                user = authData.data.user;
            }
        }
    } catch(e) {}
    
    if (user) {
        document.getElementById('stCloud').style.background = '#dcfce7';
        document.getElementById('stCloud').style.color = '#166534';
        document.getElementById('stCloud').innerText = '🟢 CLOUD';
        
        // Tải dữ liệu ban đầu
        await fetchSupabasePoints();
        
        // Đăng ký Realtime
        if (typeof RealtimeService.subscribeAI === 'function') {
            RealtimeService.subscribeAI((payload) => {
                console.log("Realtime AI payload:", payload);
                fetchSupabasePoints();
            });
        }
    } else {
        document.getElementById('stCloud').style.background = '#fef3c7';
        document.getElementById('stCloud').style.color = '#92400e';
        document.getElementById('stCloud').innerText = '🟡 GUEST (LOCAL)';
    }

    // Bật GPS Watch
    if (typeof GPSService.start === 'function') {
        GPSService.start((pos) => {
            window.userGPSPos = [pos.coords.latitude, pos.coords.longitude];
            
            document.getElementById('stGps').style.background = '#dcfce7';
            document.getElementById('stGps').style.color = '#166534';
            document.getElementById('stGps').innerText = `🟢 GPS (±${Math.round(pos.coords.accuracy)}m)`;
            
            if(!window.gpsMarker) {
                window.gpsMarker = L.circleMarker(window.userGPSPos, {
                    radius: 7, color: '#fff', weight: 2, fillColor: '#2563eb', fillOpacity: 1
                }).addTo(map).bindPopup('Vị trí của bạn');
            } else {
                window.gpsMarker.setLatLng(window.userGPSPos);
            }
            
            if (window.GPS_Follow) {
                map.setView(window.userGPSPos, map.getZoom());
            }
        });
    }

    // Map drag event to disable auto-follow
    map.on('dragstart', () => {
        window.GPS_Follow = false;
        document.getElementById('btnFollow').style.background = '#fff';
    });
    
    // Gắn session UI
    if (!window.survey_session_id) {
        document.getElementById('pt').innerHTML = '📍 Vị trí <button onclick="startSession()" style="float:right;background:#16a34a;color:#fff;border:none;padding:4px 8px;border-radius:4px">▶ Bắt đầu khảo sát</button>';
    } else {
        document.getElementById('pt').innerHTML = '📍 Đang khảo sát <button onclick="endSession()" style="float:right;background:#dc2626;color:#fff;border:none;padding:4px 8px;border-radius:4px">⏹ Kết thúc</button>';
    }
}

window.startSession = async function() {
    try {
        let field_id = '00000000-0000-0000-0000-000000000000'; // mock field
        const session = await SupabaseService.createSurveySession(field_id);
        window.survey_session_id = session.id;
        localStorage.setItem('survey_session_id', session.id);
        document.getElementById('pt').innerHTML = '📍 Đang khảo sát <button onclick="endSession()" style="float:right;background:#dc2626;color:#fff;border:none;padding:4px 8px;border-radius:4px">⏹ Kết thúc</button>';
        alert("Đã tạo Survey Session mới!");
    } catch(e) {
        alert("Lỗi tạo session: " + e.message);
    }
}

window.endSession = function() {
    window.survey_session_id = null;
    localStorage.removeItem('survey_session_id');
    document.getElementById('pt').innerHTML = '📍 Vị trí <button onclick="startSession()" style="float:right;background:#16a34a;color:#fff;border:none;padding:4px 8px;border-radius:4px">▶ Bắt đầu khảo sát</button>';
    alert("Đã kết thúc khảo sát.");
}

// Lấy dữ liệu điểm khảo sát từ Supabase
async function fetchSupabasePoints() {
    try {
        const { data: points, error } = await SupabaseService.client
            .from('survey_points')
            .select('*, survey_images(*), ai_results(*)');
            
        if(error) throw error;
        
        let newData = [];
        points.forEach(p => {
            let s = 'gray'; // pending
            let diseaseText = 'Đang chờ xử lý';
            let conf = '—';
            let id = null;
            let imgUrl = null;
            
            // Xử lý AI result mới nhất
            if(p.ai_results && p.ai_results.length > 0) {
                // Sắp xếp theo created_at
                p.ai_results.sort((a,b) => new Date(a.created_at) - new Date(b.created_at));
                let ai = p.ai_results[p.ai_results.length - 1]; 
                
                // Trạng thái AI
                if (ai.status === 'completed' || ai.disease) {
                    if(ai.disease && (ai.disease.toLowerCase().includes('khỏe') || ai.disease.toLowerCase().includes('không'))) {
                        s = 'green';
                        id = null;
                    } else if(ai.disease) {
                        s = 'red';
                        id = 'fungal_dao_on'; // default fallback for UI testing
                    } else {
                        s = 'yellow';
                    }
                    diseaseText = ai.disease;
                    conf = ai.confidence ? Math.round(ai.confidence * 100) + '%' : '—';
                    if (ai.class_id) {
                        // find matching ID in DISEASES logic or mapping if needed
                    }
                } else if(ai.status === 'failed') {
                    s = 'yellow';
                    diseaseText = 'Lỗi AI';
                }
            } else if (p.survey_images && p.survey_images.length > 0) {
                let img = p.survey_images[p.survey_images.length - 1];
                if (img.status === 'ai_failed') {
                    s = 'yellow';
                    diseaseText = 'Lỗi AI (Ảnh)';
                } else if (img.status === 'ai_pending') {
                    s = 'yellow';
                    diseaseText = 'Đang phân tích AI...';
                } else if (img.status === 'uploading') {
                    s = 'gray';
                    diseaseText = 'Đang upload ảnh...';
                }
            } else {
                s = 'gray';
                diseaseText = 'Chưa có ảnh/AI';
            }
            
            newData.push({
                db_id: p.id,
                f: 'Điểm',
                s: s,
                d: diseaseText,
                id: id, // for detail popup
                c: conf,
                a: 50,
                g: 'Sinh trưởng',
                t: p.captured_at,
                lat: p.latitude,
                lng: p.longitude,
                provider: 'Supabase'
            });
        });
        
        window.data = newData;
        if(typeof window.render === 'function') window.render();
        
    } catch(e) {
        console.error("fetchSupabasePoints error", e);
    }
}

// Ghi đè hàm follow / locate
window.followMe = function() {
    window.GPS_Follow = true;
    document.getElementById('btnFollow').style.background = '#dcfce7';
    if(window.userGPSPos) {
        map.setView(window.userGPSPos, 17);
    } else {
        alert('Đang tìm GPS, vui lòng đợi...');
    }
};

window.locate = function() {
    window.followMe();
};

// Ghi đè saveCheck để thực thi quy trình khảo sát Offline-first
window.saveCheck = async function() {
    const file = document.getElementById('cam').files[0] || document.getElementById('up').files[0];
    if(!file) { alert('Hãy chụp ảnh mới hoặc chọn một ảnh có sẵn.'); return; }
    
    let lat, lng, acc;
    if (window.userGPSPos) {
        lat = window.userGPSPos[0];
        lng = window.userGPSPos[1];
        acc = 10.0;
    } else if (window.selectedPos) {
        lat = window.selectedPos.lat;
        lng = window.selectedPos.lng;
        acc = 0;
    } else {
        closeCheck(); window.pickingLocation = true; alert('Chưa có vị trí. Hãy bật GPS hoặc chọn trên bản đồ.'); return; 
    }
    
    const st = document.getElementById('aiStatus');
    st.style.display = 'block'; st.style.background = '#fffbeb'; st.style.color = '#92400e'; 
    st.textContent = '⏳ Đang lưu khảo sát...';
    
    try {
        let user = null;
        try { if(SupabaseService.client) user = (await SupabaseService.client.auth.getUser()).data.user; } catch(e) {}
        
        // Auto create session if not exists
        if (!window.survey_session_id && user) {
            await window.startSession();
        }
        
        let session_id = window.survey_session_id || '00000000-0000-0000-0000-000000000000';
        let point_id = window.uuidv4();
        let image_id = window.uuidv4();
        let user_id = user ? user.id : '00000000-0000-0000-0000-000000000000';
        let field_id = '00000000-0000-0000-0000-000000000000'; // mock
        
        // Thêm marker lên UI tạm
        let tempRecord = {
            db_id: point_id,
            f: 'Offline',
            s: 'gray',
            d: 'Đang xử lý / Chưa đồng bộ',
            id: null,
            c: '—',
            a: 50,
            g: 'Sinh trưởng',
            t: new Date().toISOString(),
            lat: lat,
            lng: lng,
            provider: 'Local'
        };
        window.data.unshift(tempRecord); // Thêm lên đầu
        if(typeof window.render === 'function') window.render();
        closeCheck();
        
        // Đọc blob arraybuffer
        const arrayBuffer = await file.arrayBuffer();
        
        // Queue lên IndexedDB
        st.textContent = '⏳ Đang lưu offline queue...';
        await SyncService.addQueue('survey_image', image_id, 'upload', {
            user_id, session_id, point_id, lat, lng,
            file_name: file.name,
            mime_type: file.type,
            size: file.size
        }, arrayBuffer);
        
        console.log("Saved to offline queue.");
        
        document.getElementById('stSync').innerText = '🟡 SYNCING...';
        
    } catch (e) {
        alert("Lỗi khi tạo khảo sát: " + e.message);
    }
}

// Bổ sung hàm uuidv4 nếu chưa có
if(typeof window.uuidv4 !== 'function') {
    window.uuidv4 = function() {
        return ([1e7]+-1e3+-4e3+-8e3+-1e11).replace(/[018]/g, c =>
            (c ^ crypto.getRandomValues(new Uint8Array(1))[0] & 15 >> c / 4).toString(16)
        );
    }
}

// Ghi đè hàm render để xử lý filter/màu sắc tốt hơn
const originalRender = window.render;
window.render = function() {
    // Gọi hàm gốc để tạo map marker và HTML list
    if (originalRender) originalRender();
    
    // Đảm bảo Marker GPS luôn nổi lên trên
    if (window.gpsMarker) {
        window.gpsMarker.bringToFront();
    }
}

// Sửa lại quá trình load IndexedDB Queue
const originalProcessQueue = SyncService.processQueue;
SyncService.processQueue = async function() {
    document.getElementById('stSync').innerText = '🟡 SYNCING...';
    try {
        await originalProcessQueue.call(SyncService);
        document.getElementById('stSync').innerText = '🟢 SYNCED';
        fetchSupabasePoints();
    } catch (e) {
        document.getElementById('stSync').innerText = '🔴 SYNC ERR';
    }
}

// Bắt đầu
document.addEventListener("DOMContentLoaded", () => {
    // Đợi 1 giây để các object có sẵn load xong
    setTimeout(initMapCentricApp, 1000);
});

// Ghi đè hàm tab để làm cho Dashboard & Thống kê động
const originalTab = window.tab;
window.tab = function(b, t) {
    // Gọi hàm cũ để chuyển trạng thái UI (đổi active class)
    document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active')); 
    if(b) b.classList.add('active');
    
    const list = document.getElementById('list');
    
    if (t === 'recent') {
        if(typeof window.render === 'function') window.render(); // Gọi lại render list
    }
    else if (t === 'overview') {
        const total = window.data.length;
        const diseaseCount = window.data.filter(x => x.s === 'red').length;
        const healthyCount = window.data.filter(x => x.s === 'green').length;
        const pendingCount = window.data.filter(x => x.s === 'gray' || x.s === 'yellow').length;
        
        list.innerHTML = `
            <h3 style="font-size:13px; cursor:pointer" onclick="filterMap('all')">📊 Phân tích khảo sát</h3>
            <div class="dataStat">
                <div class="info" style="cursor:pointer" onclick="filterMap('all')">
                    <b>${total}</b><span>Tổng số điểm</span>
                </div>
                <div class="info" style="cursor:pointer; background:#fee2e2" onclick="filterMap('red')">
                    <b style="color:#991b1b">${diseaseCount}</b><span style="color:#991b1b">Có bệnh</span>
                </div>
                <div class="info" style="cursor:pointer; background:#dcfce7" onclick="filterMap('green')">
                    <b style="color:#166534">${healthyCount}</b><span style="color:#166534">Không bệnh</span>
                </div>
                <div class="info" style="cursor:pointer; background:#fef3c7" onclick="filterMap('yellow')">
                    <b style="color:#92400e">${pendingCount}</b><span style="color:#92400e">Chờ/Lỗi/Theo dõi</span>
                </div>
            </div>
            <div class="rec">
                <b>💡 Gợi ý:</b> Bấm vào các thẻ thống kê phía trên để lọc các điểm tương ứng trên bản đồ.
            </div>
        `;
    }
    else if (t === 'tasks') {
        // dynamic tasks based on red markers
        const redPoints = window.data.filter(x => x.s === 'red');
        let taskHtml = `
            <div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:10px;padding:10px;margin-bottom:8px">
                <div style="display:flex;justify-content:space-between;align-items:center">
                    <b style="font-size:11px;color:#1e40af">🌦️ CẢNH BÁO TỪ HỆ THỐNG</b>
                </div>
                <div style="margin-top:8px;padding:6px;border-radius:6px;background:#fee2e2;color:#991b1b;font-size:10px;line-height:1.4">
                    ⚠️ Có <b>${redPoints.length}</b> điểm nghi nhiễm bệnh. Đề nghị kiểm tra và xử lý gấp.
                </div>
            </div>
            <h4 style="margin:6px 0;font-size:11px">Các điểm khẩn cấp:</h4>
        `;
        redPoints.forEach(x => {
            taskHtml += `
                <div class="item" onclick="detail(${JSON.stringify(x).replace(/"/g, '&quot;')})">
                    <div style="font-size:25px">🔴</div>
                    <div>
                        <div class="title">${x.f} — ${x.d}</div>
                        <div class="meta">Cần xử lý kịp thời.</div>
                    </div>
                </div>
            `;
        });
        if (redPoints.length === 0) taskHtml += '<div style="font-size:11px;color:#667085;padding:10px">Không có điểm nào khẩn cấp.</div>';
        list.innerHTML = taskHtml;
    }
    else if (t === 'knowledge') {
        if(typeof renderKnowledge === 'function') renderKnowledge('');
    }
    else if (t === 'data') {
        if(originalTab) {
            // we have to re-evaluate the original code for data or just mock it here
            list.innerHTML = '<div style="padding:10px;font-size:11px">Module dữ liệu đang phát triển...</div>';
        }
    }
};

window.filterMap = function(status) {
    if(status === 'all') {
        window.filteredData = null;
    } else {
        window.filteredData = window.data.filter(x => x.s === status || (status==='yellow' && x.s==='gray'));
    }
    if(typeof window.render === 'function') window.render();
};

const originalRenderListMap = window.render;
window.render = function() {
    // override render function slightly to use filteredData if available
    window.ms.forEach(x => map.removeLayer(x)); 
    window.ms = [];
    
    const displayData = window.filteredData || window.data;
    
    displayData.forEach(x => {
        let col = x.s === 'red' ? '#dc2626' : x.s === 'yellow' ? '#eab308' : x.s === 'green' ? '#16a34a' : '#64748b';
        let m = L.circleMarker([x.lat, x.lng], {radius:10, color:'#fff', weight:2, fillColor:col, fillOpacity:0.95})
            .addTo(map).on('click', () => detail(x)); 
        window.ms.push(m);
    });
    
    let q = document.getElementById('q').value.toLowerCase();
    let arr = displayData.filter(x => (x.f+x.d+x.g).toLowerCase().includes(q)).sort((a,b) => new Date(b.t) - new Date(a.t));
    let el = document.getElementById('list'); 
    
    // Only update list if we are in 'recent' tab
    const activeTab = document.querySelector('.tab.active');
    if (activeTab && activeTab.textContent.includes('Nhật ký')) {
        el.innerHTML = '';
        arr.forEach(x => {
            let e = document.createElement('div'); e.className = 'item';
            e.innerHTML = '<div class="thumb">🌾</div><div><div class="title">'+label(x.s)+' · '+x.f+'</div><div class="meta">'+x.d+'<br>'+x.a+' ngy · '+x.g+' · '+new Date(x.t).toLocaleTimeString('vi-VN',{hour:'2-digit',minute:'2-digit'})+'</div></div><span class="badge '+x.s+'">'+x.c+'</span>';
            e.onclick = (ev) => {
                detail(x);
            };
            el.appendChild(e);
        });
    }

    if (window.gpsMarker) window.gpsMarker.bringToFront();
};

// Helper label
function label(s) {
    if(s==='red') return 'CẢNH BÁO';
    if(s==='yellow') return 'CHỜ/LỖI';
    if(s==='green') return 'BÌNH THƯỜNG';
    return 'CHƯA ĐỒNG BỘ';
}

// Draw Route Polyline
window.routePolyline = null;
const originalRenderWithRoute = window.render;
window.render = function() {
    originalRenderWithRoute();
    
    // Draw route if there are points
    if (window.routePolyline) {
        map.removeLayer(window.routePolyline);
        window.routePolyline = null;
    }
    
    const displayData = window.filteredData || window.data;
    if (displayData && displayData.length > 1) {
        // Sort by time ascending to draw route
        const routePoints = [...displayData].sort((a,b) => new Date(a.t) - new Date(b.t));
        const latlngs = routePoints.map(p => [p.lat, p.lng]);
        window.routePolyline = L.polyline(latlngs, {color: '#3b82f6', weight: 3, dashArray: '5, 5'}).addTo(map);
    }
}

// HEALTH CHECK SCRIPT
async function checkSystemHealth() {
    // Check AI
    try {
        const aiRes = await fetch('http://localhost:8000/api/ai/predict', { method: 'POST' }).catch(()=>null);
        const stAi = document.getElementById('stAi');
        if (stAi) {
            // Because it's a POST without body, it might return 422, but that means it's online
            if (aiRes && (aiRes.status === 200 || aiRes.status === 422 || aiRes.status === 405)) {
                stAi.style.background = '#dcfce7'; stAi.style.color = '#166534';
                stAi.innerText = '🟢 YOLO AI';
            } else {
                stAi.style.background = '#fef3c7'; stAi.style.color = '#92400e';
                stAi.innerText = '🟡 GEMINI FALLBACK';
            }
        }
    } catch(e) {}
}

setInterval(checkSystemHealth, 30000);
setTimeout(checkSystemHealth, 2000);
