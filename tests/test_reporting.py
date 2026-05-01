from pathlib import Path

from dfm_reviewer.models import (
    CertificationStatus,
    Confidence,
    EvidenceAnchor,
    ExProtectionConcept,
    Finding,
    FindingStatus,
    ManufacturingRoute,
    OpenQuestion,
    Review,
    ReviewIntake,
    StakeholderNeed,
    TechnicalRequirement,
    VerificationItem,
)
from dfm_reviewer.reporting import render_markdown_report, write_markdown_report


def make_review() -> Review:
    return Review(
        review_id="PN-123_REV-A",
        part_number="PN-123",
        revision="A",
        title="Mounting Bracket",
        source_pdf=Path("source/drawing.pdf"),
        intake=ReviewIntake(
            manufacturing_routes=[ManufacturingRoute.MACHINED],
            ex_concepts=[ExProtectionConcept.EX_D],
            certification_status=CertificationStatus.EXISTING_CERTIFIED,
            drawing_purpose="Release for manufacture",
            product_or_system="Gas detector",
            ecn="ECN-456",
            supplier_or_process="Internal machine shop",
            known_risks="Flamepath dimensions need checking.",
            supporting_documents=["certificate schedule"],
        ),
        stakeholder_needs=[
            StakeholderNeed(
                need_id="NEED-001",
                stakeholder="Manufacturing",
                text="Part can be machined and inspected repeatably.",
            )
        ],
        requirements=[
            TechnicalRequirement(
                requirement_id="REQ-001",
                source_need_id="NEED-001",
                text="Material grade is explicit.",
                rationale="Material drives corrosion resistance.",
            )
        ],
        evidence=[
            EvidenceAnchor(
                evidence_id="EV-001",
                source_pdf=Path("source/drawing.pdf"),
                page_number=1,
                page_image_path=Path("pages/page-001.png"),
                crop_image_path=Path("evidence/EV-001.png"),
                region=[1, 2, 30, 40],
                extracted_text="MATERIAL: 316 SS",
                linked_requirement_id="REQ-001",
                confidence=Confidence.HIGH,
                reviewer_note="Material evidence.",
            )
        ],
        findings=[
            Finding(
                finding_id="F-001",
                title="Missing tolerance",
                status=FindingStatus.MISSING_INFORMATION,
                confidence=Confidence.MEDIUM,
                details="Critical bore tolerance is not visible.",
                recommendation="Confirm the bore tolerance before release.",
                linked_evidence_ids=["EV-001"],
            )
        ],
        open_questions=[
            OpenQuestion(
                question_id="Q-001",
                text="Is the certification drawing available?",
                context="Existing certified product.",
            )
        ],
        verification_items=[
            VerificationItem(
                verification_id="V-001",
                text="Inspect bore diameter against final tolerance.",
                linked_requirement_id="REQ-001",
            )
        ],
        extracted_title_block_text="TITLE: Mounting Bracket",
        extracted_notes_text="NOTE 1: REMOVE ALL BURRS",
    )


def test_render_markdown_report_contains_mvp_sections_and_traceability() -> None:
    markdown = render_markdown_report(make_review())

    assert "# Mechanical DFM Review: PN-123 Rev A" in markdown
    assert "## Review Summary" in markdown
    assert "## Drawing Metadata" in markdown
    assert "## Intake And Context" in markdown
    assert "## Manufacturing Route" in markdown
    assert "## IECEx Context And Evidence Status" in markdown
    assert "## Stakeholder Needs" in markdown
    assert "## Technical Requirements" in markdown
    assert "## Design Evidence" in markdown
    assert "## DFM Findings" in markdown
    assert "## Open Questions And Missing Information" in markdown
    assert "## Suggested Inspection Or Verification Items" in markdown
    assert "## Appendix: Extracted Text" in markdown
    assert "source/drawing.pdf" in markdown
    assert "pages/page-001.png" in markdown
    assert "evidence/EV-001.png" in markdown
    assert "1, 2, 30, 40" in markdown
    assert "REQ-001" in markdown
    assert "Missing tolerance" in markdown
    assert "TITLE: Mounting Bracket" in markdown
    assert "NOTE 1: REMOVE ALL BURRS" in markdown
    assert "### OCR Status" in markdown
    assert "No separate OCR pass has been run for this MVP report." in markdown
    assert "### OCR Text" in markdown
    assert "OCR text is not captured separately in this MVP report." in markdown
    assert "not a certification determination" in markdown


def test_write_markdown_report_creates_file(tmp_path: Path) -> None:
    output = write_markdown_report(make_review(), tmp_path)

    assert output.name == "mechanical-dfm-review.md"
    assert output.exists()
    assert "Mounting Bracket" in output.read_text(encoding="utf-8")


def test_render_markdown_report_escapes_table_cell_content() -> None:
    review = make_review()
    review.evidence[0].reviewer_note = "Check A | B\nSecond line"

    markdown = render_markdown_report(review)

    assert "Check A \\| B<br>Second line" in markdown


def test_render_markdown_report_uses_longer_code_fence_for_backticks() -> None:
    review = make_review()
    review.extracted_notes_text = "A note with ``` inside"

    markdown = render_markdown_report(review)

    assert "````\nA note with ``` inside\n````" in markdown
