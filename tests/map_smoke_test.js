/**
 * AUTOMATED SMOKE TEST - CAY LUA MAP
 * 
 * Instructions: Run this script inside the browser console at http://localhost:8080/index.html
 * Or use Puppeteer/Playwright to automate the execution.
 */

async function runMapSmokeTest() {
    console.log("🚀 STARTING MAP SMOKE TEST...");
    let passed = 0;
    let failed = 0;

    function assert(condition, message) {
        if (condition) {
            console.log("✅ PASS:", message);
            passed++;
        } else {
            console.error("❌ FAIL:", message);
            failed++;
        }
    }

    // 1. Map Initialization
    assert(typeof map !== 'undefined' && map !== null, "Leaflet Map object is initialized.");
    assert(document.getElementById('map').innerHTML.includes('leaflet-pane'), "Map container has Leaflet DOM elements.");

    // 2. Marker Creation
    let initialMarkerCount = window.ms ? window.ms.length : 0;
    assert(initialMarkerCount > 0, `Map has markers loaded (${initialMarkerCount} markers).`);

    // 3. Coordinate update & Click Simulation
    if (typeof map.fire === 'function') {
        map.fire('click', { latlng: L.latLng(10.05, 105.74) });
        assert(window.selectedPos !== null && window.selectedPos.lat === 10.05, "Map click registers coordinates successfully.");
        
        let popupOpen = document.querySelector('.leaflet-popup');
        assert(popupOpen !== null, "Popup opens on map click.");
    } else {
        assert(false, "Map fire method missing.");
    }

    // 4. Layer Switching (Road / Sat)
    assert(typeof window.setBaseLayer === 'function', "setBaseLayer function exists.");
    try {
        window.setBaseLayer('sat');
        assert(true, "Switched to Satellite Layer successfully.");
        window.setBaseLayer('road');
        assert(true, "Switched to Road Layer successfully.");
    } catch (e) {
        assert(false, "Layer switching threw an error.");
    }

    // 5. Upload Flow & Queue (Offline Check)
    assert(typeof SyncService !== 'undefined' && typeof SyncService.addQueue === 'function', "SyncService (IndexedDB) is available for Offline-First upload.");
    
    // 6. Supabase Failure Handling
    let isSupabaseLoaded = typeof SupabaseService !== 'undefined' && SupabaseService.client !== null;
    if (!isSupabaseLoaded) {
        console.warn("⚠️ Supabase Client is null (expected if no internet or invalid keys). System should fallback to local Mock/IndexedDB.");
    }
    assert(typeof window.render === 'function', "UI Render function remains intact even if DB state varies.");

    // 7. AI Fallback
    assert(typeof window.testServer === 'function' && typeof window.checkAIHealth === 'function', "AI Health checks and fallback mechanisms are defined.");

    console.log("--------------------------------------");
    console.log(`🏁 TEST COMPLETE: ${passed} PASS, ${failed} FAIL.`);
}

// Automatically expose to window
window.runMapSmokeTest = runMapSmokeTest;
console.log("ℹ️ Type 'runMapSmokeTest()' to execute the smoke test.");
