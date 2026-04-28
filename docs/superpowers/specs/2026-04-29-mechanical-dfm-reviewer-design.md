# Mechanical DFM Reviewer MVP Design

## Purpose

Build a local Python-first review workbench for mechanical DFM reviews of SolidWorks drawing PDFs. The first useful version focuses on guided intake, evidence capture, and Markdown report generation for a single part or assembly drawing. Automated review intelligence is scaffolded, but the MVP should be useful even when the AI needs human correction.

The system is for the mechanical team first. It does not replace existing release gates, formal signoff, certification approval, or company-wide review processes.

## Design Goals

- Review one component or assembly PDF at a time.
- Support a local web app as the primary interface.
- Provide a CLI fallback that uses the same backend logic.
- Keep most code in Python for maintainability by the primary user.
- Use deterministic Python tools for PDF rendering, OCR, cropping, file watching, templating, and storage.
- Use cloud AI only where judgment or interpretation is needed.
- Keep the AI provider modular so it can later be redirected to another cloud or local provider.
- Generate Markdown as the primary export format.
- Preserve evidence as real local files, with auditable citations from generated review content.
- Scaffold later growth into ECN-level, product-level, Confluence, SharePoint, and database-backed workflows.

## Non-Goals For MVP

- No live Confluence or SharePoint writes.
- No replacement of existing signoff or release processes.
- No full IECEx certification determination.
- No formal standards retrieval or clause-citing engine.
- No heavy audit trail or immutable review history.
- No full ECN package review.
- No company-wide cross-functional review workflow.

## Primary User

The MVP is optimized for Jonathan's personal mechanical review workflow. The design should avoid hard-coding assumptions that would prevent later use by other mechanical design engineers or mechanical checkers.

## Product Scope

### MVP Scope

The MVP handles a single drawing PDF review. It guides the user through intake, renders the PDF, captures evidence crops, stores review data locally, and exports a Markdown report.

### Later Scope

The architecture should allow later expansion to:

- ECN/change package review.
- Top-level assembly and BOM traversal.
- Product and certification family history.
- Work instruction/manual assembly review.
- Locally synced SharePoint folder ingestion.
- Confluence page ingestion and later publishing.
- SQLite-backed review history and search.
- DOCX export from Markdown.

## Architecture Overview

The system is composed of Python services with two user interfaces:

- NiceGUI local web app for the primary workflow.
- Typer CLI for fallback operation and automation.

Both interfaces call the same application services and data models.

```text
User
  -> NiceGUI web app
  -> Typer CLI

Interfaces
  -> Review service
  -> PDF processing service
  -> Evidence service
  -> Review pack service
  -> AI adapter
  -> Report generator
  -> Local file store
```

## Components

### Web App

Use NiceGUI for a Python-first local web interface.

Responsibilities:

- Select or upload drawing PDFs.
- Run the guided intake interview.
- Display rendered PDF pages.
- Allow evidence crop creation and correction.
- Show extracted text and AI suggestions.
- Let the user accept, reject, edit, or replace suggested evidence and findings.
- Generate and open Markdown review reports.

The strongest part of the MVP UI should be evidence correction. The user must be able to adjust a crop, replace a crop, unlink a crop, or attach it to a different requirement/finding.

### CLI

Use Typer for command-line fallback.

Initial commands:

- Create a review folder from a PDF.
- Run intake prompts.
- Render PDF pages.
- Extract text/OCR.
- Generate Markdown report.

The CLI may have limited crop editing at first, but it must share the same data model and report generator as the web app.

### PDF Processing Service

Use established Python tools for deterministic document work.

Responsibilities:

- Render PDF pages to high-resolution images.
- Extract embedded text where available.
- Run OCR where embedded text is poor or absent.
- Capture title block and drawing notes where possible.
- Crop evidence regions from page images.
- Store page images, crop images, and extracted text.

Candidate tools:

- PyMuPDF for PDF rendering and text extraction.
- Pillow for image manipulation.
- Tesseract/pytesseract or another OCR layer if available.

### Evidence Service

Evidence anchors are a core data structure. Each anchor links a requirement or finding to a real screenshot crop and source location.

Each evidence item stores:

- Evidence ID.
- Source PDF path.
- Page number.
- Page image path.
- Crop image path.
- Region coordinates.
- Extracted text from the region if available.
- Linked requirement ID.
- Linked finding ID.
- Confidence.
- Reviewer note.

Evidence crops should be created automatically where possible, but the reviewer must be able to override them.

### Review Data Model

Use Pydantic models or similar Python dataclasses for structured review data.

Core entities:

- Review.
- Drawing metadata.
- Intake response.
- Manufacturing route.
- IECEx context.
- Stakeholder need.
- Technical requirement.
- Evidence anchor.
- DFM finding.
- Open question.
- Verification or inspection suggestion.

The model should be database-ready, even though the MVP saves to files.

### Review Packs

Review packs are editable YAML/Markdown files that provide checklist prompts and review guidance.

Initial packs:

- Machined parts.
- Fabricated/welded parts.
- Cast, moulded, and encapsulated parts.
- Cable/electro-mechanical assemblies.
- Manual assembly/work instruction review.
- Ex d.
- Ex m.
- Ex i.
- Ex e.
- Simple apparatus.

These packs are advisory mechanical review prompts. They are not certification decisions or authoritative standards text.

