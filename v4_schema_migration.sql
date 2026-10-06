-- v4_schema_migration.sql

-- 1. FIELDS (UPDATE)
ALTER TABLE public.fields ADD COLUMN IF NOT EXISTS sowing_date DATE;
ALTER TABLE public.fields ADD COLUMN IF NOT EXISTS transplanting_date DATE;
ALTER TABLE public.fields ADD COLUMN IF NOT EXISTS growth_stage TEXT;
ALTER TABLE public.fields ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'active';
ALTER TABLE public.fields ADD COLUMN IF NOT EXISTS boundary_geojson JSONB;

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

-- 6. INSPECTIONS
CREATE TABLE IF NOT EXISTS public.inspections (
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

-- 10. INDEXES
CREATE INDEX IF NOT EXISTS images_user_created_idx ON public.images(user_id, created_at);
CREATE INDEX IF NOT EXISTS images_field_captured_idx ON public.images(field_id, captured_at);
CREATE INDEX IF NOT EXISTS ai_jobs_user_status_idx ON public.ai_jobs(user_id, status, created_at);
CREATE INDEX IF NOT EXISTS inspections_user_idx ON public.inspections(user_id, created_at);
CREATE INDEX IF NOT EXISTS alerts_user_read_idx ON public.alerts(user_id, is_read, created_at);
CREATE INDEX IF NOT EXISTS disease_detections_image_idx ON public.disease_detections(image_id);
CREATE INDEX IF NOT EXISTS disease_detections_analysis_idx ON public.disease_detections(analysis_id);

-- 11. RLS POLICIES (Simplified for user ownership)
DO $$ 
DECLARE
    tbl text;
BEGIN
    FOR tbl IN SELECT unnest(ARRAY['images', 'ai_jobs', 'ai_analysis', 'disease_detections', 'inspections', 'insights', 'reminders', 'ai_feedback'])
    LOOP
        EXECUTE format('DROP POLICY IF EXISTS "Users can view own %I" ON public.%I', tbl, tbl);
        EXECUTE format('DROP POLICY IF EXISTS "Users can modify own %I" ON public.%I', tbl, tbl);
        
        -- Analysis & Detections don't have user_id, they link to images
        IF tbl = 'ai_analysis' OR tbl = 'disease_detections' THEN
            EXECUTE format('CREATE POLICY "Users can view own %I" ON public.%I FOR SELECT USING (EXISTS (SELECT 1 FROM public.images WHERE images.id = %I.image_id AND images.user_id = auth.uid()))', tbl, tbl, tbl);
            EXECUTE format('CREATE POLICY "Users can modify own %I" ON public.%I FOR ALL USING (EXISTS (SELECT 1 FROM public.images WHERE images.id = %I.image_id AND images.user_id = auth.uid()))', tbl, tbl, tbl);
        ELSE
            EXECUTE format('CREATE POLICY "Users can view own %I" ON public.%I FOR SELECT USING (auth.uid() = user_id)', tbl, tbl);
            EXECUTE format('CREATE POLICY "Users can modify own %I" ON public.%I FOR ALL USING (auth.uid() = user_id)', tbl, tbl);
        END IF;
    END LOOP;
END $$;
