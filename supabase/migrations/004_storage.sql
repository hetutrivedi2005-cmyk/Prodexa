-- PRODEXA Supabase Production Migration 004: Storage Buckets & Policies
-- Defines storage buckets and access policies for prodexa-reports, prodexa-exports, prodexa-evidence, prodexa-uploads

-- Create Buckets
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES 
    ('prodexa-reports', 'prodexa-reports', true, 52428800, ARRAY['text/plain', 'application/json', 'text/csv']),
    ('prodexa-exports', 'prodexa-exports', true, 104857600, ARRAY['text/csv', 'application/json', 'application/x-jsonlines']),
    ('prodexa-evidence', 'prodexa-evidence', true, 52428800, ARRAY['application/pdf', 'image/jpeg', 'image/png', 'application/json']),
    ('prodexa-uploads', 'prodexa-uploads', false, 104857600, ARRAY['text/csv', 'application/json', 'application/x-jsonlines'])
ON CONFLICT (id) DO NOTHING;

-- Storage RLS Policies
CREATE POLICY "Public read prodexa-reports" ON storage.objects
    FOR SELECT USING (bucket_id = 'prodexa-reports');

CREATE POLICY "Public read prodexa-exports" ON storage.objects
    FOR SELECT USING (bucket_id = 'prodexa-exports');

CREATE POLICY "Public read prodexa-evidence" ON storage.objects
    FOR SELECT USING (bucket_id = 'prodexa-evidence');

CREATE POLICY "Authenticated upload files to prodexa-uploads" ON storage.objects
    FOR INSERT WITH CHECK (bucket_id = 'prodexa-uploads');

CREATE POLICY "Admins full storage management" ON storage.objects
    FOR ALL USING (bucket_id IN ('prodexa-reports', 'prodexa-exports', 'prodexa-evidence', 'prodexa-uploads'));