### AI Adapter

Provide a modular provider interface for AI calls.

Responsibilities:

- Interpret drawing notes and callouts.
- Suggest missing requirements and open questions.
- Suggest DFM findings based on selected manufacturing route.
- Suggest IECEx evidence gaps based on selected Ex type and certification status.
- Map evidence crops and extracted text to requirements/findings.
- Draft report text from structured review data.

The AI should not be used for deterministic tasks such as rendering PDFs, cropping images, watching folders, or formatting Markdown.

### Report Generator

Generate Markdown from the review model and evidence files.

MVP report sections:

1. Review summary.
2. Drawing metadata.
3. Intake and context.
4. Manufacturing route.
5. IECEx context and evidence status.
6. Stakeholder needs scaffold.
7. Technical requirements scaffold.
8. Design evidence table.
9. DFM findings.
10. Open questions and missing information.
11. Suggested inspection or verification items.
12. Appendix: extracted title block, drawing notes, and OCR text.

The report should be concise but complete enough to move into Confluence later.

## Local Storage

The MVP uses file-based review packages. Each review folder contains the source PDF, page renders, evidence crops, extracted text, structured review state, and generated reports.

Example:

```text
reviews/
  PART-1234_REV-A_2026-04-29/
    review.yaml
    source/
      drawing.pdf
    pages/
      page-001.png
      page-002.png
    evidence/
      EV-001.png
      EV-002.png
    extracted/
      page-text.json
      ocr.json
    reports/
      mechanical-dfm-review.md
```

The later database should index this data, not replace evidence files. PDFs, crops, and generated reports remain real artefacts with stable paths and source citations.

## Intake Flow

Use a two-pass interview model.

### Pass 1: Pre-Review Intake

Ask enough questions to ground the review:

- Part or assembly number.
- Revision.
- Drawing purpose.
- Intended product or system if known.
- ECN/change number if known.
- Manufacturing route.
- Supplier/process assumptions.
- Ex protection concept if applicable.
- Certification status: existing certified product, maintenance of existing design, new product not yet certified, or non-Ex/simple apparatus.
- Known risks or design concerns.
- Required supporting documents if known.

### Pass 2: Targeted Follow-Up

After PDF rendering, text extraction, and preliminary review, ask targeted questions based on gaps:

- Missing or unclear title block data.
- Missing material, finish, tolerance, note, or inspection requirement.
- Unclear Ex classification or certification evidence.
- Unclear manufacturing process assumptions.
- Drawing features that need human interpretation.

For MVP, Pass 1 is the priority. Pass 2 can begin as a simple open-questions list.

## Review Behavior

Use a hybrid review style:

- Checklist backbone.
- Concise engineering commentary.
- Prioritized findings.
- Lifecycle traceability scaffold.

Every finding should have a status and confidence:

- Confirmed issue.
- Likely issue.
- Needs human review.
- Missing information.
- Advisory suggestion.

The system should ask for clarification where uncertainty matters.

## IECEx Handling

IECEx review is evidence-aware but not certification-authoritative.

For existing certified products, the tool should ask for or reference:

- Certification drawing if available.
- Certificate schedule or datasheet if available.
- Existing Ex type.
- Existing approval constraints.
- Relevant drawing notes and markings.

For new products not yet certified, the tool should identify likely evidence gaps and questions for later certification review.

The MVP may use Ex-type review packs for common mechanical prompts, but it must not claim to prove compliance with IECEx standards.

## Folder Watcher

Include scaffolding for a watched folder workflow.

Expected future use:

- PDM exports PDFs into an ECN-organized folder hierarchy.
- Each part or assembly has an ECN number in metadata/datacard and/or filename/path.
- The watcher detects new PDFs and creates review candidates.

MVP watcher behavior can be simple:

- Watch configured folders.
- Detect new PDFs.
- Add them to an inbox list.
- Let the user start a review manually.

No PDM API integration is assumed.

## SharePoint And Confluence Scaffolding

The MVP should include abstraction boundaries for document sources, but no live writes.

Initial source types:

- Local file.
- Local folder.
- Locally synced SharePoint folder.
- Future Confluence page/source adapter.

These adapters should provide document discovery and citation metadata. Publishing to Confluence or writing to SharePoint is out of scope for MVP.

## Implementation Priority

1. Create the review data model and file package layout.
2. Build the guided intake flow.
3. Render PDF pages and show them in the local web app.
4. Support manual evidence crop creation and correction.
5. Generate Markdown reports with evidence tables.
6. Add basic editable review packs.
7. Add AI-assisted suggestions for questions, findings, and evidence mapping.
8. Add folder watcher inbox.
9. Add CLI fallback.
10. Add SQLite index/history after the MVP workflow proves useful.

## Success Criteria

The first prototype is useful if, after one real drawing review:

- The intake flow captures the key manufacturing and IECEx context.
- The user can create and correct evidence crops without fighting the UI.
- The Markdown report is worth keeping as a review artefact.
- The structured review folder is understandable and auditable.
- The system exposes uncertainty clearly instead of hiding it.

## Open Design Decisions

- Exact OCR engine and local installation assumptions.
- Whether the first web UI uses built-in NiceGUI image interaction or a small custom browser component for crop selection.
- Exact AI provider and model configuration.
- Whether review state is YAML or JSON for the first pass.
- How soon to introduce SQLite indexing.

