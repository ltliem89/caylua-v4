-- ==========================================
-- CAY LÚA - SUPABASE DATABASE SCHEMA V3
-- ==========================================

-- 1. PROFILES
CREATE TABLE public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT,
    full_name TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Users can view own profile" ON public.profiles;
CREATE POLICY "Users can view own profile" ON public.profiles FOR SELECT USING (auth.uid() = id);
DROP POLICY IF EXISTS "Users can update own profile" ON public.profiles;
CREATE POLICY "Users can update own profile" ON public.profiles FOR UPDATE USING (auth.uid() = id);

-- 2. FIELDS (Ruộng)
CREATE TABLE public.fields (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    area_m2 FLOAT,
    sowing_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);
ALTER TABLE public.fields ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Users can view own fields" ON public.fields;
CREATE POLICY "Users can view own fields" ON public.fields FOR SELECT USING (auth.uid() = user_id);
DROP POLICY IF EXISTS "Users can insert own fields" ON public.fields;
CREATE POLICY "Users can insert own fields" ON public.fields FOR INSERT WITH CHECK (auth.uid() = user_id);
DROP POLICY IF EXISTS "Users can update own fields" ON public.fields;
CREATE POLICY "Users can update own fields" ON public.fields FOR UPDATE USING (auth.uid() = user_id);
DROP POLICY IF EXISTS "Users can delete own fields" ON public.fields;
CREATE POLICY "Users can delete own fields" ON public.fields FOR DELETE USING (auth.uid() = user_id);

-- 3. SURVEY SESSIONS
CREATE TABLE public.survey_sessions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    field_id UUID REFERENCES public.fields(id) ON DELETE CASCADE,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    ended_at TIMESTAMP WITH TIME ZONE,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'completed', 'cancelled'))
);
ALTER TABLE public.survey_sessions ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Users can view own sessions" ON public.survey_sessions;
CREATE POLICY "Users can view own sessions" ON public.survey_sessions FOR SELECT USING (auth.uid() = user_id);
DROP POLICY IF EXISTS "Users can insert own sessions" ON public.survey_sessions;
CREATE POLICY "Users can insert own sessions" ON public.survey_sessions FOR INSERT WITH CHECK (auth.uid() = user_id);
DROP POLICY IF EXISTS "Users can update own sessions" ON public.survey_sessions;
CREATE POLICY "Users can update own sessions" ON public.survey_sessions FOR UPDATE USING (auth.uid() = user_id);

