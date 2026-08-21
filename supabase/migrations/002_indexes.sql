-- PRODEXA Supabase Production Migration 002: Indexes
-- Creates performance B-tree indexes for fast queries and joins

-- Products lookup indexes
CREATE INDEX IF NOT EXISTS idx_products_mpn ON public.products(mpn);
CREATE INDEX IF NOT EXISTS idx_products_brand ON public.products(brand);
CREATE INDEX IF NOT EXISTS idx_products_manufacturer ON public.products(manufacturer);
CREATE INDEX IF NOT EXISTS idx_products_type ON public.products(product_type);
CREATE INDEX IF NOT EXISTS idx_products_category ON public.products(category_id);
CREATE INDEX IF NOT EXISTS idx_products_val_status ON public.products(validation_status);
CREATE INDEX IF NOT EXISTS idx_products_rev_status ON public.products(review_status);
CREATE INDEX IF NOT EXISTS idx_products_confidence ON public.products(confidence_score DESC);
CREATE INDEX IF NOT EXISTS idx_products_source_id ON public.products(source_product_id);

-- Product attributes lookup indexes
CREATE INDEX IF NOT EXISTS idx_attributes_product_id ON public.product_attributes(product_id);
CREATE INDEX IF NOT EXISTS idx_attributes_name ON public.product_attributes(attribute_name);
CREATE INDEX IF NOT EXISTS idx_attributes_product_name ON public.product_attributes(product_id, attribute_name);

-- Evidence lookup indexes
CREATE INDEX IF NOT EXISTS idx_evidence_product_id ON public.evidence(product_id);
CREATE INDEX IF NOT EXISTS idx_evidence_attribute_id ON public.evidence(attribute_id);
CREATE INDEX IF NOT EXISTS idx_evidence_source_type ON public.evidence(source_type);

-- Validation lookup indexes
CREATE INDEX IF NOT EXISTS idx_validations_product_id ON public.validations(product_id);
CREATE INDEX IF NOT EXISTS idx_validations_type ON public.validations(validation_type);
CREATE INDEX IF NOT EXISTS idx_validations_status ON public.validations(status);

-- Review queue indexes
CREATE INDEX IF NOT EXISTS idx_review_status ON public.review_queue(status);
CREATE INDEX IF NOT EXISTS idx_review_priority ON public.review_queue(priority);
CREATE INDEX IF NOT EXISTS idx_review_assigned ON public.review_queue(assigned_to);
CREATE INDEX IF NOT EXISTS idx_review_product_id ON public.review_queue(product_id);

-- Audit log indexes
CREATE INDEX IF NOT EXISTS idx_audit_logs_user ON public.audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_entity ON public.audit_logs(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created ON public.audit_logs(created_at DESC);

-- Pipeline phases indexes
CREATE INDEX IF NOT EXISTS idx_pipeline_phases_run ON public.pipeline_phases(pipeline_run_id);
CREATE INDEX IF NOT EXISTS idx_pipeline_phases_num ON public.pipeline_phases(phase_number);

-- Evaluation errors indexes
CREATE INDEX IF NOT EXISTS idx_eval_errors_run ON public.evaluation_errors(evaluation_run_id);
CREATE INDEX IF NOT EXISTS idx_eval_errors_field ON public.evaluation_errors(field_name);
