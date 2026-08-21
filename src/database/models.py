from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
import datetime

class UserProfile(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = None
    role: str = "USER"
    avatar_url: Optional[str] = None
    is_active: bool = True
    created_at: Optional[str] = None

class CategoryModel(BaseModel):
    id: Optional[str] = None
    category_id: str
    category_name: str
    parent_id: Optional[str] = None
    level: int = 1
    is_leaf: bool = True
    category_path: Optional[str] = None

class ProductModel(BaseModel):
    id: Optional[str] = None
    source_product_id: str
    mpn: str
    brand: Optional[str] = None
    manufacturer: Optional[str] = None
    product_type: Optional[str] = None
    category_id: Optional[str] = None
    validation_status: str = "valid"
    review_status: str = "auto_approved"
    confidence_score: float = 1.0

class ProductAttributeModel(BaseModel):
    id: Optional[str] = None
    product_id: str
    attribute_name: str
    attribute_value: Optional[str] = None
    normalized_value: Optional[str] = None
    uom: Optional[str] = None
    source: Optional[str] = None
    confidence: float = 1.0
    validation_status: str = "valid"

class EvidenceModel(BaseModel):
    id: Optional[str] = None
    product_id: str
    attribute_id: Optional[str] = None
    source_type: str
    source_url: Optional[str] = None
    source_title: Optional[str] = None
    source_document: Optional[str] = None
    page_number: Optional[int] = 1
    evidence_text: Optional[str] = None
    authority_score: float = 1.0
    confidence: float = 1.0

class ValidationModel(BaseModel):
    id: Optional[str] = None
    product_id: str
    attribute_id: Optional[str] = None
    field_name: str
    validation_type: str
    status: str = "PASS"
    expected_value: Optional[str] = None
    actual_value: Optional[str] = None
    reason: Optional[str] = None
    severity: str = "INFO"

class ConfidenceModel(BaseModel):
    id: Optional[str] = None
    product_id: str
    score: float = 1.0
    source_authority: float = 1.0
    mpn_match: float = 1.0
    evidence_grounding: float = 1.0
    lov_validation: float = 1.0
    uom_validation: float = 1.0
    confidence_band: str = "AUTO_APPROVED"

class DescriptionModel(BaseModel):
    id: Optional[str] = None
    product_id: str
    title: Optional[str] = None
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    grounding_status: str = "grounded"
    grounding_score: float = 1.0

class ReviewQueueModel(BaseModel):
    id: Optional[str] = None
    review_id: str
    product_id: str
    attribute_id: Optional[str] = None
    field_name: str
    current_value: Optional[str] = None
    proposed_value: Optional[str] = None
    human_override_value: Optional[str] = None
    confidence: float = 0.5
    reason: Optional[str] = None
    priority: str = "MEDIUM"
    status: str = "PENDING"

class ReviewActionModel(BaseModel):
    id: Optional[str] = None
    audit_id: str
    review_id: str
    user_id: Optional[str] = None
    actor_id: str = "HUMAN"
    action: str
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    comment: Optional[str] = None

class AuditLogModel(BaseModel):
    id: Optional[str] = None
    user_id: Optional[str] = None
    action: str
    entity_type: str
    entity_id: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    metadata: Dict[str, Any] = {}

class PipelineRunModel(BaseModel):
    id: Optional[str] = None
    run_id: str
    status: str = "COMPLETED"
    total_products: int = 1000
    successful_products: int = 1000
    failed_products: int = 0

class PipelinePhaseModel(BaseModel):
    id: Optional[str] = None
    pipeline_run_id: str
    phase_number: int
    phase_name: str
    status: str = "COMPLETED"
    records_processed: int = 1000

class EvaluationRunModel(BaseModel):
    id: Optional[str] = None
    run_id: str
    products_evaluated: int = 1000
    fields_evaluated: int = 3997
    field_accuracy: float = 96.63
    data_completeness: float = 99.50
    lov_compliance: float = 0.00
    uom_compliance: float = 97.13
    human_review_rate: float = 2.00

class ReportModel(BaseModel):
    id: Optional[str] = None
    name: str
    file_name: str
    file_path: str
    file_type: str = "text/plain"
    report_type: str = "AUDIT"
    size_bytes: int = 0
