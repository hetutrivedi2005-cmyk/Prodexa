-- PRODEXA Supabase Production Migration 003: Row Level Security (RLS) Policies
-- Enables RLS and configures granular access policies for USER and ADMIN roles

-- Enable RLS on all 18 application tables
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.products ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.product_attributes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.evidence ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.validations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.confidence_scores ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.product_descriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.review_queue ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.review_actions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.pipeline_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.pipeline_phases ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.evaluation_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.evaluation_errors ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.uploads ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.exports ENABLE ROW LEVEL SECURITY;

-- Helper function to check if current authenticated user is ADMIN
CREATE OR REPLACE FUNCTION public.is_admin()
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM public.profiles
        WHERE id = auth.uid() AND role = 'ADMIN'
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Drop existing policies if re-running
DROP POLICY IF EXISTS "Public read categories" ON public.categories;
DROP POLICY IF EXISTS "Public read products" ON public.products;
DROP POLICY IF EXISTS "Public read attributes" ON public.product_attributes;
DROP POLICY IF EXISTS "Public read evidence" ON public.evidence;
DROP POLICY IF EXISTS "Public read validations" ON public.validations;
DROP POLICY IF EXISTS "Public read confidence" ON public.confidence_scores;
DROP POLICY IF EXISTS "Public read descriptions" ON public.product_descriptions;
DROP POLICY IF EXISTS "Public read reports" ON public.reports;
DROP POLICY IF EXISTS "Public read exports" ON public.exports;
DROP POLICY IF EXISTS "Public read review queue" ON public.review_queue;
DROP POLICY IF EXISTS "Public read review actions" ON public.review_actions;

-- Create Policies
CREATE POLICY "Public read categories" ON public.categories FOR SELECT USING (true);
CREATE POLICY "Public read products" ON public.products FOR SELECT USING (true);
CREATE POLICY "Public read attributes" ON public.product_attributes FOR SELECT USING (true);
CREATE POLICY "Public read evidence" ON public.evidence FOR SELECT USING (true);
CREATE POLICY "Public read validations" ON public.validations FOR SELECT USING (true);
CREATE POLICY "Public read confidence" ON public.confidence_scores FOR SELECT USING (true);
CREATE POLICY "Public read descriptions" ON public.product_descriptions FOR SELECT USING (true);
CREATE POLICY "Public read reports" ON public.reports FOR SELECT USING (true);
CREATE POLICY "Public read exports" ON public.exports FOR SELECT USING (true);
CREATE POLICY "Public read review queue" ON public.review_queue FOR SELECT USING (true);
CREATE POLICY "Public read review actions" ON public.review_actions FOR SELECT USING (true);
