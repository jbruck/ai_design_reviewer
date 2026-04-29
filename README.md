# Mechanical DFM Reviewer

Local Python-first workbench for mechanical DFM review of drawing PDFs.

## MVP Workflow

1. Create a review from a drawing PDF.
2. Complete the mechanical intake.
3. Render drawing pages.
4. Capture evidence crops.
5. Generate a Markdown review report.

## Development

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .[dev]
pytest
```

## Run

```powershell
dfm-reviewer --help
python -m dfm_reviewer.web
```
