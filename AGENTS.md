# AGENTS.md

This repository should be easy to continue with Codex, Claude, Gemini, or a human engineer. Treat the files in `docs/superpowers/` as project documentation, not as a Codex-only workflow.

Development agents must keep the repo resumable while staying concise. Update the checkpoint when a commit changes the plan state, next action, verification status, risks, or implementation behavior. Do not rewrite checkpoints for trivial edits that do not alter the state of play.

## Project

The goal is to build a local Python-first Mechanical DFM Reviewer for SolidWorks drawing PDFs. The MVP focuses on:

- Guided mechanical intake for one part or assembly drawing PDF.
- Local review package storage.
- PDF rendering, embedded text extraction, and evidence cropping.
- Markdown review report generation.
- Editable manufacturing and IECEx advisory review packs.
- CLI fallback.
- Minimal NiceGUI local web app.
- OpenAI as the initial app-time AI provider behind a replaceable adapter.

## Key Docs

Read these before continuing development:

- `docs/superpowers/specs/2026-04-29-mechanical-dfm-reviewer-design.md`
- `docs/superpowers/plans/2026-04-29-mechanical-dfm-reviewer-mvp.md`
- `docs/superpowers/checkpoints/2026-04-29-mechanical-dfm-reviewer-mvp-checkpoint.md`
- `docs/development/agentic-development-procedure.md`
- `docs/development/checkpoint-template.md`

The checkpoint is the fastest way to resume after a context switch.

## Current Implementation Branch

Implementation work is happening in a git worktree:

```text
C:\Users\jonathan.b\ai\ai_design_reviewer\.worktrees\mvp
```

Branch:

```text
feature/mechanical-dfm-mvp
```

Unless intentionally changing branch strategy, continue from that worktree.

## Development Environment

Use `uv` and the project-local virtual environment.

From the implementation worktree:

```powershell
$env:UV_CACHE_DIR = "$PWD\.uv-cache"
New-Item -ItemType Directory -Force .uv-cache, .test-tmp | Out-Null
uv sync --extra dev
uv run --no-sync pytest
uv run --no-sync ruff check src tests
```

The project config disables pytest's cache provider. Tests override pytest's built-in `tmp_path` fixture to use `.test-tmp/` inside the worktree because Windows ACLs caused permission failures with pytest's default temp factory. Keep uv's package cache inside the worktree with `UV_CACHE_DIR`. After the environment has been synced, prefer `uv run --no-sync ...` for test and lint commands so uv does not try to rebuild the editable package in `.uv-cache`.

## Development Workflow

Work task-by-task from the MVP implementation plan.

Preferred AI operating model:

- Use a strong top-level orchestrator agent to keep the plan, checkpoint, review gates, verification, and git scope under control.
- Use lower-token worker subagents for narrow implementation tasks with explicit file ownership and expected tests.
- Use reviewer subagents for read-only spec compliance and code-quality reviews.
- Keep subagent prompts self-contained and narrow. Avoid broad prompts such as "continue the MVP".
- Do not run parallel worker subagents against the same files or shared behavior unless the write scopes are clearly disjoint.
- The orchestrator must inspect diffs and run verification locally before committing, even when a subagent reports success.

For each task:

1. Write or update tests first.
2. Run the targeted test and confirm it fails for the expected reason.
3. Implement the smallest useful change.
4. Run the targeted test, full test suite, and ruff.
5. Update the current checkpoint if the change affects plan progress, verification evidence, remaining work, next action, or risks.
6. Commit the task with a concise message.
7. Review for both spec compliance and code quality before moving to the next task.

Every meaningful implementation commit must leave enough written state for a new development agent to resume. Small commits that do not change the overall state of play do not need checkpoint churn.

Do not skip review of Task 4. The current checkpoint says Task 4 implementation is committed but not yet reviewed.

## Commands

Common commands from the implementation worktree:

```powershell
$env:UV_CACHE_DIR = "$PWD\.uv-cache"
New-Item -ItemType Directory -Force .uv-cache, .test-tmp | Out-Null
uv run --no-sync pytest tests/test_pdf_processing.py -v
uv run --no-sync pytest
uv run --no-sync ruff check src tests
git status --short
```

CLI and web commands may be stubs until later MVP tasks:

```powershell
uv run dfm-reviewer --help
uv run python -m dfm_reviewer.web
```

## Coding Guidelines

- Keep most application code in Python.
- Prefer deterministic Python libraries for deterministic work:
  - PyMuPDF for PDF rendering and embedded text extraction.
  - Pillow for image cropping.
  - Pydantic for structured review state.
  - Typer for CLI.
  - NiceGUI for the local web app.
- Use AI only for interpretation, judgment, review suggestions, and report drafting.
- Keep OpenAI-specific code behind an adapter boundary.
- Keep files and services small and focused.
- Store evidence as real files and structured citations, not opaque blobs.
- Do not introduce database, Confluence write, SharePoint write, DOCX export, or full ECN workflow before the MVP asks for it.

## Git Safety

- Do not revert user changes unless explicitly asked.
- Do not use destructive commands such as `git reset --hard` or checkout-based file reverts without explicit permission.
- Commit small, coherent steps.
- Include checkpoint updates when progress against the plan, verification status, next action, or risks change.
- Keep generated review artefacts under `reviews/`, which is ignored.
- `.worktrees/` is ignored and should remain ignored.

## Known Local Issue

A generated directory named similar to this may exist in the MVP worktree:

```text
pytest-cache-files-u3x6blsf/
```

It was previously undeletable due local permission behavior and is ignored. Do not rely on it. The project disables pytest's cache provider in `pyproject.toml`. Keep uv's package cache local to the worktree by setting:

```powershell
$env:UV_CACHE_DIR = "$PWD\.uv-cache"
```

## Model-Agnostic Handoff

This project does not require Codex to continue development. A future AI development agent should:

1. Read this file.
2. Read `docs/development/agentic-development-procedure.md`.
3. Read the latest checkpoint.
4. Change into the MVP worktree.
5. Verify tests and lint.
6. Resume from the next remaining task.

The app may initially call OpenAI, but the development workflow can be performed by Codex, Claude, Gemini, or another capable coding agent.
