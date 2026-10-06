
-- Add image_path to inspections table
ALTER TABLE public.inspections ADD COLUMN IF NOT EXISTS image_path TEXT;

-- Create storage bucket if it doesn't exist
INSERT INTO storage.buckets (id, name, public) VALUES ('rice-images', 'rice-images', true) ON CONFLICT DO NOTHING;

-- Set up storage policies for public access (Anon)
CREATE POLICY "Cho phép đọc công khai ảnh" ON storage.objects FOR SELECT USING (bucket_id = 'rice-images');
CREATE POLICY "Cho phép tải ảnh lên" ON storage.objects FOR INSERT WITH CHECK (bucket_id = 'rice-images');
CREATE POLICY "Cho phép xóa ảnh" ON storage.objects FOR DELETE USING (bucket_id = 'rice-images');
