-- v4_final_schema.sql

-- 1. FIELDS
CREATE TABLE IF NOT EXISTS public.fields (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    area DOUBLE PRECISION,
    rice_variety TEXT,
    sowing_date DATE,
    transplanting_date DATE,
    growth_stage TEXT,
    status TEXT DEFAULT 'active',
    boundary_geojson JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);
ALTER TABLE public.fields ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Users can view own fields" ON public.fields;
CREATE POLICY "Users can view own fields" ON public.fields FOR SELECT USING (auth.uid() = user_id);
DROP POLICY IF EXISTS "Users can insert own fields" ON public.fields;
CREATE POLICY "Users can insert own fields" ON public.fields FOR INSERT WITH CHECK (auth.uid() = user_id);
DROP POLICY IF EXISTS "Users can modify own fields" ON public.fields;
CREATE POLICY "Users can modify own fields" ON public.fields FOR UPDATE USING (auth.uid() = user_id);
DROP POLICY IF EXISTS "Users can delete own fields" ON public.fields;
CREATE POLICY "Users can delete own fields" ON public.fields FOR DELETE USING (auth.uid() = user_id);

-- 2. IMAGES
CREATE TABLE IF NOT EXISTS public.images (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    field_id UUID REFERENCES public.fields(id) ON DELETE CASCADE,
    
    original_filename TEXT,
    storage_path TEXT NOT NULL,
    processed_storage_path TEXT,
    mime_type TEXT,
    file_size INTEGER,
    sha256 TEXT,
    
    captured_at TIMESTAMP WITH TIME ZONE,
    uploaded_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    location_source TEXT DEFAULT 'unknown',
    location_accuracy DOUBLE PRECISION,
    
    device_id TEXT,
    camera_source TEXT,
    width INTEGER,
    height INTEGER,
    orientation INTEGER,
    
    processing_status TEXT DEFAULT 'PENDING_AI',
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);
ALTER TABLE public.images ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Users can view own images" ON public.images;
CREATE POLICY "Users can view own images" ON public.images FOR SELECT USING (auth.uid() = user_id);
DROP POLICY IF EXISTS "Users can insert own images" ON public.images;
CREATE POLICY "Users can insert own images" ON public.images FOR INSERT WITH CHECK (auth.uid() = user_id);
DROP POLICY IF EXISTS "Users can modify own images" ON public.images;
CREATE POLICY "Users can modify own images" ON public.images FOR UPDATE USING (auth.uid() = user_id);

-- 3. AI JOBS
CREATE TABLE IF NOT EXISTS public.ai_jobs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    image_id UUID NOT NULL REFERENCES public.images(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    field_id UUID REFERENCES public.fields(id) ON DELETE CASCADE,
    
    provider TEXT,
    model TEXT,
    model_version TEXT,
    
    status TEXT DEFAULT 'QUEUED',
    request_id TEXT,
    
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    processing_ms INTEGER,
    
    error_code TEXT,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);
ALTER TABLE public.ai_jobs ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Users can view own ai_jobs" ON public.ai_jobs;
CREATE POLICY "Users can view own ai_jobs" ON public.ai_jobs FOR SELECT USING (auth.uid() = user_id);
DROP POLICY IF EXISTS "Users can modify own ai_jobs" ON public.ai_jobs;
CREATE POLICY "Users can modify own ai_jobs" ON public.ai_jobs FOR ALL USING (auth.uid() = user_id);

-- 4. AI ANALYSIS
CREATE TABLE IF NOT EXISTS public.ai_analysis (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    job_id UUID NOT NULL REFERENCES public.ai_jobs(id) ON DELETE CASCADE,
    image_id UUID NOT NULL REFERENCES public.images(id) ON DELETE CASCADE,
    
    provider TEXT,
    model TEXT,
    model_version TEXT,
    
    status TEXT,
    overall_confidence DOUBLE PRECISION,
    summary TEXT,
    raw_result_json JSONB,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);