-- 4. SURVEY POINTS
CREATE TABLE public.survey_points (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    survey_session_id UUID NOT NULL REFERENCES public.survey_sessions(id) ON DELETE CASCADE,
    field_id UUID REFERENCES public.fields(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    accuracy DOUBLE PRECISION,
    captured_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    status TEXT DEFAULT 'pending'
);
ALTER TABLE public.survey_points ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Users can view own points" ON public.survey_points;
CREATE POLICY "Users can view own points" ON public.survey_points FOR SELECT USING (auth.uid() = user_id);
DROP POLICY IF EXISTS "Users can insert own points" ON public.survey_points;
CREATE POLICY "Users can insert own points" ON public.survey_points FOR INSERT WITH CHECK (auth.uid() = user_id);
DROP POLICY IF EXISTS "Users can update own points" ON public.survey_points;
CREATE POLICY "Users can update own points" ON public.survey_points FOR UPDATE USING (auth.uid() = user_id);

-- 5. SURVEY IMAGES
CREATE TABLE public.survey_images (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    survey_session_id UUID NOT NULL REFERENCES public.survey_sessions(id) ON DELETE CASCADE,
    survey_point_id UUID NOT NULL REFERENCES public.survey_points(id) ON DELETE CASCADE,
    file_name TEXT NOT NULL,
    mime_type TEXT,
    size INTEGER,
    storage_path TEXT NOT NULL,
    sha256 TEXT,
    status TEXT DEFAULT 'local_pending' CHECK (status IN ('local_pending', 'uploading', 'uploaded', 'ai_pending', 'ai_processing', 'completed', 'upload_failed', 'ai_failed')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);
ALTER TABLE public.survey_images ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Users can view own images" ON public.survey_images;
CREATE POLICY "Users can view own images" ON public.survey_images FOR SELECT USING (auth.uid() = user_id);
DROP POLICY IF EXISTS "Users can insert own images" ON public.survey_images;
CREATE POLICY "Users can insert own images" ON public.survey_images FOR INSERT WITH CHECK (auth.uid() = user_id);
DROP POLICY IF EXISTS "Users can update own images" ON public.survey_images;
CREATE POLICY "Users can update own images" ON public.survey_images FOR UPDATE USING (auth.uid() = user_id);

-- 6. AI RESULTS
CREATE TABLE public.ai_results (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    survey_point_id UUID NOT NULL REFERENCES public.survey_points(id) ON DELETE CASCADE,
    survey_image_id UUID NOT NULL REFERENCES public.survey_images(id) ON DELETE CASCADE,
    job_id TEXT,
    status TEXT DEFAULT 'pending',
    class_id INTEGER,
    disease TEXT,
    confidence DOUBLE PRECISION,
    final_confidence DOUBLE PRECISION,
    environment_score DOUBLE PRECISION,
    bbox JSONB,
    preview_path TEXT,
    model_version TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);
ALTER TABLE public.ai_results ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Users can view own ai results" ON public.ai_results;
CREATE POLICY "Users can view own ai results" ON public.ai_results FOR SELECT USING (
    EXISTS (SELECT 1 FROM public.survey_images WHERE survey_images.id = ai_results.survey_image_id AND survey_images.user_id = auth.uid())
);
DROP POLICY IF EXISTS "Users can insert own ai results" ON public.ai_results;
CREATE POLICY "Users can insert own ai results" ON public.ai_results FOR INSERT WITH CHECK (
    EXISTS (SELECT 1 FROM public.survey_images WHERE survey_images.id = ai_results.survey_image_id AND survey_images.user_id = auth.uid())
);
DROP POLICY IF EXISTS "Users can update own ai results" ON public.ai_results;
CREATE POLICY "Users can update own ai results" ON public.ai_results FOR UPDATE USING (
    EXISTS (SELECT 1 FROM public.survey_images WHERE survey_images.id = ai_results.survey_image_id AND survey_images.user_id = auth.uid())
);

-- 7. ALERTS
CREATE TABLE public.alerts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    field_id UUID REFERENCES public.fields(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    type TEXT,
    is_read BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);
ALTER TABLE public.alerts ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Users can view own alerts" ON public.alerts;
CREATE POLICY "Users can view own alerts" ON public.alerts FOR SELECT USING (auth.uid() = user_id);

-- 8. GPS TRACKS
CREATE TABLE public.gps_tracks (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    survey_session_id UUID NOT NULL REFERENCES public.survey_sessions(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    accuracy DOUBLE PRECISION,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);
ALTER TABLE public.gps_tracks ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Users can view own tracks" ON public.gps_tracks;
CREATE POLICY "Users can view own tracks" ON public.gps_tracks FOR SELECT USING (auth.uid() = user_id);
DROP POLICY IF EXISTS "Users can insert own tracks" ON public.gps_tracks;
CREATE POLICY "Users can insert own tracks" ON public.gps_tracks FOR INSERT WITH CHECK (auth.uid() = user_id);

-- KEEP DISEASES from previous script
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
ALTER TABLE public.diseases ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Cho phép đọc công khai diseases" ON public.diseases;
CREATE POLICY "Cho phép đọc công khai diseases" ON public.diseases FOR SELECT USING (true);

-- 9. STORAGE BUCKET
INSERT INTO storage.buckets (id, name, public) VALUES ('survey-images', 'survey-images', false) ON CONFLICT DO NOTHING;

DROP POLICY IF EXISTS "Users can view own survey images" ON storage.objects;
CREATE POLICY "Users can view own survey images" ON storage.objects FOR SELECT USING (bucket_id = 'survey-images' AND auth.uid()::text = (string_to_array(name, '/'))[1]);

DROP POLICY IF EXISTS "Users can upload own survey images" ON storage.objects;
CREATE POLICY "Users can upload own survey images" ON storage.objects FOR INSERT WITH CHECK (bucket_id = 'survey-images' AND auth.uid()::text = (string_to_array(name, '/'))[1]);
