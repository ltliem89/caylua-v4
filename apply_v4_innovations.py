import re

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

# 1. Add Sunlight High-Contrast CSS
sun_css = """
/* Chế độ Nắng Chói Ngoài Trời (High-Contrast Sunlight Mode) */
body.sun-mode {
  background: #000 !important;
  color: #fff !important;
}
body.sun-mode .app {
  background: #000 !important;
}
body.sun-mode .side, body.sun-mode .sheet, body.sun-mode .panel, body.sun-mode .setbox {
  background: #050505 !important;
  color: #ffffff !important;
  border: 3px solid #facc15 !important;
}
body.sun-mode .item, body.sun-mode .info, body.sun-mode .kcard {
  background: #18181b !important;
  color: #ffffff !important;
  border: 2px solid #a1a1aa !important;
}
body.sun-mode .title, body.sun-mode .big, body.sun-mode b {
  color: #fde047 !important;
  font-weight: 900 !important;
}
body.sun-mode .meta, body.sun-mode .sub, body.sun-mode small {
  color: #e4e4e7 !important;
}
body.sun-mode button {
  border: 2px solid #facc15 !important;
  font-weight: 800 !important;
}
body.sun-mode .primary, body.sun-mode .action, body.sun-mode .save {
  background: #facc15 !important;
  color: #000000 !important;
  border: 3px solid #ffffff !important;
}
body.sun-mode .tab.active {
  background: #facc15 !important;
  color: #000000 !important;
  font-weight: 900 !important;
}
body.sun-mode .rec {
  background: #064e3b !important;
  color: #a7f3d0 !important;
  border-left: 6px solid #34d399 !important;
}
body.sun-mode .warn {
  background: #78350f !important;
  color: #fef08a !important;
  border-left: 6px solid #fbbf24 !important;
}
"""

if "body.sun-mode" not in html:
    html = html.replace('</style>\n<style id="accessibility-font-style">', sun_css + '\n</style>\n<style id="accessibility-font-style">')

# 2. Add buttons in tools toolbar for Sunlight mode, Wind Radar, and Microclimate DRI
new_tools = """<button id="btnSunMode" onclick="toggleSunMode()" title="Chế độ Nắng Chói Ngoài Đồng">☀️ Nắng Chói</button><button id="btnWindRadar" onclick="toggleWindRadar()" title="Radar Gió & Dịch Tễ Lây Lan">💨 Gió & Dịch</button>"""

if 'id="btnSunMode"' not in html:
    html = html.replace('<div class="tools">', '<div class="tools">' + new_tools)

# 3. Enhance modal with Voice Input & Zero-Typing
old_modal_start = """<div class="field"><label>📅 Ngày gieo</label><input id="sow" type="date" value="2026-08-01"></div><div class="field"><label>🌱 Tuổi lúa</label><input id="age" readonly></div><div class="field"><label>🌿 Giai đoạn</label><select><option>Chưa chọn</option><option>Mạ</option><option>Đẻ nhánh</option><option>Làm đòng</option><option>Trổ</option><option>Chín sữa</option><option>Chín</option></select></div><div class="field"><label>📝 Ghi chú</label><input placeholder="Lá vàng, có đốm..."></div>"""

new_modal_start = """<div class="field"><label>📅 Ngày gieo</label><input id="sow" type="date" value="2026-08-01" onchange="updateCropStageFromDate()"></div><div class="grid" style="grid-template-columns:1fr 1fr;gap:6px"><div class="field"><label>🌱 Tuổi lúa (tự tính)</label><input id="age" readonly style="font-weight:700"></div><div class="field"><label>🌿 Giai đoạn (tự chọn)</label><select id="stageSelect"><option>Mạ</option><option>Đẻ nhánh</option><option>Làm đòng</option><option>Trổ</option><option>Chín sữa</option><option>Chín</option></select></div></div><div class="field"><label>📝 Ghi chú / Triệu chứng bệnh</label><div style="display:flex;gap:6px"><input id="noteInput" placeholder="Ví dụ: đốm mắt én ở lá, khô chóp..." style="flex:1"><button type="button" id="btnVoiceInput" onclick="startVoiceInput()" style="background:#2563eb;color:#fff;border:0;border-radius:8px;padding:0 12px;font-size:12px;font-weight:700" title="Bấm nói tiếng Việt">🎙️ Nói</button></div><div id="voiceStatus" style="display:none;margin-top:6px;padding:7px;border-radius:7px;background:#f0fdf4;font-size:10px;line-height:1.4"></div></div>"""

