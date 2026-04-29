from pathlib import Path

import fitz
from PIL import Image


def render_pdf_pages(pdf_path: Path, output_dir: Path, zoom: float = 2.0) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    matrix = fitz.Matrix(zoom, zoom)
    page_paths: list[Path] = []

    with fitz.open(pdf_path) as document:
        for index, page in enumerate(document, start=1):
            page_path = output_dir / f"page-{index:03d}.png"
            pixmap = page.get_pixmap(matrix=matrix, alpha=False)
            pixmap.save(page_path)
            page_paths.append(page_path)

    return page_paths


def extract_page_text(pdf_path: Path) -> list[dict[str, object]]:
    pages: list[dict[str, object]] = []

    with fitz.open(pdf_path) as document:
        for index, page in enumerate(document, start=1):
            pages.append(
                {
                    "page_number": index,
                    "text": page.get_text("text"),
                }
            )

    return pages


def crop_region(page_image_path: Path, crop_path: Path, region: list[int]) -> Path:
    crop_path.parent.mkdir(parents=True, exist_ok=True)

    with Image.open(page_image_path) as image:
        cropped = image.crop(tuple(region))
        cropped.save(crop_path)

    return crop_path
