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
    if len(region) != 4:
        msg = "Crop region must contain exactly 4 coordinates."
        raise ValueError(msg)

    left, top, right, bottom = region
    if left < 0 or top < 0:
        msg = "Crop region left and top coordinates must be non-negative."
        raise ValueError(msg)

    if left >= right or top >= bottom:
        msg = "Crop region must satisfy left < right and top < bottom."
        raise ValueError(msg)

    with Image.open(page_image_path) as image:
        if right > image.width or bottom > image.height:
            msg = "Crop region must be within image bounds."
            raise ValueError(msg)

        crop_path.parent.mkdir(parents=True, exist_ok=True)
        cropped = image.crop(tuple(region))
        cropped.save(crop_path)

    return crop_path