if 'id="stageSelect"' not in html:
    html = html.replace(old_modal_start, new_modal_start)

# 4. JavaScript Innovations (Sunlight, Voice, Wind Radar, Microclimate DRI, Prescriptions, Zalo)
js_innovations = """
// ==================== CẢI TIẾN ĐỘT PHÁ V4 CHO NÔNG DÂN ====================

// 1. Chế độ Nắng Chói Ngoài Đồng
window.toggleSunMode = function() {
    document.body.classList.toggle('sun-mode');
    const isSun = document.body.classList.contains('sun-mode');
    const btn = document.getElementById('btnSunMode');
    if (btn) {
        btn.textContent = isSun ? '🌙 Chế độ Thường' : '☀️ Nắng Chói';
        btn.style.background = isSun ? '#facc15' : '#fff';
        btn.style.color = isSun ? '#000' : 'inherit';
    }
};

// 2. Zero-Typing: Tự động tính tuổi lúa & Giai đoạn từ ngày gieo
window.updateCropStageFromDate = function() {
    const sowInput = document.getElementById('sow');
    const ageInput = document.getElementById('age');
    const stageSelect = document.getElementById('stageSelect');
    if (!sowInput || !sowInput.value) return;
    
    const sowDate = new Date(sowInput.value);
    const today = new Date();
    const ageDays = Math.max(1, Math.floor((today - sowDate) / (1000 * 60 * 60 * 24)));
    if (ageInput) ageInput.value = ageDays + ' ngày';

    if (stageSelect) {
        if (ageDays <= 15) stageSelect.value = "Mạ";
        else if (ageDays <= 40) stageSelect.value = "Đẻ nhánh";
        else if (ageDays <= 65) stageSelect.value = "Làm đòng";
        else if (ageDays <= 85) stageSelect.value = "Trổ";
        else if (ageDays <= 100) stageSelect.value = "Chín sữa";
        else stageSelect.value = "Chín";
    }
};

// 3. Trợ lý Giọng nói Tiếng Việt (Web Speech API)
let speechRecognizer = null;
let isRecognizing = false;

window.startVoiceInput = function() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const btn = document.getElementById('btnVoiceInput');
    const noteInput = document.getElementById('noteInput');
    const voiceStatus = document.getElementById('voiceStatus');
    
    if (!SpeechRecognition) {
        alert("Trình duyệt hiện tại chưa hỗ trợ Web Speech API. Bác vui lòng dùng trình duyệt Google Chrome trên điện thoại để nói.");
        return;
    }

    if (isRecognizing) {
        if (speechRecognizer) speechRecognizer.stop();
        isRecognizing = false;
        if (btn) { btn.textContent = '🎙️ Nói'; btn.style.background = '#2563eb'; }
        return;
    }

    speechRecognizer = new SpeechRecognition();
    speechRecognizer.lang = 'vi-VN';
    speechRecognizer.continuous = false;
    speechRecognizer.interimResults = false;

    if (voiceStatus) {
        voiceStatus.style.display = 'block';
        voiceStatus.style.background = '#eff6ff';
        voiceStatus.style.color = '#1e40af';
        voiceStatus.innerHTML = '🎙️ <b>Bác đang nói...</b> Hãy đọc triệu chứng (ví dụ: <i>cháy chóp lá, đốm mắt én, rầy nâu ở gốc</i>)';
    }
    if (btn) { btn.textContent = '⏹️ Dừng'; btn.style.background = '#ef4444'; }
    isRecognizing = true;

    speechRecognizer.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        if (noteInput) {
            noteInput.value = (noteInput.value ? noteInput.value + '; ' : '') + transcript;
        }
        analyzeVoiceSymptom(transcript);
    };

    speechRecognizer.onerror = function(event) {
        if (voiceStatus) {
            voiceStatus.innerHTML = '⚠️ Chưa nghe rõ âm thanh (' + (event.error || 'thử lại') + '). Bác hãy bấm Nói lại lần nữa.';
        }
        isRecognizing = false;
        if (btn) { btn.textContent = '🎙️ Nói'; btn.style.background = '#2563eb'; }
    };

    speechRecognizer.onend = function() {
        isRecognizing = false;
        if (btn) { btn.textContent = '🎙️ Nói'; btn.style.background = '#2563eb'; }
    };

    try {
        speechRecognizer.start();
    } catch(e) {
        console.warn("Speech start error:", e);
    }
};

function analyzeVoiceSymptom(text) {
    const t = text.toLowerCase();
    const voiceStatus = document.getElementById('voiceStatus');
    let advice = "";

    if (t.includes('mắt én') || t.includes('đạo ôn') || t.includes('hình thoi') || t.includes('cháy lá')) {
        advice = "💡 <b>AI nhận diện từ giọng nói:</b> Có dấu hiệu <b>Bệnh Đạo Ôn</b>. Lưu ý ngưng bón đạm, thăm chóp lá cờ!";
    } else if (t.includes('khô vằn') || t.includes('bẹ lá') || t.includes('da hổ')) {
        advice = "💡 <b>AI nhận diện:</b> Triệu chứng <b>Bệnh Khô Vằn</b> ở bẹ lá sát mặt nước. Giữ nước ngập vừa phải.";
    } else if (t.includes('đốm nâu') || t.includes('hạt cau')) {
        advice = "💡 <b>AI nhận diện:</b> Dấu hiệu <b>Đốm Nâu</b> thường do thiếu dinh dưỡng hoặc đất phèn.";
    } else if (t.includes('bạc lá') || t.includes('cháy mép') || t.includes('vi khuẩn')) {
        advice = "💡 <b>AI nhận diện:</b> Triệu chứng <b>Bạc Lá (Cháy bìa lá do vi khuẩn)</b>, dễ lây theo nước mưa.";
    } else if (t.includes('rầy') || t.includes('vàng lùn') || t.includes('lúa cỏ')) {
        advice = "💡 <b>AI nhận diện:</b> Nguy cơ <b>Rầy Nâu / Bệnh Vàng Lùn</b>. Hãy vạch sát gốc lúa kiểm tra rầy cám!";
    } else if (t.includes('đen rễ') || t.includes('thối rễ') || t.includes('hữu cơ')) {
        advice = "💡 <b>AI nhận diện:</b> Dấu hiệu <b>Ngộ độc hữu cơ / Nghẹt rễ</b> do rơm rạ mục yếm khí. Hãy thay nước ngay!";
    }

    if (voiceStatus) {
        if (advice) {
            voiceStatus.style.background = '#fef3c7';
            voiceStatus.style.color = '#92400e';
            voiceStatus.innerHTML = `✅ <i>"${text}"</i><br>${advice}`;
        } else {
            voiceStatus.style.background = '#f0fdf4';
            voiceStatus.style.color = '#166534';
            voiceStatus.innerHTML = `✅ Đã ghi nhận: <i>"${text}"</i>`;
        }
    }
}

// 4. Giọng Nói Đọc To Khuyến Cáo (Speech Synthesis Text-To-Speech)
window.speakAdvice = function(text) {
    if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
        const clean = text.replace(/<[^>]*>?/gm, '').replace(/•/g, ', ');
        const u = new SpeechSynthesisUtterance(clean);
        u.lang = 'vi-VN';
        u.rate = 0.95;
        window.speechSynthesis.speak(u);
    } else {
        alert("Trình duyệt không hỗ trợ phát âm thanh giọng đọc.");
    }
};

// 5. Radar Gió & Cảnh Báo Lây Lan Dịch Tễ Liên Hộ (Neighborhood Wind Vector Radar)
let windLayerGroup = L.layerGroup().addTo(map);
let windRadarActive = false;
let currentWind = { speed: 15, deg: 45, text: "Đông Bắc" };

function getWindCone(lat, lng, distKm, bearingDeg, spreadAngleDeg = 45) {
    const pts = [[lat, lng]];
    const startAngle = bearingDeg - spreadAngleDeg / 2;
    const endAngle = bearingDeg + spreadAngleDeg / 2;
    const steps = 12;
    for (let i = 0; i <= steps; i++) {
        const rad = (startAngle + (endAngle - startAngle) * (i / steps)) * Math.PI / 180;
        const dLat = (distKm / 111) * Math.cos(rad);
        const dLng = (distKm / (111 * Math.cos(lat * Math.PI / 180))) * Math.sin(rad);
        pts.push([lat + dLat, lng + dLng]);
    }
    return pts;
}

window.toggleWindRadar = function() {
    windRadarActive = !windRadarActive;
    windLayerGroup.clearLayers();
    const btn = document.getElementById('btnWindRadar');
    
    if (!windRadarActive) {
        if (btn) { btn.style.background = '#fff'; btn.style.color = 'inherit'; }
        return;
    }
    
    if (btn) { btn.style.background = '#3b82f6'; btn.style.color = '#fff'; }

    const center = map.getCenter();
    // Gọi Open-Meteo lấy gió thật theo tọa độ bản đồ
    fetch(`https://api.open-meteo.com/v1/forecast?latitude=${center.lat.toFixed(4)}&longitude=${center.lng.toFixed(4)}&current_weather=true`)
        .then(r => r.json())
        .then(wd => {
            if (wd && wd.current_weather) {
                currentWind.speed = wd.current_weather.windspeed;
                currentWind.deg = wd.current_weather.winddirection;
            }
            renderWindOverlay();
        })
        .catch(e => {
            console.log("Dùng gió vi khí hậu mặc định:", e);
            renderWindOverlay();
        });
};

function renderWindOverlay() {
    windLayerGroup.clearLayers();
    // Gió thổi TỪ góc deg nên hướng phát tán sâu bệnh là (deg + 180) % 360
    const blowToDeg = (currentWind.deg + 180) % 360;
    const redPoints = data.filter(x => x.s === 'red');

    if (redPoints.length === 0) {
        alert("Hiện tại không có điểm dịch đỏ nào trên bản đồ để dựng quạt phát tán gió.");
        return;
    }

    redPoints.forEach(p => {
        const cone = getWindCone(p.lat, p.lng, 0.9, blowToDeg, 50);
        const poly = L.polygon(cone, {
            color: '#dc2626',
            weight: 2,
            fillColor: '#ef4444',
            fillOpacity: 0.28,
            dashArray: '5, 5'
        }).addTo(windLayerGroup);

        poly.bindPopup(`
            <div style="font-size:11px;min-width:180px">
                <b style="color:#dc2626">⚠️ VÙNG PHÁT TÁN XUÔI GIÓ</b><br>
                Ổ bệnh: <b>${p.f} · ${p.d}</b><br>
                Gió: <b>${currentWind.speed} km/h</b> (Hướng ${blowToDeg.toFixed(0)}°)<br>
                <div style="margin-top:6px;background:#fef2f2;padding:6px;border-radius:6px;color:#991b1b">
                    Bà con có ruộng trong vùng nón 900m này cần vạch lá kiểm tra mé ruộng đón gió ngay!
                </div>
            </div>
        `);
    });

    alert(`🧭 Radar dịch tễ đã bật:\n- Tốc độ gió: ${currentWind.speed} km/h\n- Hướng dịch phát tán: ${blowToDeg.toFixed(0)}°\n- Đã khoanh vùng bảo vệ cho ${redPoints.length} ổ bệnh.`);
}

// 6. Dược thư & Kê Đơn Kinh Tế Thông Minh
const PRESCRIPTIONS = {
    'fungal_dao_on': {
        eco: 'Tricyclazole 75% WP (Beam, Bump...) — Giá rẻ ~30.000đ - 35.000đ/bình 25L',
        pro: 'Fenoxanil + Isoprothiolane (Fuji-one, Filia...) — Đặc trị dứt điểm ~60.000đ/bình 25L',
        phi: '14 ngày (Ngưng xịt trước thu hoạch)',
        note: 'Tuyệt đối ngưng bón phân đạm (Ure) và không xịt phân bón lá khi ruộng đang có vết bệnh!'
    },
    'fungal_kho_van': {
        eco: 'Validamycin 3SL / 5SL — Chi phí tiết kiệm ~20.000đ - 25.000đ/bình 25L',
        pro: 'Hexaconazole (Anvil 5SC) hoặc Azoxystrobin (Amistar Top) ~55.000đ/bình 25L',
        phi: '7 ngày',
        note: 'Xịt ướt đều gốc bẹ lá, rút bớt nước trong ruộng để tán thông thoáng.'
    },
    'fungal_brown_spot': {
        eco: 'Mancozeb 80WP hoặc Difenoconazole — ~30.000đ/bình 25L',
        pro: 'Tebuconazole + Trifloxystrobin (Nativo) ~65.000đ/bình 25L',
        phi: '10 ngày',
        note: 'Bổ sung thêm phân Kali và lân nung chảy, tránh để ruộng cạn kiệt thiếu dinh dưỡng.'
    },
    'bacterial_bac_la': {
        eco: 'Kasugamycin (Kasumin) — ~28.000đ/bình 25L',
        pro: 'Oxolinic acid (Starner) hoặc Bronopol ~60.000đ/bình 25L',
        phi: '10 ngày',
        note: 'Vi khuẩn lây theo giọt sương và mưa gió. Phun khi lá khô ráo lúc sáng sớm hoặc chiều mát.'
    },
    'viral_grassy_stunt': {
        eco: 'Pymetrozine (Chess) hoặc Dinotefuran để trừ rầy nâu truyền bệnh ~35.000đ/bình',
        pro: 'Kết hợp diệt rầy và nhổ bỏ tiêu hủy bụi lúa bệnh tránh lây lan cả ruộng',
        phi: '14 ngày',
        note: 'Bệnh do virus nên không có thuốc chữa cây đã nhiễm; mấu chốt là dập tắt rầy nâu môi giới!'
    },
    'physio_organic_toxicity': {
        eco: 'Tháo cạn nước phơi ruộng nứt chân chim 3-5 ngày + Rải vôi bột (20-30kg/công)',
        pro: 'Bổ sung lân nung chảy hoặc Axit Humic tưới gốc để kích rễ mới trắng lại',
        phi: 'Không cách ly hóa chất (Rối loạn sinh lý)',
        note: 'Không xịt thuốc sâu rầy lúc này; rễ đang nghẹt xịt hóa chất cây càng suy kiệt nặng!'
    }
};

// 7. Chia Sẻ 1-Chạm Qua Zalo Cho Khuyến Nông Xã
window.shareToZalo = function(field, disease, age, stage, lat, lng) {
    const text = `🌾 BÁO CÁO BỆNH CÂY LÚA - AI RICE 4.0\\n` +
                 `• Khu vực: Ruộng ${field}\\n` +
                 `• Tuổi lúa: ${age} ngày (${stage})\\n` +
                 `• AI Nhận diện: ${disease}\\n` +
                 `• Tọa độ GPS: ${lat.toFixed(6)}, ${lng.toFixed(6)}\\n` +
                 `• Bản đồ: https://maps.google.com/?q=${lat},${lng}\\n` +
                 `Nhờ Kỹ sư Khuyến nông tư vấn giúp biện pháp xử lý an toàn!`;
                 
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text);
        alert("✅ Đã sao chép nội dung báo cáo! Đang mở Zalo để bác dán gửi cho Cán bộ Khuyến nông hoặc Đại lý thuốc.");
    }
    window.open("https://zalo.me/", "_blank");
};
"""

