# Mechanical DFM Reviewer MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Build the first working local mechanical DFM review workbench: guided intake, review package storage, PDF rendering/cropping, Markdown report generation, CLI fallback, and a minimal NiceGUI interface.

**Architecture:** Use a Python package with focused services shared by the CLI and web app. Store each review as a transparent local folder with `review.yaml`, copied source PDF, rendered pages, evidence crops, extracted text, and generated Markdown. Keep OpenAI behind an adapter boundary so the initial provider is explicit but replaceable.

**Tech Stack:** Python 3.11+, Pydantic, PyYAML, Typer, Rich, PyMuPDF, Pillow, NiceGUI, pytest, ruff.

---

## File Structure

- Create: `pyproject.toml` - package metadata, runtime dependencies, dev dependencies, CLI entry point.
- Create: `README.md` - local setup and first-run workflow.
- Create: `.gitignore` - Python cache, virtual environments, generated review artefacts.
- Create: `src/dfm_reviewer/__init__.py` - package marker and version.
- Create: `src/dfm_reviewer/models.py` - Pydantic review, intake, evidence, finding, and enum models.
- Create: `src/dfm_reviewer/storage.py` - review folder creation, source PDF copy, YAML load/save, path helpers.
- Create: `src/dfm_reviewer/pdf_processing.py` - PDF page rendering, embedded text extraction, image crop generation.
- Create: `src/dfm_reviewer/reporting.py` - Markdown report generation from the review model.
- Create: `src/dfm_reviewer/review_packs.py` - load editable YAML review packs.
- Create: `src/dfm_reviewer/ai.py` - provider protocol, OpenAI adapter skeleton, disabled fallback provider.
- Create: `src/dfm_reviewer/cli.py` - Typer CLI commands.
- Create: `src/dfm_reviewer/web.py` - NiceGUI local web app.
- Create: `src/dfm_reviewer/watcher.py` - folder scan/inbox scaffolding.
- Create: `review_packs/manufacturing/*.yaml` - starter manufacturing route packs.
- Create: `review_packs/iecex/*.yaml` - starter IECEx advisory packs.
- Create: `tests/fixtures/minimal.pdf` - generated test fixture PDF.
- Create: `tests/test_models.py` - model behavior tests.
- Create: `tests/test_storage.py` - review package tests.
- Create: `tests/test_pdf_processing.py` - render/text/crop tests.
- Create: `tests/test_reporting.py` - Markdown report tests.
- Create: `tests/test_review_packs.py` - checklist pack tests.
- Create: `tests/test_cli.py` - CLI smoke tests.

---

## Task 1: Project Skeleton

**Files:**
- Create: `pyproject.toml`
- Create: `.gitignore`
- Create: `README.md`
- Create: `src/dfm_reviewer/__init__.py`

- [x] **Step 1: Create packaging and tool configuration**

Create `pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=69", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "mechanical-dfm-reviewer"
version = "0.1.0"
description = "Local mechanical DFM review workbench for drawing PDFs"
requires-python = ">=3.11"
dependencies = [
  "nicegui>=1.4.35",
  "openai>=1.30.0",
  "pillow>=10.0.0",
  "pydantic>=2.7.0",
  "pymupdf>=1.24.0",
  "pyyaml>=6.0.1",
  "rich>=13.7.0",
  "typer>=0.12.0",
]

[project.optional-dependencies]
dev = [
  "pytest>=8.2.0",
  "pytest-cov>=5.0.0",
  "reportlab>=4.2.0",
  "ruff>=0.4.0",
]

[project.scripts]
dfm-reviewer = "dfm_reviewer.cli:app"

[tool.setuptools.packages.find]
where = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]
```

Create `.gitignore`:

```gitignore
.venv/
__pycache__/
*.py[cod]
.pytest_cache/
.ruff_cache/
reviews/
dist/
build/
*.egg-info/
```

Create `README.md`:

```markdown
# Mechanical DFM Reviewer

Local Python-first workbench for mechanical DFM review of drawing PDFs.

## MVP Workflow

1. Create a review from a drawing PDF.
2. Complete the mechanical intake.
3. Render drawing pages.
4. Capture evidence crops.
5. Generate a Markdown review report.

## Development

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .[dev]
pytest
```

## Run

```powershell
dfm-reviewer --help
python -m dfm_reviewer.web
```
```

Create `src/dfm_reviewer/__init__.py`:

```python
"""Mechanical DFM reviewer package."""

