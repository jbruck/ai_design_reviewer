from pathlib import Path

import pytest
from PIL import Image
from reportlab.pdfgen import canvas

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


def test_crop_region_rejects_invalid_region_length(tmp_path: Path) -> None:
    image_path = tmp_path / "page.png"
    Image.new("RGB", (200, 100), "white").save(image_path)

    with pytest.raises(ValueError, match="exactly 4 coordinates"):
        crop_region(image_path, tmp_path / "crop.png", [10, 20, 60])


def test_crop_region_rejects_negative_coordinates(tmp_path: Path) -> None:
    image_path = tmp_path / "page.png"
    Image.new("RGB", (200, 100), "white").save(image_path)

    with pytest.raises(ValueError, match="non-negative"):
        crop_region(image_path, tmp_path / "crop.png", [-1, 20, 60, 70])


def test_crop_region_rejects_reversed_or_empty_region(tmp_path: Path) -> None:
    image_path = tmp_path / "page.png"
    Image.new("RGB", (200, 100), "white").save(image_path)

    invalid_regions = [
        [60, 20, 10, 70],
        [10, 70, 60, 20],
        [10, 20, 10, 70],
        [10, 20, 60, 20],
    ]

    for region in invalid_regions:
        with pytest.raises(ValueError, match="left < right and top < bottom"):
            crop_region(image_path, tmp_path / "crop.png", region)


def test_crop_region_rejects_out_of_bounds_region(tmp_path: Path) -> None:
    image_path = tmp_path / "page.png"
    Image.new("RGB", (200, 100), "white").save(image_path)
    invalid_regions = [
        [10, 20, 201, 70],
        [10, 20, 60, 101],
    ]

    for index, region in enumerate(invalid_regions):
        crop_path = tmp_path / f"nested-{index}" / "crop.png"

        with pytest.raises(ValueError, match="within image bounds"):
            crop_region(image_path, crop_path, region)

        assert not crop_path.parent.exists()