if "// ==================== CẢI TIẾN ĐỘT PHÁ V4 CHO NÔNG DÂN ====================" not in html:
    html = html.replace('</script>\n</body></html>', js_innovations + '\n</script>\n</body></html>')

# 5. Update detail(x) function to include Audio Voice output, Prescription, and Zalo Sharing
detail_patch_target = """  '<div class="grid"><div class="info"><b>'+x.a+' ngày</b><span>Tuổi lúa</span></div><div class="info"><b>'+x.g+'</b><span>Giai đoạn</span></div></div>'+
  (d ? '<div class="rec"><b>🌱 Khuyến cáo quản lý</b><br>'+rec+'</div>'+
       '<div class="warn"><b>🔎 Chẩn đoán phân biệt</b><br>'+diff+'</div>'+
       '<div style="margin-top:9px"><b style="font-size:10px">👁️ Đặc trưng hình ảnh cho AI</b><div class="pills">'+d.ai_visual_features.map(z=>'<span class="pill">'+z+'</span>').join('')+'</div></div>'
      : '')+"""

detail_patch_replacement = """  '<div class="grid"><div class="info"><b>'+x.a+' ngày</b><span>Tuổi lúa</span></div><div class="info"><b>'+x.g+'</b><span>Giai đoạn</span></div></div>'+
  (d ? '<div style="display:flex;gap:6px;margin-top:8px"><button type="button" class="wide" style="flex:1;background:#3b82f6;color:#fff;font-weight:700;padding:8px" onclick="speakAdvice(\\'Khuyến cáo cho '+d.name_vi+': '+d.management.join('. ')+'\\')">🔊 Nghe đọc to</button><button type="button" class="wide" style="flex:1;background:#059669;color:#fff;font-weight:700;padding:8px" onclick="shareToZalo(\\''+x.f+'\\',\\''+x.d+'\\',\\''+x.a+'\\',\\''+x.g+'\\','+x.lat+','+x.lng+')">📲 Gửi Zalo</button></div>' : '')+
  (d && PRESCRIPTIONS[d.id] ? 
    '<div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:9px;padding:9px;margin-top:9px;font-size:10px;line-height:1.5">' +
    '<b style="color:#1e40af">💊 KÊ ĐƠN THUỐC BVTV KINH TẾ (TIẾT KIỆM)</b><br>' +
    '• <b>Tiết kiệm:</b> ' + PRESCRIPTIONS[d.id].eco + '<br>' +
    '• <b>Đặc trị:</b> ' + PRESCRIPTIONS[d.id].pro + '<br>' +
    '• <b>Thời gian cách ly (PHI):</b> <span style="color:#dc2626;font-weight:700">' + PRESCRIPTIONS[d.id].phi + '</span><br>' +
    '• <i>Lưu ý:</i> ' + PRESCRIPTIONS[d.id].note + '</div>' : '')+
  (d ? '<div class="rec"><b>🌱 Khuyến cáo quản lý</b><br>'+rec+'</div>'+
       '<div class="warn"><b>🔎 Chẩn đoán phân biệt</b><br>'+diff+'</div>'+
       '<div style="margin-top:9px"><b style="font-size:10px">👁️ Đặc trưng hình ảnh cho AI</b><div class="pills">'+d.ai_visual_features.map(z=>'<span class="pill">'+z+'</span>').join('')+'</div></div>'
      : '')+"""

