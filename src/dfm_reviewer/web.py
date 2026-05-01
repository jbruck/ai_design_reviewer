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
            if not pdf_path.value:
                ui.notify("PDF path is required.", type="negative")
                return
            
            source = Path(pdf_path.value)
            if not source.exists():
                ui.notify(f"PDF not found: {source}", type="negative")
                return

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
            ui.image(str(page_path)).classes("w-full max-w-5xl border m-2")
        if review and package:
            def generate_report() -> None:
                output = write_markdown_report(review, package.reports_dir)
                ui.notify(f"Wrote {output}")

            ui.button("Generate Markdown Report", on_click=generate_report).classes("m-2")

    pages()


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title="Mechanical DFM Reviewer", reload=False)
