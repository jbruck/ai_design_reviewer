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
