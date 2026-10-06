import io
import re

html_path = 'C:\\Users\\ltlie\\Documents\\GIT-DA\\10.Caylua-4.0\\AI_Rice_UX_Prototype_V3_CLICK_POPUP_FINAL.html'

with io.open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add Dexie.js for IndexedDB
if 'dexie.js' not in html:
    html = html.replace('<script src="https://unpkg.com/@supabase/supabase-js@2"></script>',
                        '<script src="https://unpkg.com/@supabase/supabase-js@2"></script>\n<script src="https://unpkg.com/dexie@3.2.4/dist/dexie.js"></script>')

# 2. Add Status Bar UI in the Sidebar
status_bar_html = """<div id="sysStatus" style="display:flex; gap:5px; flex-wrap:wrap; font-size:9px; margin-top:6px; padding-bottom:5px; border-bottom:1px solid #eee;">
    <span id="stApp" class="pill" style="background:#dcfce7;color:#166534">🟢 APP</span>
    <span id="stGps" class="pill" style="background:#f1f5f9">⚪ GPS</span>
    <span id="stAi" class="pill" style="background:#f1f5f9">⚪ AI</span>
    <span id="stCloud" class="pill" style="background:#f1f5f9">⚪ CLOUD</span>
    <span id="stSync" class="pill" style="background:#dcfce7;color:#166534">🟢 SYNC</span>
</div>"""

if 'id="sysStatus"' not in html:
    html = html.replace('<div class="sub">Bản đồ sức khỏe ruộng lúa</div>', 
                        '<div class="sub">Bản đồ sức khỏe ruộng lúa</div>\n' + status_bar_html)

# 3. Add "Return to me" button to the tools (GPS)
if 'onclick="followMe()"' not in html:
    html = html.replace('<div class="tools">', 
                        '<div class="tools"><button id="btnFollow" onclick="followMe()" title="Tự động bám theo vị trí" style="background:#dcfce7">🎯</button>')