__version__ = "0.1.0"
```

- [x] **Step 2: Install dependencies**

Run: `python -m pip install -e .[dev]`

Expected: editable package installs successfully.

- [x] **Step 3: Run initial verification**

Run: `pytest`

Expected: pytest reports no tests collected or passes once later tests exist.

- [x] **Step 4: Commit**

Run:

```powershell
git add pyproject.toml .gitignore README.md src/dfm_reviewer/__init__.py
git commit -m "chore: scaffold Python project"
```

---

## Task 2: Core Review Models

**Files:**
- Create: `src/dfm_reviewer/models.py`
- Create: `tests/test_models.py`

- [x] **Step 1: Write failing model tests**

Create `tests/test_models.py`:

```python
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
```

- [x] **Step 2: Run model tests to verify failure**

Run: `pytest tests/test_models.py -v`

Expected: FAIL with `ModuleNotFoundError` or missing model names.

- [x] **Step 3: Implement minimal models**

Create `src/dfm_reviewer/models.py`:

```python
from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, Field


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
    page_number: int
    page_image_path: Path
    crop_image_path: Path
    region: list[int]
    extracted_text: str = ""
    linked_requirement_id: str | None = None
    linked_finding_id: str | None = None
    confidence: Confidence = Confidence.MEDIUM
    reviewer_note: str = ""


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
```

- [x] **Step 4: Run model tests to verify pass**

Run: `pytest tests/test_models.py -v`

Expected: PASS.

- [x] **Step 5: Commit**

Run:

```powershell
git add src/dfm_reviewer/models.py tests/test_models.py
git commit -m "feat: add review data models"
```

---

## Task 3: Review Package Storage

**Files:**
- Create: `src/dfm_reviewer/storage.py`
- Create: `tests/test_storage.py`

- [x] **Step 1: Write failing storage tests**

Create `tests/test_storage.py`:

```python
from pathlib import Path

from dfm_reviewer.models import CertificationStatus, ManufacturingRoute, Review, ReviewIntake
from dfm_reviewer.storage import ReviewPackage, create_review_package, load_review, save_review


def test_create_review_package_copies_pdf_and_creates_folders(tmp_path: Path) -> None:
    source_pdf = tmp_path / "drawing.pdf"
    source_pdf.write_bytes(b"%PDF-1.4\n%test\n")

    package = create_review_package(
        reviews_root=tmp_path / "reviews",
        source_pdf=source_pdf,
        part_number="PN 123/4",
        revision="A",
    )

    assert isinstance(package, ReviewPackage)
    assert package.root.exists()
    assert package.source_pdf.exists()
    assert package.pages_dir.exists()
    assert package.evidence_dir.exists()
    assert package.extracted_dir.exists()
    assert package.reports_dir.exists()
    assert package.source_pdf.name == "drawing.pdf"


def test_save_and_load_review_round_trip(tmp_path: Path) -> None:
    review = Review(
        review_id="PN-123_REV-A",
        part_number="PN-123",
        revision="A",
        title="Bracket",
        source_pdf=Path("source/drawing.pdf"),
        intake=ReviewIntake(
            manufacturing_routes=[ManufacturingRoute.FABRICATED_WELDED],
            certification_status=CertificationStatus.NEW_NOT_CERTIFIED,
        ),
    )

    review_path = tmp_path / "review.yaml"
    save_review(review, review_path)
    loaded = load_review(review_path)

    assert loaded.part_number == "PN-123"
    assert loaded.intake.manufacturing_routes == [ManufacturingRoute.FABRICATED_WELDED]
```

- [x] **Step 2: Run storage tests to verify failure**

Run: `pytest tests/test_storage.py -v`

Expected: FAIL with missing `dfm_reviewer.storage`.

- [x] **Step 3: Implement storage**

Create `src/dfm_reviewer/storage.py`:

```python
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from shutil import copy2
import re

import yaml

from dfm_reviewer.models import Review


@dataclass(frozen=True)
class ReviewPackage:
    root: Path
    source_dir: Path
    source_pdf: Path
    pages_dir: Path
    evidence_dir: Path
    extracted_dir: Path
    reports_dir: Path
    review_yaml: Path


def slugify(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip())
    return cleaned.strip("-") or "review"


def create_review_package(
    reviews_root: Path,
    source_pdf: Path,
    part_number: str,
    revision: str,
    review_date: date | None = None,
) -> ReviewPackage:
    review_date = review_date or date.today()
    folder_name = f"{slugify(part_number)}_REV-{slugify(revision)}_{review_date.isoformat()}"
    root = reviews_root / folder_name
    source_dir = root / "source"
    pages_dir = root / "pages"
    evidence_dir = root / "evidence"
    extracted_dir = root / "extracted"
    reports_dir = root / "reports"

    for folder in [source_dir, pages_dir, evidence_dir, extracted_dir, reports_dir]:
        folder.mkdir(parents=True, exist_ok=True)

    copied_pdf = source_dir / source_pdf.name
    copy2(source_pdf, copied_pdf)

    return ReviewPackage(
        root=root,
        source_dir=source_dir,
        source_pdf=copied_pdf,
        pages_dir=pages_dir,
        evidence_dir=evidence_dir,
        extracted_dir=extracted_dir,
        reports_dir=reports_dir,
        review_yaml=root / "review.yaml",
    )


