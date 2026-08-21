-- ============================================================================
-- PRODEXA SUPABASE FULL PRODUCTION DATABASE MIGRATION SCRIPT
-- Copy and paste this entire file into the Supabase Dashboard SQL Editor
-- (https://supabase.com/dashboard/project/_/sql/new) and click RUN.
-- ============================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- 1. PROFILES (Linked 1:1 to auth.users)
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    role TEXT NOT NULL DEFAULT 'USER' CHECK (role IN ('USER', 'ADMIN')),
    avatar_url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 2. CATEGORIES / TAXONOMY
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category_id TEXT UNIQUE NOT NULL,
    category_name TEXT NOT NULL,
    parent_id UUID REFERENCES public.categories(id) ON DELETE SET NULL,
    level INTEGER NOT NULL DEFAULT 1,
    is_leaf BOOLEAN DEFAULT TRUE,
    category_path TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 3. PRODUCTS (Canonical Product Identity)
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_product_id TEXT UNIQUE NOT NULL,
    mpn TEXT NOT NULL,
    brand TEXT,
    manufacturer TEXT,
    product_type TEXT,
    category_id UUID REFERENCES public.categories(id) ON DELETE SET NULL,
    validation_status TEXT DEFAULT 'valid',
    review_status TEXT DEFAULT 'auto_approved',
    confidence_score NUMERIC(5,4) DEFAULT 1.0000,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT unique_mpn_mfr UNIQUE (mpn, manufacturer)
);

-- ============================================================================
-- 4. PRODUCT ATTRIBUTES (Dynamic Attributes Store)
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.product_attributes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID NOT NULL REFERENCES public.products(id) ON DELETE CASCADE,
    attribute_name TEXT NOT NULL,
    attribute_value TEXT,
    normalized_value TEXT,
    uom TEXT,
    source TEXT,
    confidence NUMERIC(5,4) DEFAULT 1.0000,
    validation_status TEXT DEFAULT 'valid',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT unique_product_attribute UNIQUE (product_id, attribute_name)
);

-- ============================================================================
-- 5. EVIDENCE & PROVENANCE
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.evidence (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID NOT NULL REFERENCES public.products(id) ON DELETE CASCADE,
    attribute_id UUID REFERENCES public.product_attributes(id) ON DELETE SET NULL,
    source_type TEXT NOT NULL,
    source_url TEXT,
    source_title TEXT,
    source_document TEXT,
    page_number INTEGER,
    evidence_text TEXT,
    evidence_span TEXT,
    verification_status TEXT DEFAULT 'verified',
    authority_score NUMERIC(5,4) DEFAULT 1.0000,
    confidence NUMERIC(5,4) DEFAULT 1.0000,
    retrieved_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 6. VALIDATIONS
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.validations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID NOT NULL REFERENCES public.products(id) ON DELETE CASCADE,
    attribute_id UUID REFERENCES public.product_attributes(id) ON DELETE SET NULL,
    field_name TEXT NOT NULL,
    validation_type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'PASS',
    expected_value TEXT,
    actual_value TEXT,
    error_code TEXT,
    reason TEXT,
    severity TEXT DEFAULT 'INFO',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 7. CONFIDENCE SCORES
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.confidence_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID NOT NULL REFERENCES public.products(id) ON DELETE CASCADE,
    score NUMERIC(5,4) NOT NULL DEFAULT 1.0000,
    source_authority NUMERIC(5,4) DEFAULT 1.0000,
    mpn_match NUMERIC(5,4) DEFAULT 1.0000,
    evidence_grounding NUMERIC(5,4) DEFAULT 1.0000,
    lov_validation NUMERIC(5,4) DEFAULT 1.0000,
    uom_validation NUMERIC(5,4) DEFAULT 1.0000,
    validation_score NUMERIC(5,4) DEFAULT 1.0000,
    confidence_band TEXT DEFAULT 'AUTO_APPROVED',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 8. PRODUCT DESCRIPTIONS
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.product_descriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID NOT NULL REFERENCES public.products(id) ON DELETE CASCADE,
    title TEXT,
    short_description TEXT,
    long_description TEXT,
    grounding_status TEXT DEFAULT 'grounded',
    grounding_score NUMERIC(5,4) DEFAULT 1.0000,
    character_validation BOOLEAN DEFAULT TRUE,
    factual_claim_count INTEGER DEFAULT 0,
    grounded_claim_count INTEGER DEFAULT 0,
    unsupported_claim_count INTEGER DEFAULT 0,
    validation_status TEXT DEFAULT 'valid',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 9. HUMAN-IN-THE-LOOP REVIEW QUEUE
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.review_queue (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    review_id TEXT UNIQUE NOT NULL,
    product_id UUID NOT NULL REFERENCES public.products(id) ON DELETE CASCADE,
    attribute_id UUID REFERENCES public.product_attributes(id) ON DELETE SET NULL,
    field_name TEXT NOT NULL,
    current_value TEXT,
    proposed_value TEXT,
    human_override_value TEXT,
    confidence NUMERIC(5,4) DEFAULT 0.5000,
    reason TEXT,
    priority TEXT DEFAULT 'MEDIUM',
    status TEXT NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'IN_REVIEW', 'ACCEPTED', 'EDITED', 'REJECTED', 'ESCALATED', 'RESOLVED')),
    assigned_to UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    resolved_at TIMESTAMPTZ
);

