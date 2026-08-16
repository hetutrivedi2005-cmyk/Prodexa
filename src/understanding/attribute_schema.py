from typing import Optional, Dict, Any, Union, Literal
from pydantic import BaseModel, Field, field_validator


class AttributeItem(BaseModel):
    """
    Pydantic schema for individual extracted attribute items.
    """
    value: Union[str, int, float, bool]
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: str
    method: Literal["rule", "llm", "hybrid", "none"]

    @field_validator("evidence")
    @classmethod
    def validate_evidence_not_empty(cls, v):
        if not v or not str(v).strip():
            raise ValueError("Evidence string cannot be empty!")
        return str(v).strip()


class ExtractedAttributesPayload(BaseModel):
    """
    Pydantic payload container for extracted product attributes.
    """
    attributes: Dict[str, AttributeItem] = Field(default_factory=dict)