if "💊 KÊ ĐƠN THUỐC BVTV KINH TẾ" not in html:
    html = html.replace(detail_patch_target, detail_patch_replacement)

# 6. Update openCheck to trigger updateCropStageFromDate
if "updateCropStageFromDate()" not in html:
    html = html.replace("age.value=Math.floor((Date.now()-new Date(sow.value))/86400000)", "updateCropStageFromDate()")

# 7. Update tab 'tasks' with Microclimate Weather & DRI
task_old = """list.innerHTML='<div class="item"><div style="font-size:25px">🔴</div><div><div class="title">A3 — Bệnh đạo ôn</div><div class="meta">Cần kiểm tra lại và đối chiếu điều kiện ruộng.</div></div></div>'+
    '<div class="item"><div style="font-size:25px">🟡</div><div><div class="title">B2 — Theo dõi</div><div class="meta">Kiểm tra trong 3 ngày.</div></div></div>';"""

task_new = """list.innerHTML='<div style="background:#eff6ff;border:1px solid #bfdbfe;border-radius:10px;padding:10px;margin-bottom:8px">' +
    '<div style="display:flex;justify-content:space-between;align-items:center"><b style="font-size:11px;color:#1e40af">🌦️ VI KHÍ HẬU & DỰ BÁO BỆNH (DRI)</b><span style="font-size:9px;background:#dbeafe;padding:2px 6px;border-radius:10px;color:#1e40af">ĐBSCL</span></div>' +
    '<div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-top:6px;font-size:10px">' +
    '<div>Nhiệt độ: <b>26.5°C</b></div><div>Độ ẩm: <b style="color:#dc2626">93% (Rất cao)</b></div>' +
    '<div>Sương mù: <b>Kéo dài 4h</b></div><div>Gió: <b>15 km/h Đông Bắc</b></div></div>' +
    '<div style="margin-top:8px;padding:6px;border-radius:6px;background:#fee2e2;color:#991b1b;font-size:10px;line-height:1.4">' +
    '🔴 <b>BÁO ĐỘNG ĐẠO ÔN (DRI: 84%):</b> Vi khí hậu rất thuận lợi cho nấm đạo ôn bùng phát trong 48h tới. Ngưng ngay phân Ure, chuẩn bị xịt ngừa Tricyclazole!' +
    '</div></div>' +
    '<h4 style="margin:6px 0;font-size:11px">Việc đồng ruộng khẩn cấp:</h4>' +
    '<div class="item"><div style="font-size:25px">🔴</div><div><div class="title">A3 — Bệnh đạo ôn lá</div><div class="meta">Cần xịt dập dịch trong chiều nay & kiểm tra mé đón gió.</div></div></div>'+
    '<div class="item"><div style="font-size:25px">🟡</div><div><div class="title">B2 — Vết đốm nghi ngờ</div><div class="meta">Kiểm tra lại sau 48h.</div></div></div>';"""

if "VI KHÍ HẬU & DỰ BÁO BỆNH (DRI)" not in html:
    html = html.replace(task_old, task_new)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html)

print("SUCCESS: index.html updated with V4 Innovations!")
