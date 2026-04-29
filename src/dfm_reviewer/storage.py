import re
import shutil
from dataclasses import dataclass
from datetime import date
from pathlib import Path

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
    slug = re.sub(r"[^A-Za-z0-9]+", "-", value).strip("-").lower()
    return slug or "untitled"


def create_review_package(
    reviews_root: Path,
    source_pdf: Path,
    part_number: str,
    revision: str,
    review_date: date | None = None,
) -> ReviewPackage:
    review_date = review_date or date.today()
    package_name = f"{review_date.isoformat()}_{slugify(part_number)}_rev-{slugify(revision)}"
    root = reviews_root / package_name
    source_dir = root / "source"
    pages_dir = root / "pages"
    evidence_dir = root / "evidence"
    extracted_dir = root / "extracted"
    reports_dir = root / "reports"
    review_yaml = root / "review.yaml"

    for directory in (source_dir, pages_dir, evidence_dir, extracted_dir, reports_dir):
        directory.mkdir(parents=True, exist_ok=True)

    copied_pdf = source_dir / source_pdf.name
    shutil.copy2(source_pdf, copied_pdf)

    return ReviewPackage(
        root=root,
        source_dir=source_dir,
        source_pdf=copied_pdf,
        pages_dir=pages_dir,
        evidence_dir=evidence_dir,
        extracted_dir=extracted_dir,
        reports_dir=reports_dir,
        review_yaml=review_yaml,
    )


def save_review(review: Review, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    yaml_text = yaml.safe_dump(review.model_dump(mode="json"), sort_keys=False)
    path.write_text(yaml_text, encoding="utf-8")


def load_review(path: Path) -> Review:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return Review.model_validate(data)