ALTER TABLE public.ai_analysis ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Users can view own ai_analysis" ON public.ai_analysis;
CREATE POLICY "Users can view own ai_analysis" ON public.ai_analysis FOR SELECT USING (EXISTS (SELECT 1 FROM public.images WHERE images.id = ai_analysis.image_id AND images.user_id = auth.uid()));
DROP POLICY IF EXISTS "Users can modify own ai_analysis" ON public.ai_analysis;
CREATE POLICY "Users can modify own ai_analysis" ON public.ai_analysis FOR ALL USING (EXISTS (SELECT 1 FROM public.images WHERE images.id = ai_analysis.image_id AND images.user_id = auth.uid()));

-- 5. DISEASE DETECTIONS
CREATE TABLE IF NOT EXISTS public.disease_detections (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    analysis_id UUID NOT NULL REFERENCES public.ai_analysis(id) ON DELETE CASCADE,
    image_id UUID NOT NULL REFERENCES public.images(id) ON DELETE CASCADE,
    
    class_id INTEGER,
    disease_code TEXT,
    disease_name TEXT,
    confidence DOUBLE PRECISION,
    
    bbox_x DOUBLE PRECISION,
    bbox_y DOUBLE PRECISION,
    bbox_width DOUBLE PRECISION,
    bbox_height DOUBLE PRECISION,
    
    severity TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);
ALTER TABLE public.disease_detections ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Users can view own disease_detections" ON public.disease_detections;
CREATE POLICY "Users can view own disease_detections" ON public.disease_detections FOR SELECT USING (EXISTS (SELECT 1 FROM public.images WHERE images.id = disease_detections.image_id AND images.user_id = auth.uid()));
DROP POLICY IF EXISTS "Users can modify own disease_detections" ON public.disease_detections;
CREATE POLICY "Users can modify own disease_detections" ON public.disease_detections FOR ALL USING (EXISTS (SELECT 1 FROM public.images WHERE images.id = disease_detections.image_id AND images.user_id = auth.uid()));

-- 6. INSPECTIONS (Check if exists first)
DROP TABLE IF EXISTS public.inspections CASCADE;
CREATE TABLE public.inspections (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    field_id UUID REFERENCES public.fields(id) ON DELETE CASCADE,
    image_id UUID REFERENCES public.images(id) ON DELETE SET NULL,
    ai_job_id UUID REFERENCES public.ai_jobs(id) ON DELETE SET NULL,
    
    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,
    location_source TEXT,
    
    captured_at TIMESTAMP WITH TIME ZONE,
    crop_age_days INTEGER,
    growth_stage TEXT,
    
    status TEXT,
    severity TEXT,
    notes TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);
ALTER TABLE public.inspections ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Users can view own inspections" ON public.inspections;
CREATE POLICY "Users can view own inspections" ON public.inspections FOR SELECT USING (auth.uid() = user_id);
DROP POLICY IF EXISTS "Users can modify own inspections" ON public.inspections;
CREATE POLICY "Users can modify own inspections" ON public.inspections FOR ALL USING (auth.uid() = user_id);

-- 7. INSIGHTS
CREATE TABLE IF NOT EXISTS public.insights (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    field_id UUID REFERENCES public.fields(id) ON DELETE CASCADE,
    inspection_id UUID REFERENCES public.inspections(id) ON DELETE CASCADE,
    image_id UUID REFERENCES public.images(id) ON DELETE SET NULL,
    
    insight_type TEXT,
    title TEXT,
    message TEXT,
    severity TEXT,
    
    source TEXT,
    confidence DOUBLE PRECISION,
    
    related_disease TEXT,
    related_alert UUID,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE
);
ALTER TABLE public.insights ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Users can view own insights" ON public.insights;
CREATE POLICY "Users can view own insights" ON public.insights FOR SELECT USING (auth.uid() = user_id);
DROP POLICY IF EXISTS "Users can modify own insights" ON public.insights;
CREATE POLICY "Users can modify own insights" ON public.insights FOR ALL USING (auth.uid() = user_id);

