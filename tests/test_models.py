from pathlib import Path

from dfm_reviewer.models import (
    CertificationStatus,
    Confidence,
    EvidenceAnchor,
    Finding,
    FindingStatus,
    ManufacturingRoute,
    Review,
    ReviewIntake,
)


def test_review_defaults_to_empty_traceability_lists() -> None:
    review = Review(
        review_id="REV-001",
        part_number="PN-123",
        revision="A",
        title="Bracket",
        source_pdf=Path("source/drawing.pdf"),
        intake=ReviewIntake(
            manufacturing_routes=[ManufacturingRoute.MACHINED],
            certification_status=CertificationStatus.EXISTING_CERTIFIED,
        ),
    )

    assert review.requirements == []
    assert review.evidence == []
    assert review.findings == []
    assert review.open_questions == []


def test_evidence_anchor_keeps_auditable_source_region() -> None:
    anchor = EvidenceAnchor(
        evidence_id="EV-001",
        source_pdf=Path("source/drawing.pdf"),
        page_number=1,
        page_image_path=Path("pages/page-001.png"),
        crop_image_path=Path("evidence/EV-001.png"),
        region=[10, 20, 110, 220],
        extracted_text="MATERIAL: 316 SS",
        linked_requirement_id="REQ-001",
        confidence=Confidence.HIGH,
        reviewer_note="Material callout confirms corrosion-resistant material.",
    )

    assert anchor.region == [10, 20, 110, 220]
    assert anchor.linked_requirement_id == "REQ-001"
    assert anchor.linked_finding_id is None


def test_finding_status_records_uncertainty() -> None:
    finding = Finding(
        finding_id="F-001",
        title="Missing coating thickness",
        status=FindingStatus.NEEDS_HUMAN_REVIEW,
        confidence=Confidence.MEDIUM,
        details="Drawing calls up coating but does not show measurable acceptance criteria.",
    )

    assert finding.status is FindingStatus.NEEDS_HUMAN_REVIEW
    assert finding.confidence is Confidence.MEDIUM