def save_review(review: Review, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = review.model_dump(mode="json")
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def load_review(path: Path) -> Review:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return Review.model_validate(data)
```

- [x] **Step 4: Run storage tests to verify pass**

Run: `pytest tests/test_storage.py -v`

Expected: PASS.

- [x] **Step 5: Commit**

Run:

```powershell
git add src/dfm_reviewer/storage.py tests/test_storage.py
git commit -m "feat: add review package storage"
```

---

## Task 4: PDF Rendering, Text Extraction, And Cropping

**Files:**
- Create: `src/dfm_reviewer/pdf_processing.py`
- Create: `tests/test_pdf_processing.py`

- [x] **Step 1: Write failing PDF processing tests**

Create `tests/test_pdf_processing.py`:

```python
from pathlib import Path

from reportlab.pdfgen import canvas
from PIL import Image

from dfm_reviewer.pdf_processing import crop_region, extract_page_text, render_pdf_pages


def make_pdf(path: Path) -> None:
    c = canvas.Canvas(str(path), pagesize=(300, 200))
    c.drawString(20, 170, "PART NO: PN-123")
    c.drawString(20, 150, "MATERIAL: 316 SS")
    c.save()


def test_render_pdf_pages_creates_png_per_page(tmp_path: Path) -> None:
    pdf = tmp_path / "drawing.pdf"
    make_pdf(pdf)

    pages = render_pdf_pages(pdf, tmp_path / "pages", zoom=2.0)

    assert len(pages) == 1
    assert pages[0].name == "page-001.png"
    assert pages[0].exists()


def test_extract_page_text_returns_embedded_text(tmp_path: Path) -> None:
    pdf = tmp_path / "drawing.pdf"
    make_pdf(pdf)

    extracted = extract_page_text(pdf)

    assert extracted[0]["page_number"] == 1
    assert "PART NO: PN-123" in extracted[0]["text"]


def test_crop_region_writes_requested_rectangle(tmp_path: Path) -> None:
    image_path = tmp_path / "page.png"
    Image.new("RGB", (200, 100), "white").save(image_path)
    crop_path = tmp_path / "crop.png"

    crop_region(image_path, crop_path, [10, 20, 60, 70])

    with Image.open(crop_path) as cropped:
        assert cropped.size == (50, 50)
```

- [x] **Step 2: Run PDF tests to verify failure**

Run: `pytest tests/test_pdf_processing.py -v`

Expected: FAIL with missing `dfm_reviewer.pdf_processing`.

- [x] **Step 3: Implement PDF processing**

Create `src/dfm_reviewer/pdf_processing.py`:

```python
from pathlib import Path

import fitz
from PIL import Image


def render_pdf_pages(pdf_path: Path, output_dir: Path, zoom: float = 2.0) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    rendered: list[Path] = []
    matrix = fitz.Matrix(zoom, zoom)

    with fitz.open(pdf_path) as document:
        for index, page in enumerate(document, start=1):
            pixmap = page.get_pixmap(matrix=matrix, alpha=False)
            output_path = output_dir / f"page-{index:03}.png"
            pixmap.save(output_path)
            rendered.append(output_path)

    return rendered


def extract_page_text(pdf_path: Path) -> list[dict[str, object]]:
    pages: list[dict[str, object]] = []
    with fitz.open(pdf_path) as document:
        for index, page in enumerate(document, start=1):
            pages.append({"page_number": index, "text": page.get_text("text")})
    return pages


def crop_region(page_image_path: Path, crop_path: Path, region: list[int]) -> Path:
    crop_path.parent.mkdir(parents=True, exist_ok=True)
    left, top, right, bottom = region
    with Image.open(page_image_path) as image:
        image.crop((left, top, right, bottom)).save(crop_path)
    return crop_path
```

- [x] **Step 4: Run PDF tests to verify pass**

Run: `pytest tests/test_pdf_processing.py -v`

Expected: PASS.

- [x] **Step 5: Commit**

Run:

```powershell
git add src/dfm_reviewer/pdf_processing.py tests/test_pdf_processing.py
git commit -m "feat: add PDF rendering and cropping"
```

---

## Task 5: Markdown Report Generation

**Files:**
- Create: `src/dfm_reviewer/reporting.py`
- Create: `tests/test_reporting.py`

- [x] **Step 1: Write failing report tests**

Create `tests/test_reporting.py`:

```python
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
            certification_status=CertificationStatus.EXISTING_CERTIFIED,
            ecn="ECN-456",
        ),
        evidence=[
            EvidenceAnchor(
                evidence_id="EV-001",
                source_pdf=Path("source/drawing.pdf"),
                page_number=1,
                page_image_path=Path("pages/page-001.png"),
                crop_image_path=Path("evidence/EV-001.png"),
                region=[1, 2, 3, 4],
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
                linked_evidence_ids=["EV-001"],
            )
        ],
    )


def test_render_markdown_report_contains_core_sections() -> None:
    markdown = render_markdown_report(make_review())

    assert "# Mechanical DFM Review: PN-123 Rev A" in markdown
    assert "## Design Evidence" in markdown
    assert "evidence/EV-001.png" in markdown
    assert "## DFM Findings" in markdown
    assert "Missing tolerance" in markdown


def test_write_markdown_report_creates_file(tmp_path: Path) -> None:
    output = write_markdown_report(make_review(), tmp_path)

    assert output.name == "mechanical-dfm-review.md"
    assert output.exists()
    assert "Mounting Bracket" in output.read_text(encoding="utf-8")
```

- [x] **Step 2: Run report tests to verify failure**

Run: `pytest tests/test_reporting.py -v`

Expected: FAIL with missing `dfm_reviewer.reporting`.

- [x] **Step 3: Implement report generation**

Create `src/dfm_reviewer/reporting.py`:

```python
from pathlib import Path

from dfm_reviewer.models import Review


