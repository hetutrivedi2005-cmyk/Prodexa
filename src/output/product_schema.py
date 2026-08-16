from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional


class ProductIdentityModel(BaseModel):
    product_id: str
    mpn: Optional[str] = None
    brand: Optional[str] = None
    manufacturer: Optional[str] = None
    product_type: Optional[str] = None


class ProductDescriptionsModel(BaseModel):
    title: Optional[str] = None
    short_description: Optional[str] = None
    long_description: Optional[str] = None


class ProductValidationModel(BaseModel):
    status: str
    confidence: float
    description_status: Optional[str] = None


class EvidenceReferenceModel(BaseModel):
    product_id: str
    attribute: str
    value: str
    source: Optional[str] = None
    source_id: Optional[str] = None
    evidence_id: Optional[str] = None
    evidence_text: Optional[str] = None
    verification_status: Optional[str] = None
    confidence: Optional[float] = None


class ProductFinalSchema(BaseModel):
    product: ProductIdentityModel
    attributes: Dict[str, Any] = Field(default_factory=dict)
    descriptions: ProductDescriptionsModel
    validation: ProductValidationModel
    evidence: List[EvidenceReferenceModel] = Field(default_factory=list)
