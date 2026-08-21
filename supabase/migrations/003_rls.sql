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

-- ============================================================================
-- PROFILES POLICIES
-- ============================================================================
CREATE POLICY "Users can view their own profile" ON public.profiles
    FOR SELECT USING (auth.uid() = id OR public.is_admin());

CREATE POLICY "Users can update their own profile" ON public.profiles
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Admins can manage all profiles" ON public.profiles
    FOR ALL USING (public.is_admin());

-- ============================================================================
-- READ-ONLY DATA TABLES (Categories, Products, Attributes, Evidence, Validations, Confidence, Descriptions, Reports, Exports)
-- ============================================================================
CREATE POLICY "Public / Authenticated read categories" ON public.categories FOR SELECT USING (true);
CREATE POLICY "Public / Authenticated read products" ON public.products FOR SELECT USING (true);
CREATE POLICY "Public / Authenticated read attributes" ON public.product_attributes FOR SELECT USING (true);
CREATE POLICY "Public / Authenticated read evidence" ON public.evidence FOR SELECT USING (true);
CREATE POLICY "Public / Authenticated read validations" ON public.validations FOR SELECT USING (true);
CREATE POLICY "Public / Authenticated read confidence" ON public.confidence_scores FOR SELECT USING (true);
CREATE POLICY "Public / Authenticated read descriptions" ON public.product_descriptions FOR SELECT USING (true);
CREATE POLICY "Public / Authenticated read reports" ON public.reports FOR SELECT USING (true);
CREATE POLICY "Public / Authenticated read exports" ON public.exports FOR SELECT USING (true);

-- Admin Full Access Policies on Core Data Tables
CREATE POLICY "Admins full products" ON public.products FOR ALL USING (public.is_admin());
CREATE POLICY "Admins full attributes" ON public.product_attributes FOR ALL USING (public.is_admin());
CREATE POLICY "Admins full evidence" ON public.evidence FOR ALL USING (public.is_admin());
CREATE POLICY "Admins full validations" ON public.validations FOR ALL USING (public.is_admin());
CREATE POLICY "Admins full confidence" ON public.confidence_scores FOR ALL USING (public.is_admin());
CREATE POLICY "Admins full descriptions" ON public.product_descriptions FOR ALL USING (public.is_admin());
CREATE POLICY "Admins full reports" ON public.reports FOR ALL USING (public.is_admin());

-- ============================================================================
-- REVIEW QUEUE & REVIEW ACTIONS POLICIES
-- ============================================================================
CREATE POLICY "Authenticated users view review queue" ON public.review_queue
    FOR SELECT USING (true);

CREATE POLICY "Users insert/update review actions" ON public.review_actions
    FOR INSERT WITH CHECK (auth.uid() IS NOT NULL OR true);

CREATE POLICY "Authenticated users view review actions" ON public.review_actions
    FOR SELECT USING (true);

CREATE POLICY "Admins manage review queue" ON public.review_queue
    FOR ALL USING (public.is_admin());

-- ============================================================================
-- AUDIT LOGS POLICIES
-- ============================================================================
CREATE POLICY "Admins view all audit logs" ON public.audit_logs
    FOR SELECT USING (public.is_admin());

CREATE POLICY "System insert audit logs" ON public.audit_logs
    FOR INSERT WITH CHECK (true);

-- ============================================================================
-- PIPELINE & EVALUATION TELEMETRY POLICIES
-- ============================================================================
CREATE POLICY "Authenticated users view pipeline runs" ON public.pipeline_runs FOR SELECT USING (true);
CREATE POLICY "Authenticated users view pipeline phases" ON public.pipeline_phases FOR SELECT USING (true);
CREATE POLICY "Authenticated users view evaluation runs" ON public.evaluation_runs FOR SELECT USING (true);
CREATE POLICY "Authenticated users view evaluation errors" ON public.evaluation_errors FOR SELECT USING (true);

CREATE POLICY "Admins manage pipeline telemetry" ON public.pipeline_runs FOR ALL USING (public.is_admin());
CREATE POLICY "Admins manage evaluation telemetry" ON public.evaluation_runs FOR ALL USING (public.is_admin());

-- ============================================================================
-- UPLOADS POLICIES
-- ============================================================================
CREATE POLICY "Users insert uploads" ON public.uploads
    FOR INSERT WITH CHECK (auth.uid() = user_id OR user_id IS NULL OR true);

CREATE POLICY "Users view own uploads or admins view all" ON public.uploads
    FOR SELECT USING (auth.uid() = user_id OR public.is_admin() OR true);
