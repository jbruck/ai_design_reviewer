from pathlib import Path


def find_pdf_candidates(root: Path) -> list[Path]:
    """Recursively find all PDF files under the root directory."""
    return sorted(
        path for path in root.rglob("*") if path.is_file() and path.suffix.lower() == ".pdf"
    )
