# Mechanical DFM Reviewer: Phase 1 (Intelligence & Persistence)

**Goal:** Transform the MVP from a manual workbench into an AI-assisted review platform with robust history, broader drawing support, and professional reporting.

## Overview of Phase 1

1.  **AI Orchestration:** Implement the OpenAI adapter to generate automated DFM suggestions and clarifying questions.
2.  **OCR Pass:** Add Tesseract/OCR support for drawings without embedded text.
3.  **SQLite Storage:** Migration from pure YAML to a local database for review history and cross-project search.
4.  **Professional Export:** Support for DOCX and PDF report generation.

---

## Task 1: OpenAI Adapter Implementation

**Objective:** Enable the "Reviewer suggestions" feature using LLMs.

- [ ] **Step 1: Implement OpenAIProvider**
  - Create `src/dfm_reviewer/ai_openai.py` (or update `ai.py`).
  - Implement structured output parsing for DFM findings and questions.
  - Add `OPENAI_API_KEY` handling via `.env`.
- [ ] **Step 2: Integrate with Web/CLI**
  - Add "Ask AI" button to the NiceGUI workbench.
  - Add `--ai` flag to CLI `create` command.
- [ ] **Step 3: Verification**
  - Mock OpenAI responses in tests to verify injection logic.

## Task 2: OCR for Rasterized Drawings

**Objective:** Support drawings where text is stored as paths or images (not embedded).

- [ ] **Step 1: Add OCR Dependencies**
  - Add `pytesseract` to `pyproject.toml`.
- [ ] **Step 2: Implement OCR Service**
  - Create `src/dfm_reviewer/ocr.py`.
  - Update `pdf_processing.py` to fall back to OCR if `get_text()` returns low-density results.
- [ ] **Step 3: Verification**
  - Add a rasterized PDF fixture and verify text recovery.

## Task 3: SQLite Persistence & History

**Objective:** Move from "one folder = one review" to a searchable local database.

- [ ] **Step 1: Define Schema**
  - Use `SQLAlchemy` or `SQLModel`.
  - Support `Review`, `Finding`, and `Evidence` tables.
- [ ] **Step 2: Migration Logic**
  - Implement a tool to ingest existing `review.yaml` files into the DB.
- [ ] **Step 3: Dashboard**
  - Add a "History" view to the NiceGUI app to list and search past reviews.

## Task 4: Professional Reporting (DOCX/PDF)

**Objective:** Generate reports suitable for official submission.

- [ ] **Step 1: Add Export Dependencies**
  - Add `python-docx` and `reportlab` (already in dev) to core dependencies.
- [ ] **Step 2: Implement DOCX Template**
  - Create `src/dfm_reviewer/export.py`.
  - Support image embedding for evidence crops.
- [ ] **Step 3: CLI/Web Integration**
  - `dfm-reviewer export --format docx`
  - "Download DOCX" button in Web UI.

---

## Technical Standards

- **Graceful Failure:** If OCR or AI is unavailable, the manual workflow must remain 100% functional.
- **Privacy:** Ensure `OPENAI_API_KEY` is never logged or committed.
- **Portability:** SQLite DB must reside within the `reviews/` folder or a user-configurable local path.