def render_markdown_report(review: Review) -> str:
    routes = ", ".join(route.value for route in review.intake.manufacturing_routes) or "not specified"
    ex_concepts = ", ".join(concept.value for concept in review.intake.ex_concepts) or "not specified"

    lines = [
        f"# Mechanical DFM Review: {review.part_number} Rev {review.revision}",
        "",
        "## Review Summary",
        "",
        f"- **Title:** {review.title}",
        f"- **Review ID:** {review.review_id}",
        f"- **Source PDF:** `{review.source_pdf}`",
        f"- **ECN:** {review.intake.ecn or 'not specified'}",
        "",
        "## Drawing Metadata",
        "",
        f"- **Part/assembly number:** {review.part_number}",
        f"- **Revision:** {review.revision}",
        "",
        "## Intake And Context",
        "",
        f"- **Drawing purpose:** {review.intake.drawing_purpose or 'not specified'}",
        f"- **Product/system:** {review.intake.product_or_system or 'not specified'}",
        f"- **Supplier/process:** {review.intake.supplier_or_process or 'not specified'}",
        f"- **Known risks:** {review.intake.known_risks or 'none recorded'}",
        "",
        "## Manufacturing Route",
        "",
        f"- **Selected route(s):** {routes}",
        "",
        "## IECEx Context And Evidence Status",
        "",
        f"- **Protection concept(s):** {ex_concepts}",
        f"- **Certification status:** {review.intake.certification_status.value}",
        "",
        "## Stakeholder Needs",
        "",
        "| ID | Stakeholder | Need | Notes |",
        "| --- | --- | --- | --- |",
    ]

    if review.stakeholder_needs:
        for need in review.stakeholder_needs:
            lines.append(f"| {need.need_id} | {need.stakeholder} | {need.text} | {need.notes} |")
    else:
        lines.append("| - | - | No stakeholder needs recorded in MVP intake. | - |")

    lines.extend(
        [
            "",
            "## Technical Requirements",
            "",
            "| ID | Source Need | Requirement | Rationale | Status |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    if review.requirements:
        for requirement in review.requirements:
            lines.append(
                f"| {requirement.requirement_id} | {requirement.source_need_id or '-'} | "
                f"{requirement.text} | {requirement.rationale} | {requirement.status} |"
            )
    else:
        lines.append("| - | - | No technical requirements recorded yet. | - | - |")

    lines.extend(
        [
            "",
            "## Design Evidence",
            "",
            "| ID | Requirement | Page | Evidence | Extracted Text | Confidence | Note |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    if review.evidence:
        for evidence in review.evidence:
            lines.append(
                f"| {evidence.evidence_id} | {evidence.linked_requirement_id or '-'} | "
                f"{evidence.page_number} | ![]({evidence.crop_image_path.as_posix()}) | "
                f"{evidence.extracted_text} | {evidence.confidence.value} | {evidence.reviewer_note} |"
            )
    else:
        lines.append("| - | - | - | No evidence captured yet. | - | - | - |")

    lines.extend(
        [
            "",
            "## DFM Findings",
            "",
            "| ID | Status | Confidence | Finding | Details | Recommendation | Evidence |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    if review.findings:
        for finding in review.findings:
            evidence_ids = ", ".join(finding.linked_evidence_ids) or "-"
            lines.append(
                f"| {finding.finding_id} | {finding.status.value} | {finding.confidence.value} | "
                f"{finding.title} | {finding.details} | {finding.recommendation or '-'} | {evidence_ids} |"
            )
    else:
        lines.append("| - | - | - | No findings recorded yet. | - | - | - |")

    lines.extend(
        [
            "",
            "## Open Questions And Missing Information",
            "",
        ]
    )
    if review.open_questions:
        for question in review.open_questions:
            lines.append(f"- **{question.question_id}:** {question.text} ({question.context})")
    else:
        lines.append("- No open questions recorded yet.")

    lines.extend(
        [
            "",
            "## Suggested Inspection Or Verification Items",
            "",
        ]
    )
    if review.verification_items:
        for item in review.verification_items:
            lines.append(f"- **{item.verification_id}:** {item.text} [{item.method}]")
    else:
        lines.append("- No verification items recorded yet.")

    lines.extend(
        [
            "",
            "## Appendix: Extracted Drawing Text",
            "",
            "### Title Block",
            "",
            review.extracted_title_block_text or "No title block text extracted yet.",
            "",
            "### Notes",
            "",
            review.extracted_notes_text or "No drawing notes extracted yet.",
            "",
        ]
    )

    return "\n".join(lines)


def write_markdown_report(review: Review, reports_dir: Path) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output = reports_dir / "mechanical-dfm-review.md"
    output.write_text(render_markdown_report(review), encoding="utf-8")
    return output
```

- [x] **Step 4: Run report tests to verify pass**

Run: `pytest tests/test_reporting.py -v`

Expected: PASS.

- [x] **Step 5: Commit**

Run:

```powershell
git add src/dfm_reviewer/reporting.py tests/test_reporting.py
git commit -m "feat: generate Markdown review reports"
```

---

## Task 6: Editable Review Packs

**Files:**
- Create: `src/dfm_reviewer/review_packs.py`
- Create: `tests/test_review_packs.py`
- Create: `review_packs/manufacturing/machined.yaml`
- Create: `review_packs/manufacturing/fabricated_welded.yaml`
- Create: `review_packs/manufacturing/cast_moulded_encapsulated.yaml`
- Create: `review_packs/manufacturing/cable_electromechanical.yaml`
- Create: `review_packs/manufacturing/manual_assembly.yaml`
- Create: `review_packs/iecex/ex_d.yaml`
- Create: `review_packs/iecex/ex_m.yaml`
- Create: `review_packs/iecex/ex_i.yaml`
- Create: `review_packs/iecex/ex_e.yaml`
- Create: `review_packs/iecex/simple_apparatus.yaml`

- [x] **Step 1: Write failing review pack tests**

Create `tests/test_review_packs.py`:

```python
from pathlib import Path

import yaml

from dfm_reviewer.review_packs import ReviewPack, load_review_pack, load_review_packs


def test_load_review_pack_reads_yaml(tmp_path: Path) -> None:
    path = tmp_path / "machined.yaml"
    path.write_text(
        yaml.safe_dump(
            {
                "id": "machined",
                "name": "Machined Parts",
                "category": "manufacturing",
                "prompts": ["Check material callout.", "Check tolerances."],
            }
        ),
        encoding="utf-8",
    )

    pack = load_review_pack(path)

    assert isinstance(pack, ReviewPack)
    assert pack.id == "machined"
    assert pack.prompts == ["Check material callout.", "Check tolerances."]


def test_load_review_packs_finds_nested_yaml_files(tmp_path: Path) -> None:
    folder = tmp_path / "packs" / "manufacturing"
    folder.mkdir(parents=True)
    (folder / "machined.yaml").write_text(
        "id: machined\nname: Machined Parts\ncategory: manufacturing\nprompts:\n  - Check datum scheme.\n",
        encoding="utf-8",
    )

    packs = load_review_packs(tmp_path / "packs")

    assert [pack.id for pack in packs] == ["machined"]
```

- [x] **Step 2: Run review pack tests to verify failure**

Run: `pytest tests/test_review_packs.py -v`

Expected: FAIL with missing `dfm_reviewer.review_packs`.

- [x] **Step 3: Implement review pack loader**

Create `src/dfm_reviewer/review_packs.py`:

```python
from pathlib import Path

import yaml
from pydantic import BaseModel, Field


class ReviewPack(BaseModel):
    id: str
    name: str
    category: str
    prompts: list[str] = Field(default_factory=list)


def load_review_pack(path: Path) -> ReviewPack:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return ReviewPack.model_validate(data)


def load_review_packs(root: Path) -> list[ReviewPack]:
    return [load_review_pack(path) for path in sorted(root.rglob("*.yaml"))]
```

- [x] **Step 4: Add starter pack files**

Create `review_packs/manufacturing/machined.yaml`:

```yaml
id: machined
name: Machined Parts
category: manufacturing
prompts:
  - Check material grade and specification are explicit.
  - Check critical dimensions have tolerances suitable for the function and manufacturing method.
  - Check datum scheme supports inspection and machining setup.
  - Check thread callouts include size, pitch, depth, class, and standard where needed.
  - Check surface finish callouts exist where sealing, fit, wear, or flamepath function depends on finish.
```

Create `review_packs/manufacturing/fabricated_welded.yaml`:

```yaml
id: fabricated_welded
name: Fabricated And Welded Parts
category: manufacturing
prompts:
  - Check weld symbols define size, type, extent, and acceptance expectations.
  - Check bend, cut, and formed features are manufacturable from the selected material thickness.
  - Check distortion-sensitive features have inspection or post-weld machining requirements.
  - Check coating access, drain paths, and masking requirements are clear.
  - Check datum scheme remains usable after fabrication.
```

Create `review_packs/manufacturing/cast_moulded_encapsulated.yaml`:

```yaml
id: cast_moulded_encapsulated
name: Cast, Moulded, And Encapsulated Parts
category: manufacturing
prompts:
  - Check draft, wall thickness, corner radii, and transitions are suitable for the selected process.
  - Check critical machined-after-cast features are identified.
  - Check encapsulation boundaries and keep-out regions are clear where applicable.
  - Check material, compound, cure, and environmental requirements are explicit where applicable.
  - Check inspection access exists for critical embedded or sealed features.
```

Create `review_packs/manufacturing/cable_electromechanical.yaml`:

```yaml
id: cable_electromechanical
name: Cable And Electro-Mechanical Assemblies
category: manufacturing
prompts:
  - Check gland, seal, and strain relief interfaces are specified.
  - Check cable routing, bend radius, clamp positions, and service loops are buildable.
  - Check labels, ferrules, and identification requirements are clear.
  - Check IP sealing and environmental interfaces are inspectable.
  - Check assembly sequence does not trap inaccessible fasteners or terminals.
```

Create `review_packs/manufacturing/manual_assembly.yaml`:

```yaml
id: manual_assembly
name: Manual Assembly And Work Instructions
category: manufacturing
prompts:
  - Check sequence supports safe and repeatable assembly.
  - Check tooling, torque, adhesive, cure, and inspection points are explicit.
  - Check orientation-sensitive parts have clear visual cues.
  - Check acceptance criteria are measurable by the assembler or inspector.
  - Check rework and service access are considered where relevant.
```

Create `review_packs/iecex/ex_d.yaml`:

```yaml
id: ex_d
name: Ex d Advisory Mechanical Review
category: iecex
prompts:
  - Check flamepath-relevant dimensions, fits, lengths, and surface finishes are controlled where applicable.
  - Check fasteners relevant to enclosure integrity are specified with grade, engagement, and retention expectations where applicable.
  - Check marking, enclosure material, and environmental sealing notes are consistent with the certified design where applicable.
  - Check certification drawing or certificate schedule evidence is requested for existing certified product maintenance.
```

Create `review_packs/iecex/ex_m.yaml`:

```yaml
id: ex_m
name: Ex m Advisory Mechanical Review
category: iecex
prompts:
  - Check encapsulation material, boundaries, minimum coverage, and cure requirements are clear where applicable.
  - Check voids, trapped air, and process controls are considered for potted regions.
  - Check inspection or process verification evidence exists for encapsulated features that cannot be inspected afterward.
  - Check certified drawings or datasheets are requested for existing designs.
```

Create `review_packs/iecex/ex_i.yaml`:

```yaml
id: ex_i
name: Ex i Advisory Mechanical Review
category: iecex
prompts:
  - Check segregation, barriers, spacing, and mechanical protection are clear where mechanically relevant.
  - Check labels, terminals, cable entries, and connection interfaces match the intended intrinsically safe use.
  - Check mechanical changes do not undermine certified creepage, clearance, or separation assumptions.
  - Check certification evidence is requested where the design maintains an existing approved product.
```

Create `review_packs/iecex/ex_e.yaml`:

```yaml
id: ex_e
name: Ex e Advisory Mechanical Review
category: iecex
prompts:
  - Check terminal, enclosure, sealing, and mechanical retention details are controlled where applicable.
  - Check creepage, clearance, and tracking-related mechanical features are not obscured by drawing ambiguity.
  - Check ingress protection and environmental sealing details are inspectable.
  - Check certification drawing or approval evidence is requested for existing certified designs.
```

Create `review_packs/iecex/simple_apparatus.yaml`:

```yaml
id: simple_apparatus
name: Simple Apparatus Advisory Review
category: iecex
prompts:
  - Check the basis for simple apparatus treatment is recorded as an open certification/design assumption.
  - Check marking, installation, and interface assumptions are clear where mechanically relevant.
  - Check the drawing does not introduce stored energy, heat, or mechanical features that undermine the assumption.
  - Check evidence or reviewer rationale is captured for later certification review.
```

- [x] **Step 5: Run review pack tests to verify pass**

Run: `pytest tests/test_review_packs.py -v`

Expected: PASS.

- [x] **Step 6: Commit**

Run:

```powershell
git add src/dfm_reviewer/review_packs.py tests/test_review_packs.py review_packs
git commit -m "feat: add editable review packs"
```

---

## Task 7: CLI Vertical Slice

**Files:**
- Create: `src/dfm_reviewer/cli.py`
- Create: `tests/test_cli.py`

- [x] **Step 1: Write failing CLI tests**

Create `tests/test_cli.py`:

```python
from pathlib import Path

from reportlab.pdfgen import canvas
from typer.testing import CliRunner

from dfm_reviewer.cli import app


runner = CliRunner()


def make_pdf(path: Path) -> None:
    c = canvas.Canvas(str(path), pagesize=(300, 200))
    c.drawString(20, 170, "PART NO: PN-123")
    c.save()


def test_cli_create_generates_review_package(tmp_path: Path) -> None:
    pdf = tmp_path / "drawing.pdf"
    make_pdf(pdf)
    reviews_root = tmp_path / "reviews"

    result = runner.invoke(
        app,
        [
            "create",
            str(pdf),
            "--reviews-root",
            str(reviews_root),
            "--part-number",
            "PN-123",
            "--revision",
            "A",
            "--title",
            "Bracket",
            "--manufacturing-route",
            "machined",
            "--certification-status",
            "existing certified product",
        ],
    )

    assert result.exit_code == 0
    assert "Created review" in result.stdout
    review_files = list(reviews_root.rglob("review.yaml"))
    assert len(review_files) == 1


def test_cli_report_writes_markdown(tmp_path: Path) -> None:
    pdf = tmp_path / "drawing.pdf"
    make_pdf(pdf)
    reviews_root = tmp_path / "reviews"
    create_result = runner.invoke(
        app,
        [
            "create",
            str(pdf),
            "--reviews-root",
            str(reviews_root),
            "--part-number",
            "PN-123",
            "--revision",
            "A",
            "--title",
            "Bracket",
            "--manufacturing-route",
            "machined",
        ],
    )
    assert create_result.exit_code == 0
    review_path = next(reviews_root.rglob("review.yaml"))

    report_result = runner.invoke(app, ["report", str(review_path)])

    assert report_result.exit_code == 0
    assert (review_path.parent / "reports" / "mechanical-dfm-review.md").exists()
```

- [x] **Step 2: Run CLI tests to verify failure**

Run: `pytest tests/test_cli.py -v`

Expected: FAIL with missing `dfm_reviewer.cli`.

- [x] **Step 3: Implement CLI**

Create `src/dfm_reviewer/cli.py`:

```python
from pathlib import Path
from uuid import uuid4

import typer
from rich.console import Console

from dfm_reviewer.models import CertificationStatus, ManufacturingRoute, Review, ReviewIntake
from dfm_reviewer.pdf_processing import extract_page_text, render_pdf_pages
from dfm_reviewer.reporting import write_markdown_report
from dfm_reviewer.storage import create_review_package, load_review, save_review

app = typer.Typer(help="Mechanical DFM review workbench")
console = Console()


@app.command()
def create(
    pdf: Path,
    reviews_root: Path = typer.Option(Path("reviews"), help="Folder for review packages."),
    part_number: str = typer.Option(..., help="Part or assembly number."),
    revision: str = typer.Option(..., help="Drawing revision."),
    title: str = typer.Option("", help="Drawing title."),
    manufacturing_route: list[ManufacturingRoute] = typer.Option(
        [ManufacturingRoute.MACHINED],
        help="Manufacturing route. Can be supplied multiple times.",
    ),
    certification_status: CertificationStatus = typer.Option(CertificationStatus.UNKNOWN),
) -> None:
    package = create_review_package(reviews_root, pdf, part_number, revision)
    rendered_pages = render_pdf_pages(package.source_pdf, package.pages_dir)
    page_text = extract_page_text(package.source_pdf)
    (package.extracted_dir / "page-text.json").write_text(
        __import__("json").dumps(page_text, indent=2),
        encoding="utf-8",
    )

    review = Review(
        review_id=f"{part_number}_REV-{revision}_{uuid4().hex[:8]}",
        part_number=part_number,
        revision=revision,
        title=title or part_number,
        source_pdf=package.source_pdf.relative_to(package.root),
        intake=ReviewIntake(
            manufacturing_routes=manufacturing_route,
            certification_status=certification_status,
        ),
        extracted_notes_text="\n\n".join(str(page["text"]) for page in page_text),
    )
    save_review(review, package.review_yaml)

    console.print(f"Created review: {package.root}")
    console.print(f"Rendered pages: {len(rendered_pages)}")


@app.command()
def report(review_yaml: Path) -> None:
    review = load_review(review_yaml)
    output = write_markdown_report(review, review_yaml.parent / "reports")
    console.print(f"Wrote report: {output}")
```

- [x] **Step 4: Run CLI tests to verify pass**

Run: `pytest tests/test_cli.py -v`

Expected: PASS.

- [x] **Step 5: Commit**

Run:

```powershell
git add src/dfm_reviewer/cli.py tests/test_cli.py
git commit -m "feat: add CLI review workflow"
```

---

## Task 8: AI Adapter Boundary

**Files:**
- Create: `src/dfm_reviewer/ai.py`
- Create: `tests/test_ai.py`

- [x] **Step 1: Write failing AI adapter tests**

Create `tests/test_ai.py`:

```python
from dfm_reviewer.ai import DisabledAIProvider, ReviewAIProvider


def test_disabled_ai_provider_returns_clear_message() -> None:
    provider: ReviewAIProvider = DisabledAIProvider()

    result = provider.suggest_open_questions(extracted_text="MATERIAL: 316 SS", context="machined")

    assert result == [
        "AI suggestions are disabled. Capture reviewer questions manually for this review."
    ]
```

- [x] **Step 2: Run AI tests to verify failure**

Run: `pytest tests/test_ai.py -v`

Expected: FAIL with missing `dfm_reviewer.ai`.

- [x] **Step 3: Implement adapter protocol and disabled provider**

Create `src/dfm_reviewer/ai.py`:

```python
from typing import Protocol


class ReviewAIProvider(Protocol):
    def suggest_open_questions(self, extracted_text: str, context: str) -> list[str]:
        """Suggest clarification questions from drawing text and review context."""


class DisabledAIProvider:
    def suggest_open_questions(self, extracted_text: str, context: str) -> list[str]:
        return [
            "AI suggestions are disabled. Capture reviewer questions manually for this review."
        ]
```

- [x] **Step 4: Run AI tests to verify pass**

Run: `pytest tests/test_ai.py -v`

Expected: PASS.

- [x] **Step 5: Commit**

Run:

```powershell
git add src/dfm_reviewer/ai.py tests/test_ai.py
git commit -m "feat: add AI provider boundary"
```

---

## Task 9: Folder Watcher Inbox Scaffolding

**Files:**
- Create: `src/dfm_reviewer/watcher.py`
- Create: `tests/test_watcher.py`

- [x] **Step 1: Write failing watcher tests**

Create `tests/test_watcher.py`:

```python
from pathlib import Path

from dfm_reviewer.watcher import find_pdf_candidates


def test_find_pdf_candidates_returns_nested_pdfs_sorted(tmp_path: Path) -> None:
    first = tmp_path / "ECN-1" / "PN-1.pdf"
    second = tmp_path / "ECN-2" / "PN-2.PDF"
    first.parent.mkdir()
    second.parent.mkdir()
    first.write_bytes(b"pdf")
    second.write_bytes(b"pdf")

    candidates = find_pdf_candidates(tmp_path)

    assert candidates == [first, second]
```

- [x] **Step 2: Run watcher tests to verify failure**

Run: `pytest tests/test_watcher.py -v`

Expected: FAIL with missing `dfm_reviewer.watcher`.

- [x] **Step 3: Implement watcher scan**

Create `src/dfm_reviewer/watcher.py`:

```python
from pathlib import Path


def find_pdf_candidates(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*") if path.is_file() and path.suffix.lower() == ".pdf")
```

- [x] **Step 4: Run watcher tests to verify pass**

Run: `pytest tests/test_watcher.py -v`

Expected: PASS.

- [x] **Step 5: Commit**

Run:

```powershell
git add src/dfm_reviewer/watcher.py tests/test_watcher.py
git commit -m "feat: add PDF inbox scanner"
```

---

## Task 10: Minimal NiceGUI Web App

**Files:**
- Create: `src/dfm_reviewer/web.py`

- [x] **Step 1: Add a manual-run web app**

Create `src/dfm_reviewer/web.py`:

```python
from pathlib import Path
from uuid import uuid4

from nicegui import app as nicegui_app
from nicegui import ui

from dfm_reviewer.models import CertificationStatus, ManufacturingRoute, Review, ReviewIntake
from dfm_reviewer.pdf_processing import extract_page_text, render_pdf_pages
from dfm_reviewer.reporting import write_markdown_report
from dfm_reviewer.storage import create_review_package, save_review


state: dict[str, object] = {"package": None, "review": None, "page_paths": []}


@ui.page("/")
def index() -> None:
    ui.label("Mechanical DFM Reviewer").classes("text-2xl font-bold")
    ui.label("MVP local review workbench").classes("text-sm text-gray-600")

    with ui.card().classes("w-full max-w-3xl"):
        pdf_path = ui.input("PDF path").classes("w-full")
        part_number = ui.input("Part or assembly number").classes("w-full")
        revision = ui.input("Revision", value="A").classes("w-full")
        title = ui.input("Drawing title").classes("w-full")
        route = ui.select(
            {item.value: item.value for item in ManufacturingRoute},
            label="Manufacturing route",
            value=ManufacturingRoute.MACHINED.value,
        ).classes("w-full")
        cert_status = ui.select(
            {item.value: item.value for item in CertificationStatus},
            label="Certification status",
            value=CertificationStatus.UNKNOWN.value,
        ).classes("w-full")

        def create_review() -> None:
            source = Path(pdf_path.value)
            package = create_review_package(Path("reviews"), source, part_number.value, revision.value)
            page_paths = render_pdf_pages(package.source_pdf, package.pages_dir)
            page_text = extract_page_text(package.source_pdf)
            review = Review(
                review_id=f"{part_number.value}_REV-{revision.value}_{uuid4().hex[:8]}",
                part_number=part_number.value,
                revision=revision.value,
                title=title.value or part_number.value,
                source_pdf=package.source_pdf.relative_to(package.root),
                intake=ReviewIntake(
                    manufacturing_routes=[ManufacturingRoute(route.value)],
                    certification_status=CertificationStatus(cert_status.value),
                ),
                extracted_notes_text="\n\n".join(str(page["text"]) for page in page_text),
            )
            save_review(review, package.review_yaml)
            state["package"] = package
            state["review"] = review
            state["page_paths"] = page_paths
            ui.notify(f"Created review at {package.root}")
            pages.refresh()

        ui.button("Create Review", on_click=create_review)

    @ui.refreshable
    def pages() -> None:
        page_paths = state.get("page_paths") or []
        review = state.get("review")
        package = state.get("package")
        if not page_paths:
            ui.label("No rendered pages yet.")
            return
        ui.label("Rendered Pages").classes("text-xl font-semibold")
        for page_path in page_paths:
            ui.image(str(page_path)).classes("w-full max-w-5xl border")
        if review and package:
            def generate_report() -> None:
                output = write_markdown_report(review, package.reports_dir)
                ui.notify(f"Wrote {output}")

            ui.button("Generate Markdown Report", on_click=generate_report)

    pages()


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title="Mechanical DFM Reviewer", reload=False)
```

- [x] **Step 2: Manually run the web app**

Run: `python -m dfm_reviewer.web`

Expected: NiceGUI starts and prints a local URL.

- [x] **Step 3: Commit**

Run:

```powershell
git add src/dfm_reviewer/web.py
git commit -m "feat: add minimal NiceGUI workbench"
```

---

## Task 11: Full Verification

**Files:**
- Modify: `README.md`

- [x] **Step 1: Run automated tests**

Run: `pytest -v`

Expected: all tests pass.

- [x] **Step 2: Run lint**

Run: `ruff check .`

Expected: all checks pass.

- [x] **Step 3: Update README with implemented commands**

Add this section to `README.md`:

```markdown
## CLI Example

```powershell
dfm-reviewer create C:\path\to\drawing.pdf --part-number PN-123 --revision A --title "Mounting Bracket" --manufacturing-route machined
dfm-reviewer report reviews\PN-123_REV-A_2026-04-29\review.yaml
```

## Web App

```powershell
python -m dfm_reviewer.web
```

The web MVP accepts a local PDF path, creates a review package, renders pages, and generates a Markdown report.
```

- [x] **Step 4: Commit**

Run:

```powershell
git add README.md
git commit -m "docs: document MVP usage"
```

---

## Self-Review Notes

Spec coverage:

- Single drawing PDF review: Tasks 2, 3, 4, 7, 10.
- Guided intake: Tasks 2, 7, 10.
- Evidence file structure and crop support: Tasks 3 and 4.
- Markdown report: Task 5.
- Review packs for manufacturing and IECEx: Task 6.
- OpenAI provider boundary: Task 8.
- Folder watcher scaffold: Task 9.
- CLI fallback: Task 7.
- Local web app: Task 10.
- SQLite history, live Confluence/SharePoint writes, DOCX export, and full ECN review remain outside MVP code scope as specified.

Type consistency:

- `Review`, `ReviewIntake`, `EvidenceAnchor`, `Finding`, and enum names are introduced in Task 2 and reused consistently.
- `create_review_package`, `save_review`, and `load_review` are introduced in Task 3 and reused by CLI and web app.
- `render_pdf_pages`, `extract_page_text`, and `crop_region` are introduced in Task 4 and reused by CLI and web app.

