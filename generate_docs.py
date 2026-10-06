import os

# Write PROJECT_AUDIT.md
with open("docs/PROJECT_AUDIT.md", "w", encoding="utf-8") as f:
    f.write("""# PROJECT AUDIT
1. **Entry point HTML**: AI_Rice_UX_Prototype_V3_CLICK_POPUP_FINAL.html
2. **Entry point server**: server.py (FastAPI)
3. **Model path**: best02.pt (fallback to best.pt)
4. **Model version**: YOLOv8
5. **API hiện tại**: Supabase SDK, Local FastAPI YOLO, PlantNet
6. **Storage hiện tại**: Supabase (via supabase-js)
7. **History hiện tại**: Supabase `inspections` table
8. **Authentication hiện tại**: RLS with Anon Key for prototype
9. **Config hiện tại**: `CAYLUA_CONFIG` in HTML
10. **Test hiện tại**: manual testing, mock AI fallback
11. **Khởi động**: run_server.bat & mở HTML
12. **File đang sử dụng**: HTML, server.py, run_server.bat
13. **File cũ**: temp files, old V2 HTML.
""")

# Write ARCHITECTURE_PLAN.md
with open("docs/ARCHITECTURE_PLAN.md", "w", encoding="utf-8") as f:
    f.write("""# ARCHITECTURE PLAN
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
""")

# Write SUPABASE_SCHEMA.md
with open("docs/SUPABASE_SCHEMA.md", "w", encoding="utf-8") as f:
    f.write("""# SUPABASE SCHEMA
Includes `diseases` and `inspections` tables, satisfying the project needs for history and knowledge base.
""")

# Write migrations
with open("supabase/migrations/001_initial_schema.sql", "w", encoding="utf-8") as f:
    f.write("""
CREATE TABLE IF NOT EXISTS public.diseases (
    id TEXT PRIMARY KEY,
    name_vi TEXT NOT NULL,
    name_en TEXT,
    disease_group TEXT,
    causal_agent TEXT,
    symptoms JSONB,
    favorable_conditions JSONB,
    management JSONB,
    differential JSONB,
    ai_visual_features JSONB,
    vector_or_spread TEXT,
    target_organs JSONB
);

CREATE TABLE IF NOT EXISTS public.inspections (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    field_name TEXT NOT NULL,
    disease_id TEXT REFERENCES public.diseases(id) ON DELETE SET NULL,
    disease_name TEXT,
    status_color TEXT,
    confidence TEXT,
    age_days INTEGER,
    growth_stage TEXT,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    location_source TEXT,
    ai_provider TEXT,
    job_id TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

ALTER TABLE public.diseases ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Cho phép đọc công khai diseases" ON public.diseases FOR SELECT USING (true);

ALTER TABLE public.inspections ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Cho phép đọc công khai inspections" ON public.inspections FOR SELECT USING (true);
CREATE POLICY "Cho phép insert công khai inspections" ON public.inspections FOR INSERT WITH CHECK (true);
CREATE POLICY "Cho phép xóa công khai inspections" ON public.inspections FOR DELETE USING (true);
""")

# Write IMPLEMENTATION_REPORT.md
with open("docs/IMPLEMENTATION_REPORT.md", "w", encoding="utf-8") as f:
    f.write("""# IMPLEMENTATION REPORT
1. **Xây dựng**: Tích hợp AI Adapter linh hoạt với FastAPI YOLO, Fallback PlantNet, và Supabase DB.
2. **Files tạo**: `server.py`, `run_server.bat`, `docs/`, `supabase/migrations/`
3. **Files sửa**: `AI_Rice_UX_Prototype_V3_CLICK_POPUP_FINAL.html` (thêm Supabase SDK, AI Adapter, Fallback)
4. **API contracts**: `/health`, `/analyze_mobile`
5. **AI providers**: `caylua-yolov8`, `plantnet`, `mock-ai`
6. **Error handling**: Supabase try-catch fallback to local state, Model import try-catch.
7. **Cách khởi động**: Chạy `run_server.bat` -> Mở HTML.
""")
