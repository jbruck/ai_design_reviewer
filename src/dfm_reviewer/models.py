from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, Field, field_validator


class ManufacturingRoute(StrEnum):
    MACHINED = "machined"
    FABRICATED_WELDED = "fabricated_welded"
    CAST_MOULDED_ENCAPSULATED = "cast_moulded_encapsulated"
    CABLE_ELECTROMECHANICAL = "cable_electromechanical"
    MANUAL_ASSEMBLY = "manual_assembly"


class ExProtectionConcept(StrEnum):
    EX_D = "Ex d"
    EX_M = "Ex m"
    EX_I = "Ex i"
    EX_E = "Ex e"
    SIMPLE_APPARATUS = "simple apparatus"
    NOT_APPLICABLE = "not applicable"


class CertificationStatus(StrEnum):
    EXISTING_CERTIFIED = "existing certified product"
    MAINTENANCE_OF_EXISTING = "maintenance of existing design"
    NEW_NOT_CERTIFIED = "new product not yet certified"
    NON_EX = "non-Ex"
    UNKNOWN = "unknown"


class Confidence(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class FindingStatus(StrEnum):
    CONFIRMED_ISSUE = "confirmed issue"
    LIKELY_ISSUE = "likely issue"
    NEEDS_HUMAN_REVIEW = "needs human review"
    MISSING_INFORMATION = "missing information"
    ADVISORY = "advisory suggestion"


class ReviewIntake(BaseModel):
    manufacturing_routes: list[ManufacturingRoute] = Field(default_factory=list)
    ex_concepts: list[ExProtectionConcept] = Field(default_factory=list)
    certification_status: CertificationStatus = CertificationStatus.UNKNOWN
    drawing_purpose: str = ""
    product_or_system: str = ""
    ecn: str = ""
    supplier_or_process: str = ""
    known_risks: str = ""
    supporting_documents: list[str] = Field(default_factory=list)


class TechnicalRequirement(BaseModel):
    requirement_id: str
    source_need_id: str | None = None
    text: str
    rationale: str = ""
    status: str = "draft"


class StakeholderNeed(BaseModel):
    need_id: str
    stakeholder: str
    text: str
    notes: str = ""


class EvidenceAnchor(BaseModel):
    evidence_id: str
    source_pdf: Path
    page_number: int = Field(ge=1)
    page_image_path: Path
    crop_image_path: Path
    region: list[int] = Field(min_length=4, max_length=4)
    extracted_text: str = ""
    linked_requirement_id: str | None = None
    linked_finding_id: str | None = None
    confidence: Confidence = Confidence.MEDIUM
    reviewer_note: str = ""

    @field_validator("region")
    @classmethod
    def validate_region_ordering(cls, region: list[int]) -> list[int]:
        left, top, right, bottom = region
        if left >= right:
            raise ValueError("region left coordinate must be less than right coordinate")
        if top >= bottom:
            raise ValueError("region top coordinate must be less than bottom coordinate")
        return region


class Finding(BaseModel):
    finding_id: str
    title: str
    status: FindingStatus
    confidence: Confidence
    details: str
    recommendation: str = ""
    linked_evidence_ids: list[str] = Field(default_factory=list)


class OpenQuestion(BaseModel):
    question_id: str
    text: str
    context: str = ""
    resolved: bool = False


class VerificationItem(BaseModel):
    verification_id: str
    text: str
    method: str = "inspection"
    linked_requirement_id: str | None = None


class Review(BaseModel):
    review_id: str
    part_number: str
    revision: str
    title: str
    source_pdf: Path
    intake: ReviewIntake
    requirements: list[TechnicalRequirement] = Field(default_factory=list)
    stakeholder_needs: list[StakeholderNeed] = Field(default_factory=list)
    evidence: list[EvidenceAnchor] = Field(default_factory=list)
    findings: list[Finding] = Field(default_factory=list)
    open_questions: list[OpenQuestion] = Field(default_factory=list)
    verification_items: list[VerificationItem] = Field(default_factory=list)
    extracted_title_block_text: str = ""
    extracted_notes_text: str = ""
