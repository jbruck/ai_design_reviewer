# Mechanical DFM Reviewer

Local Python-first workbench for mechanical DFM review of drawing PDFs.

## MVP Workflow

1. **Intake:** Create a review package from a drawing PDF.
2. **Analysis:** Render drawing pages and extract text (automated).
3. **Evidence:** Capture evidence crops and link to findings (Web UI).
4. **Reporting:** Generate a comprehensive Markdown review report.

## Installation

This project uses `uv` for dependency management.

```powershell
uv sync --extra dev
```

## Usage

### Command Line Interface (CLI)

The CLI provides commands for creating reviews and generating reports.

**Create a new review:**
```powershell
uv run dfm-reviewer create path/to/drawing.pdf --part-number PN-123 --revision A --title "Mounting Bracket"
```

**Generate a report:**
```powershell
uv run dfm-reviewer report reviews/PN-123_REV-A_2026-05-01/review.yaml
```

**List all commands:**
```powershell
uv run dfm-reviewer --help
```

### Local Web Workbench

The NiceGUI web app provides a visual interface for the review process.

```powershell
uv run python -m dfm_reviewer.web
```

Navigate to `http://localhost:8080` to access the workbench.

## Development

**Run Tests:**
```powershell
uv run pytest
```

**Run Linting:**
```powershell
uv run ruff check .
```

## Structure

- `src/dfm_reviewer/`: Core logic and services.
- `review_packs/`: Editable YAML checklists for manufacturing and IECEx.
- `reviews/`: (Generated) Local storage for review packages.
- `docs/`: Project documentation and checkpoints.