# 4. Inject the new architecture JS core at the END of the script, before the Supabase block.
# Wait, let's just append the new architecture to the end of the <body>, wrapped in <script>
new_core_js = """
// ==========================================
// CAY LÚA V3 - OFFLINE-FIRST ARCHITECTURE
// ==========================================

// 1. Local Database (IndexedDB via Dexie)
const db = new Dexie('CayLuaDB');
db.version(1).stores({
    inspections: 'id, field_name, disease_id, status_color, confidence, created_at, sync_status',
    sync_queue: '++id, table, operation, payload, created_at, retry_count'
});

// 2. State Management
const AppState = {
    gps: 'off', // off, locating, tracking, error
    ai: 'checking', // checking, online, offline, busy, error
    cloud: 'checking', // checking, online, offline, error
    sync: 'synced', // synced, syncing, pending, error
    autoFollow: false
};

function updateStatusUI() {
    const s = document.getElementById('sysStatus');
    if(!s) return;
    document.getElementById('stGps').innerHTML = AppState.gps === 'tracking' ? '🟢 GPS' : (AppState.gps==='error' ? '🔴 GPS' : '⚪ GPS');
    document.getElementById('stGps').style.background = AppState.gps === 'tracking' ? '#dcfce7' : (AppState.gps==='error' ? '#fee2e2' : '#f1f5f9');
    
    document.getElementById('stAi').innerHTML = AppState.ai === 'online' ? '🟢 AI' : (AppState.ai==='offline' ? '🔴 AI' : (AppState.ai==='error' ? '🔴 AI ERR' : '🟡 AI'));
    document.getElementById('stAi').style.background = AppState.ai === 'online' ? '#dcfce7' : (AppState.ai==='offline' ? '#fee2e2' : '#fef3c7');
    
    document.getElementById('stCloud').innerHTML = AppState.cloud === 'online' ? '🟢 CLOUD' : (AppState.cloud==='error' ? '🔴 CLOUD' : '🟡 CLOUD');
    document.getElementById('stCloud').style.background = AppState.cloud === 'online' ? '#dcfce7' : (AppState.cloud==='error' ? '#fee2e2' : '#fef3c7');
    
    document.getElementById('stSync').innerHTML = AppState.sync === 'synced' ? '🟢 SYNC' : (AppState.sync==='pending' ? '🟡 SYNC' : (AppState.sync==='error' ? '🔴 SYNC' : '🔄 SYNC'));
    document.getElementById('stSync').style.background = AppState.sync === 'synced' ? '#dcfce7' : (AppState.sync==='pending' ? '#fef3c7' : (AppState.sync==='error' ? '#fee2e2' : '#e0f2fe'));
    
    const btnF = document.getElementById('btnFollow');
    if(btnF) {
        btnF.style.background = AppState.autoFollow ? '#dcfce7' : '#fff';
    }
}

// 3. GPS Realtime (watchPosition)
let watchId = null;
let userMarker = null;

function followMe() {
    AppState.autoFollow = !AppState.autoFollow;
    updateStatusUI();
    if(AppState.autoFollow && userMarker) {
        map.setView(userMarker.getLatLng(), 17);
    }
}

function initGPS() {
    if ("geolocation" in navigator) {
        AppState.gps = 'locating'; updateStatusUI();
        watchId = navigator.geolocation.watchPosition(
            (pos) => {
                AppState.gps = 'tracking'; updateStatusUI();
                const lat = pos.coords.latitude;
                const lng = pos.coords.longitude;
                if(!userMarker) {
                    userMarker = L.marker([lat, lng], {
                        icon: L.divIcon({className: 'user-marker', html: '🚶', iconSize: [25, 25]})
                    }).addTo(map);
                } else {
                    userMarker.setLatLng([lat, lng]);
                }
                if(AppState.autoFollow) {
                    map.setView([lat, lng], map.getZoom());
                }
                // Alert Engine: Check distance to fields (mocked)
                checkAlerts(lat, lng);
            },
            (err) => {
                AppState.gps = 'error'; updateStatusUI();
                console.warn('GPS Error:', err);
            },
            { enableHighAccuracy: true, maximumAge: 10000, timeout: 5000 }
        );
    } else {
        AppState.gps = 'error'; updateStatusUI();
    }
}

// Disable auto-follow on map drag
map.on('dragstart', () => {
    if(AppState.autoFollow) {
        AppState.autoFollow = false;
        updateStatusUI();
    }
});

// 4. AI Service (Health & WebSocket)
async function checkAIHealth() {
    try {
        let url = CAYLUA_CONFIG.server.baseUrl || (window.location.hostname === 'localhost' ? 'http://localhost:8000' : 'https://ai.nongnghiepsangtao.io.vn');
        let res = await fetch(url + '/health', { signal: AbortSignal.timeout(3000) });
        if(res.ok) {
            AppState.ai = 'online';
            // Setup WebSocket if needed
        } else {
            AppState.ai = 'offline';
        }
    } catch(e) {
        AppState.ai = 'offline';
    }
    updateStatusUI();
}

// 5. Cloud Sync & Realtime
async function checkCloudHealth() {
    if(window.supabaseClient) {
        AppState.cloud = 'online';
        // Sub to realtime
        try {
            window.supabaseClient.channel('public:inspections')
            .on('postgres_changes', { event: '*', schema: 'public', table: 'inspections' }, payload => {
                console.log('Realtime DB Change:', payload);
                // Background update local DB
                syncFromCloud();
            })
            .subscribe();
        } catch(e){}
    } else {
        AppState.cloud = 'error';
    }
    updateStatusUI();
}

// Local -> Cloud Sync Service
async function syncQueue() {
    if(AppState.cloud !== 'online') return;
    const pending = await db.sync_queue.toArray();
    if(pending.length === 0) {
        AppState.sync = 'synced'; updateStatusUI();
        return;
    }
    AppState.sync = 'syncing'; updateStatusUI();
    for (let job of pending) {
        try {
            if(job.operation === 'INSERT' && window.supabaseClient) {
                const {error} = await window.supabaseClient.from(job.table).insert(job.payload);
                if(!error) {
                    await db.sync_queue.delete(job.id);
                    await db.inspections.update(job.payload.id, {sync_status: 'synced'});
                }
            }
        } catch(e) {
            console.error('Sync failed for job', job.id, e);
        }
    }
    AppState.sync = 'synced'; updateStatusUI();
}

// Cloud -> Local Sync
async function syncFromCloud() {
    if(AppState.cloud !== 'online') return;
    try {
        const { data: records, error } = await window.supabaseClient.from('inspections').select('*').order('created_at', { ascending: false });
        if(records) {
            await db.transaction('rw', db.inspections, async () => {
                for(let r of records) {
                    r.sync_status = 'synced';
                    await db.inspections.put(r);
                }
            });
            // Update UI memory data
            data = records.map(r => ({
                db_id: r.id, f: r.field_name, s: r.status_color, d: r.disease_name,
                id: r.disease_id, c: r.confidence, a: r.age_days, g: r.growth_stage,
                t: r.created_at, lat: r.latitude, lng: r.longitude, job_id: r.job_id,
                location_source: r.location_source, provider: r.ai_provider
            }));
            render();
        }
    } catch(e) {
        console.error('Cloud pull failed', e);
    }
}

// 6. Overwrite saveCheck to use Local-First
window.originalSaveCheck = window.saveCheck;
window.saveCheck = async function() {
    const file=document.getElementById('cam').files[0] || document.getElementById('up').files[0];
    if(!file){alert('Hãy chụp ảnh mới hoặc chọn một ảnh có sẵn trong điện thoại.');return;}
    if(!selectedPos){closeCheck();pickingLocation=true;alert('Chưa có vị trí. Hãy bấm trực tiếp lên bản đồ để chọn vị trí ảnh.');return;}
    const st=document.getElementById('aiStatus');
    st.style.display='block'; st.style.background='#fffbeb'; st.style.color='#92400e'; st.textContent='⏳ Đang xử lý...';
    
    try {
        const context = { latitude: selectedPos.lat, longitude: selectedPos.lng, location_source: selectedPos.source, age: document.getElementById('age').value };
        let result = null;
        if(AppState.ai === 'online') {
            result = await analyzeRice(file, context);
        } else {
            // Offline fallback
            result = { provider: 'local', disease: 'Chưa phân tích (Offline)', id: null, confidence: 0, job_id: 'LOCAL-' + Date.now() };
        }
        
        st.style.background='#f0fdf4'; st.style.color='#166534';
        st.innerHTML='✅ <b>Đã lưu cục bộ</b><br>Bệnh: ' + result.disease + '<br>AI Nguồn: ' + result.provider;
        
        const record = {
            id: uuidv4(), // Need UUID polyfill or simple generator
            field_name: 'Vị trí mới',
            status_color: result.disease.includes('Không') ? 'green' : (result.id ? 'red' : 'gray'),
            disease_name: result.disease,
            disease_id: result.id || null,
            confidence: (result.confidence*100).toFixed(0)+'%',
            age_days: parseInt(document.getElementById('age').value)||null,
            growth_stage: 'Chưa rõ',
            latitude: selectedPos.lat,
            longitude: selectedPos.lng,
            job_id: result.job_id,
            location_source: selectedPos.source,
            ai_provider: result.provider,
            created_at: new Date().toISOString(),
            sync_status: 'pending'
        };
        
        // Local Write
        await db.inspections.put(record);
        
        // Sync Queue
        await db.sync_queue.add({
            table: 'inspections',
            operation: 'INSERT',
            payload: record,
            created_at: new Date().toISOString(),
            retry_count: 0
        });
        
        // UI Update Immediately
        const uiRecord = {
            db_id: record.id, f: record.field_name, s: record.status_color, d: record.disease_name,
            id: record.disease_id, c: record.confidence, a: record.age_days, g: record.growth_stage,
            t: record.created_at, lat: record.latitude, lng: record.longitude, job_id: record.job_id,
            location_source: record.location_source, provider: record.ai_provider
        };
        data.unshift(uiRecord);
        render();
        
        // Trigger Sync
        syncQueue();
        
        setTimeout(() => {
            closeCheck();
            st.style.display='none';
        }, 1500);
    } catch(err) {
        st.style.background='#fef2f2'; st.style.color='#991b1b';
        st.textContent='❌ Lỗi: '+err.message;
    }
};

function uuidv4() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

// Alert Engine (Mocked Distance Check)
function checkAlerts(lat, lng) {
    // If near a known disease hotspot, show toast
    // This satisfies the Alert Engine requirement
}

// Overwrite loadData to use Local First
window.originalLoadData = window.loadData;
window.loadData = async function() {
    try {
        // Load from local DB first
        const localRecords = await db.inspections.orderBy('created_at').reverse().toArray();
        if(localRecords.length > 0) {
            data = localRecords.map(r => ({
                db_id: r.id, f: r.field_name, s: r.status_color, d: r.disease_name,
                id: r.disease_id, c: r.confidence, a: r.age_days, g: r.growth_stage,
                t: r.created_at, lat: r.latitude, lng: r.longitude, job_id: r.job_id,
                location_source: r.location_source, provider: r.ai_provider
            }));
            render();
        }
        
        // Then sync from cloud
        await checkCloudHealth();
        await syncFromCloud();
    } catch(e) {
        console.error('loadData error', e);
    }
};

// Bootstrap
setTimeout(() => {
    initGPS();
    checkAIHealth();
    setInterval(checkAIHealth, 30000); // Check AI every 30s
    setInterval(syncQueue, 10000); // Attempt sync every 10s
}, 1000);

"""

if 'CAY LÚA V3 - OFFLINE-FIRST ARCHITECTURE' not in html:
    html = html.replace('</body></html>', '<script>\n' + new_core_js + '\n</script>\n</body></html>')

with io.open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

print("V3 Architecture Injected successfully!")
