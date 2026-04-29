from collections.abc import Iterator
from pathlib import Path
from uuid import uuid4

import pytest


@pytest.fixture
def tmp_path() -> Iterator[Path]:
    root = Path(".test-tmp")
    root.mkdir(exist_ok=True)
    path = root / uuid4().hex
    path.mkdir()
    yield path
