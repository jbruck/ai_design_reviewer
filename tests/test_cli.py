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