-- 8. REMINDERS
CREATE TABLE IF NOT EXISTS public.reminders (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    field_id UUID REFERENCES public.fields(id) ON DELETE CASCADE,
    inspection_id UUID REFERENCES public.inspections(id) ON DELETE CASCADE,
    
    type TEXT,
    title TEXT,
    message TEXT,
    
    scheduled_at TIMESTAMP WITH TIME ZONE NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE,
    status TEXT DEFAULT 'pending',
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);
ALTER TABLE public.reminders ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Users can view own reminders" ON public.reminders;
CREATE POLICY "Users can view own reminders" ON public.reminders FOR SELECT USING (auth.uid() = user_id);
DROP POLICY IF EXISTS "Users can modify own reminders" ON public.reminders;
CREATE POLICY "Users can modify own reminders" ON public.reminders FOR ALL USING (auth.uid() = user_id);

-- 9. AI FEEDBACK
CREATE TABLE IF NOT EXISTS public.ai_feedback (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    inspection_id UUID REFERENCES public.inspections(id) ON DELETE CASCADE,
    ai_job_id UUID REFERENCES public.ai_jobs(id) ON DELETE CASCADE,
    
    feedback_type TEXT,
    comment TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);
ALTER TABLE public.ai_feedback ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Users can view own ai_feedback" ON public.ai_feedback;
CREATE POLICY "Users can view own ai_feedback" ON public.ai_feedback FOR SELECT USING (auth.uid() = user_id);
DROP POLICY IF EXISTS "Users can modify own ai_feedback" ON public.ai_feedback;
CREATE POLICY "Users can modify own ai_feedback" ON public.ai_feedback FOR ALL USING (auth.uid() = user_id);

-- 10. ALERTS
CREATE TABLE IF NOT EXISTS public.alerts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    field_id UUID REFERENCES public.fields(id) ON DELETE CASCADE,
    inspection_id UUID REFERENCES public.inspections(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    title TEXT,
    type TEXT,
    severity TEXT,
    action TEXT,
    is_read BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    read_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE
);
ALTER TABLE public.alerts ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Users can view own alerts" ON public.alerts;
CREATE POLICY "Users can view own alerts" ON public.alerts FOR SELECT USING (auth.uid() = user_id);
DROP POLICY IF EXISTS "Users can modify own alerts" ON public.alerts;
CREATE POLICY "Users can modify own alerts" ON public.alerts FOR ALL USING (auth.uid() = user_id);

-- 11. INDEXES
CREATE INDEX IF NOT EXISTS images_user_created_idx ON public.images(user_id, created_at);
CREATE INDEX IF NOT EXISTS images_field_captured_idx ON public.images(field_id, captured_at);
CREATE INDEX IF NOT EXISTS ai_jobs_user_status_idx ON public.ai_jobs(user_id, status, created_at);
CREATE INDEX IF NOT EXISTS inspections_user_idx ON public.inspections(user_id, created_at);
CREATE INDEX IF NOT EXISTS alerts_user_read_idx ON public.alerts(user_id, is_read, created_at);
CREATE INDEX IF NOT EXISTS disease_detections_image_idx ON public.disease_detections(image_id);
CREATE INDEX IF NOT EXISTS disease_detections_analysis_idx ON public.disease_detections(analysis_id);

-- 12. STORAGE
INSERT INTO storage.buckets (id, name, public) VALUES ('survey-images', 'survey-images', false) ON CONFLICT DO NOTHING;
DROP POLICY IF EXISTS "Users can view own survey images" ON storage.objects;
CREATE POLICY "Users can view own survey images" ON storage.objects FOR SELECT USING (bucket_id = 'survey-images' AND auth.uid()::text = (string_to_array(name, '/'))[1]);
DROP POLICY IF EXISTS "Users can upload own survey images" ON storage.objects;
CREATE POLICY "Users can upload own survey images" ON storage.objects FOR INSERT WITH CHECK (bucket_id = 'survey-images' AND auth.uid()::text = (string_to_array(name, '/'))[1]);
