# ARCHITECTURE PLAN
```text
HTML -> AI Adapter -> Health Check -> YOLO Server? 
YES -> YOLO
NO -> API Fallback -> PlantNet
Normalizer -> Supabase -> Map/History
```
Sequence Diagram:
1. User clicks map -> selects location -> uploads image
2. AI Adapter pings YOLO -> if OK -> posts image -> gets mapped disease & confidence
3. If YOLO fails -> pings PlantNet -> gets result
4. Normalizer formats result -> inserts to Supabase
5. Render updates map and history from Supabase.
