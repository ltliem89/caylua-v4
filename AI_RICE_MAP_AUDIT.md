# AI_RICE_MAP_AUDIT

## 1. Project Overview & Existing Architecture
The AI Rice project (V3) aims to become a map-centric field survey tool.
Currently, the UI is primarily located in `index.html` (which is a duplicate of `AI_Rice_UX_Prototype_V3_CLICK_POPUP_FINAL.html`).
The backend server runs on `server.py` using FastAPI, with Supabase integration.
The database schema (`supabase_schema.sql`) already has the necessary tables: `profiles`, `fields`, `survey_sessions`, `survey_points`, `survey_images`, `ai_results`, `alerts`, `gps_tracks`.
Offline caching logic is partially implemented in `v3_services.js` (using Dexie.js for IndexedDB).

## 2. Component Audits

### A. Map
- **Current State:** Leaflet map exists in `index.html`. It currently renders mockup data (`data` array in JS).
- **Missing:** Realtime sync from Supabase `survey_points` and `ai_results`, marker state rendering based on real DB status (pending, processing, failed, completed). Filter based on map layers.
- **Files to Modify:** `index.html`, `v3_services.js`.

### B. GPS
- **Current State:** Uses `getCurrentPosition()` or mock data.
- **Missing:** Needs `navigator.geolocation.watchPosition()`, auto-follow mode, "Return to My Location" button, and accuracy/status UI.
- **Files to Modify:** `index.html`.

### C. Survey Session & Point
- **Current State:** The mock `saveCheck()` function fakes the survey point creation.
- **Missing:** Real session initialization (creating a `survey_sessions` record), generating `survey_points` tied to actual GPS readings during the session.
- **Files to Modify:** `index.html`, `v3_services.js`.

### D. Camera & Storage
- **Current State:** Storage buckets (`survey-images`) and RLS policies are set up. `server.py` has an `api/ai/predict` endpoint.
- **Missing:** Tight integration of Camera UI -> Local Blob -> Supabase Storage (with correct path `{user_id}/{session_id}/{point_id}/{image_id}/...`) -> triggering AI.
- **Files to Modify:** `index.html`, `v3_services.js`.

### E. AI Server Integration
- **Current State:** `server.py` processes YOLO predictions and saves results to `ai_results`.
- **Missing:** Updating the marker on the map via Supabase Realtime when `ai_results` updates. Ensure backward compatibility of WebSocket and old endpoints.
- **Files to Modify:** `index.html`, `v3_services.js`, `server.py` (if missing any specific webhook/realtime publish).

### F. Realtime
- **Current State:** `v3_services.js` might have Supabase client setup but realtime listeners for map updates are not fully integrated into the UI.
- **Missing:** Realtime subscription to `ai_results` and `survey_points`.
- **Files to Modify:** `index.html`, `v3_services.js`.

### G. Offline & IndexedDB
- **Current State:** Dexie IndexedDB sync queue implemented in `v3_services.js`.
- **Missing:** Ensure `watchPosition` and photo capture gracefully degrade to offline queue. Re-sync queue logic connected to map updates.

### H. Journal
- **Current State:** HTML has a basic journal/history view.
- **Missing:** Bind journal directly to Supabase data (`survey_points` + `ai_results`), allow filtering by map clicks and vice versa.

## 3. Plan & Affected Files
- `index.html`: Refactor to make Map the central UX. Implement `watchPosition`, Marker clustering/rendering logic, Map-Journal interactions, Filter UI.
- `v3_services.js`: Expose Realtime listeners, Survey Session APIs, GPS tracking hooks.
- `server.py`: Verify endpoints. Do not break `/api/ai/predict` or WebSocket.
