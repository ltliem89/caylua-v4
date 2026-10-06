
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
