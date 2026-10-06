
-- 9. STORAGE BUCKET
INSERT INTO storage.buckets (id, name, public) VALUES ('survey-images', 'survey-images', false) ON CONFLICT DO NOTHING;

DROP POLICY IF EXISTS "Users can view own survey images" ON storage.objects;
CREATE POLICY "Users can view own survey images" ON storage.objects FOR SELECT USING (bucket_id = 'survey-images' AND auth.uid()::text = (string_to_array(name, '/'))[1]);

DROP POLICY IF EXISTS "Users can upload own survey images" ON storage.objects;
CREATE POLICY "Users can upload own survey images" ON storage.objects FOR INSERT WITH CHECK (bucket_id = 'survey-images' AND auth.uid()::text = (string_to_array(name, '/'))[1]);
