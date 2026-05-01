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


@app.callback()
def main() -> None:
    """Run the Mechanical DFM reviewer CLI."""