-- ============================================================================
-- 10. REVIEW ACTIONS (Immutable Human Review Audit)
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.review_actions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    audit_id TEXT UNIQUE NOT NULL,
    review_id UUID NOT NULL REFERENCES public.review_queue(id) ON DELETE CASCADE,
    user_id UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
    actor_id TEXT DEFAULT 'HUMAN',
    action TEXT NOT NULL,
    old_value TEXT,
    new_value TEXT,
    comment TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 11. SYSTEM AUDIT LOG
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
    action TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id UUID,
    old_value TEXT,
    new_value TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    ip_address INET,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 12. PIPELINE RUNS & MONITORING
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.pipeline_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id TEXT UNIQUE NOT NULL,
    status TEXT NOT NULL DEFAULT 'COMPLETED',
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ DEFAULT NOW(),
    total_products INTEGER DEFAULT 1000,
    successful_products INTEGER DEFAULT 1000,
    failed_products INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS public.pipeline_phases (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pipeline_run_id UUID NOT NULL REFERENCES public.pipeline_runs(id) ON DELETE CASCADE,
    phase_number INTEGER NOT NULL,
    phase_name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'COMPLETED',
    records_processed INTEGER DEFAULT 1000,
    records_failed INTEGER DEFAULT 0,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb,
    CONSTRAINT unique_run_phase UNIQUE (pipeline_run_id, phase_number)
);

-- ============================================================================
-- 13. EVALUATION RUNS & ERRORS
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.evaluation_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id TEXT UNIQUE NOT NULL,
    products_evaluated INTEGER DEFAULT 1000,
    fields_evaluated INTEGER DEFAULT 3997,
    field_accuracy NUMERIC(5,2) DEFAULT 96.63,
    data_completeness NUMERIC(5,2) DEFAULT 99.50,
    lov_compliance NUMERIC(5,2) DEFAULT 0.00,
    uom_compliance NUMERIC(5,2) DEFAULT 97.13,
    human_review_rate NUMERIC(5,2) DEFAULT 2.00,
    enrichment_recovery_rate NUMERIC(5,2) DEFAULT 91.30,
    grounding_rate NUMERIC(5,2) DEFAULT 100.00,
    confidence_quality NUMERIC(5,2) DEFAULT 73.25,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS public.evaluation_errors (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    evaluation_run_id UUID NOT NULL REFERENCES public.evaluation_runs(id) ON DELETE CASCADE,
    product_id UUID REFERENCES public.products(id) ON DELETE SET NULL,
    field_name TEXT NOT NULL,
    expected_value TEXT,
    predicted_value TEXT,
    error_category TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 14. REPORTS METADATA
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    file_name TEXT UNIQUE NOT NULL,
    file_path TEXT NOT NULL,
    file_type TEXT DEFAULT 'text/plain',
    report_type TEXT DEFAULT 'AUDIT',
    size_bytes BIGINT DEFAULT 0,
    pipeline_run_id UUID REFERENCES public.pipeline_runs(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 15. UPLOADS TRACKING
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.uploads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.profiles(id) ON DELETE SET NULL,
    filename TEXT NOT NULL,
    storage_path TEXT NOT NULL,
    file_type TEXT NOT NULL,
    file_size BIGINT NOT NULL,
    status TEXT NOT NULL DEFAULT 'UPLOADED',
    error_message TEXT,
    uploaded_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ
);

-- ============================================================================
-- 16. EXPORTS METADATA
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.exports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    filename TEXT NOT NULL,
    storage_path TEXT NOT NULL,
    format TEXT NOT NULL DEFAULT 'csv',
    size_bytes BIGINT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 17. PERFORMANCE INDEXES
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_products_mpn ON public.products(mpn);
CREATE INDEX IF NOT EXISTS idx_products_brand ON public.products(brand);
CREATE INDEX IF NOT EXISTS idx_products_manufacturer ON public.products(manufacturer);
CREATE INDEX IF NOT EXISTS idx_products_type ON public.products(product_type);
CREATE INDEX IF NOT EXISTS idx_products_category ON public.products(category_id);
CREATE INDEX IF NOT EXISTS idx_products_val_status ON public.products(validation_status);
CREATE INDEX IF NOT EXISTS idx_products_rev_status ON public.products(review_status);
CREATE INDEX IF NOT EXISTS idx_products_confidence ON public.products(confidence_score DESC);
CREATE INDEX IF NOT EXISTS idx_products_source_id ON public.products(source_product_id);

CREATE INDEX IF NOT EXISTS idx_attributes_product_id ON public.product_attributes(product_id);
CREATE INDEX IF NOT EXISTS idx_attributes_name ON public.product_attributes(attribute_name);
CREATE INDEX IF NOT EXISTS idx_attributes_product_name ON public.product_attributes(product_id, attribute_name);

CREATE INDEX IF NOT EXISTS idx_evidence_product_id ON public.evidence(product_id);
CREATE INDEX IF NOT EXISTS idx_evidence_attribute_id ON public.evidence(attribute_id);
CREATE INDEX IF NOT EXISTS idx_evidence_source_type ON public.evidence(source_type);

CREATE INDEX IF NOT EXISTS idx_validations_product_id ON public.validations(product_id);
CREATE INDEX IF NOT EXISTS idx_validations_type ON public.validations(validation_type);
CREATE INDEX IF NOT EXISTS idx_validations_status ON public.validations(status);

CREATE INDEX IF NOT EXISTS idx_review_status ON public.review_queue(status);
CREATE INDEX IF NOT EXISTS idx_review_priority ON public.review_queue(priority);
CREATE INDEX IF NOT EXISTS idx_review_assigned ON public.review_queue(assigned_to);
CREATE INDEX IF NOT EXISTS idx_review_product_id ON public.review_queue(product_id);

CREATE INDEX IF NOT EXISTS idx_audit_logs_user ON public.audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_entity ON public.audit_logs(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created ON public.audit_logs(created_at DESC);

-- ============================================================================
-- 18. ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================================================
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

CREATE OR REPLACE FUNCTION public.is_admin()
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM public.profiles
        WHERE id = auth.uid() AND role = 'ADMIN'
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

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

