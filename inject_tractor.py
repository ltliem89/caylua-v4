import re

with open("AI_Rice_UX_Prototype_V3_CLICK_POPUP_FINAL.html", "r", encoding="utf-8") as f:
    html = f.read()

# Add button
if 'startTractorSim()' not in html:
    html = html.replace('<button onclick="road()">', '<button onclick="startTractorSim()" title="Chạy mô phỏng xe">🚜</button><button onclick="road()">')

# JS Code to inject
tractor_js = """
// TRACTOR SIMULATION LOGIC
let userMarker = null;
let currentHeading = 0;
window.AppState = window.AppState || { autoFollow: true };

function initGPS() {
    if ("geolocation" in navigator) {
        navigator.geolocation.watchPosition(
            (pos) => {
                if(window.simulatingTractor) return; // Ignore real GPS if simulating
                const lat = pos.coords.latitude;
                const lng = pos.coords.longitude;
                updateTractorPos(lat, lng);
            },
            (err) => console.warn(err),
            { enableHighAccuracy: true }
        );
    }
}

function updateTractorPos(lat, lng, heading = null) {
    if(!userMarker) {
        userMarker = L.marker([lat, lng], {
            icon: L.divIcon({
                className: 'tractor-icon',
                html: '<div style="font-size: 24px; transform: rotate(0deg); transition: transform 0.3s; width: 24px; height: 24px; text-align: center; line-height: 24px; margin-left: -12px; margin-top: -12px;">🚜</div>',
                iconSize: [0, 0]
            }),
            zIndexOffset: 1000
        }).addTo(map);
    } else {
        userMarker.setLatLng([lat, lng]);
    }
    
    if(heading !== null) {
        currentHeading = heading;
        const iconDiv = userMarker.getElement().querySelector('div');
        if(iconDiv) {
            // Adjust rotation (tractor emoji usually faces left, so add 90 or adjust based on emoji)
            iconDiv.style.transform = `rotate(${heading}deg)`;
        }
    }
    
    if(AppState.autoFollow) {
        map.setView([lat, lng], map.getZoom());
    }
}

function calculateHeading(lat1, lng1, lat2, lng2) {
    const dLng = (lng2 - lng1) * Math.PI / 180;
    lat1 = lat1 * Math.PI / 180;
    lat2 = lat2 * Math.PI / 180;
    const y = Math.sin(dLng) * Math.cos(lat2);
    const x = Math.cos(lat1) * Math.sin(lat2) - Math.sin(lat1) * Math.cos(lat2) * Math.cos(dLng);
    const brng = Math.atan2(y, x) * 180 / Math.PI;
    return (brng + 360) % 360;
}

window.startTractorSim = async function() {
    if(window.simulatingTractor) return;
    window.simulatingTractor = true;
    
    // Define a path in the field
    const path = [
        {lat: 10.0452, lng: 105.7469},
        {lat: 10.0462, lng: 105.7469},
        {lat: 10.0462, lng: 105.7480},
        {lat: 10.0452, lng: 105.7480},
        {lat: 10.0452, lng: 105.7469}
    ];
    
    let currentLat = path[0].lat;
    let currentLng = path[0].lng;
    updateTractorPos(currentLat, currentLng);
    map.setView([currentLat, currentLng], 17);
    
    for (let i = 1; i < path.length; i++) {
        const targetLat = path[i].lat;
        const targetLng = path[i].lng;
        
        const heading = calculateHeading(currentLat, currentLng, targetLat, targetLng);
        
        // Move in small steps
        const steps = 30;
        const latStep = (targetLat - currentLat) / steps;
        const lngStep = (targetLng - currentLng) / steps;
        
        for (let j = 0; j < steps; j++) {
            currentLat += latStep;
            currentLng += lngStep;
            updateTractorPos(currentLat, currentLng, heading);
            await new Promise(r => setTimeout(r, 100));
        }
    }
    
    window.simulatingTractor = false;
    alert("Mô phỏng hoàn tất!");
}
"""

if 'TRACTOR SIMULATION LOGIC' not in html:
    html = html.replace('// Bootstrap', tractor_js + '\n// Bootstrap')

with open("AI_Rice_UX_Prototype_V3_CLICK_POPUP_FINAL.html", "w", encoding="utf-8") as f:
    f.write(html)
