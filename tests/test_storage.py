from datetime import date
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


def test_create_review_package_uses_unique_folder_for_existing_package(
    tmp_path: Path,
) -> None:
    source_pdf = tmp_path / "drawing.pdf"
    source_pdf.write_bytes(b"%PDF-1.4\n%test\n")
    review_date = date(2026, 4, 29)

    first_package = create_review_package(
        reviews_root=tmp_path / "reviews",
        source_pdf=source_pdf,
        part_number="PN-123",
        revision="A",
        review_date=review_date,
    )
    second_package = create_review_package(
        reviews_root=tmp_path / "reviews",
        source_pdf=source_pdf,
        part_number="PN-123",
        revision="A",
        review_date=review_date,
    )

    assert second_package.root != first_package.root
    assert first_package.source_pdf.exists()
    assert second_package.source_pdf.exists()


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
