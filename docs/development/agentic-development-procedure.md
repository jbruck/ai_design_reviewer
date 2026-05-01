# Agentic Development Procedure

## Purpose

This procedure defines how AI development agents and human engineers continue the Mechanical DFM Reviewer project without depending on any one agent platform. It is intended to be readable by Codex, Claude, Gemini, or a conventional software engineer.

## Governing Principle

The repository must remain resumable from a fresh session without creating low-value documentation churn.

A new agent should be able to read the repository files, inspect git history, run verification commands, and continue development without access to previous chat context.

## Required Inputs

Before making changes, read:

1. `AGENTS.md`
2. `docs/superpowers/specs/2026-04-29-mechanical-dfm-reviewer-design.md`
3. `docs/superpowers/plans/2026-04-29-mechanical-dfm-reviewer-mvp.md`
4. The latest checkpoint in `docs/superpowers/checkpoints/`
5. This procedure

The `docs/superpowers/` path is historical. Its contents are project records and may be used by any platform.

## Work Location

Continue MVP implementation in:

```text
.worktrees/mvp
```

On branch:

```text
feature/mechanical-dfm-mvp
```

Do not create a new implementation branch unless the user asks or the existing worktree is unavailable.

## Standard Verification Commands

From the MVP worktree:

```powershell
$env:UV_CACHE_DIR = "$PWD\.uv-cache"
New-Item -ItemType Directory -Force .uv-cache, .test-tmp | Out-Null
uv run pytest
uv run ruff check src tests
git status --short
```

Use targeted tests before full tests when implementing a specific task.

## Task Execution Standard

For each implementation task:

1. Identify the current task from the plan and checkpoint.
2. Write or update tests first.
3. Run the targeted test and verify it fails for the expected reason.
4. Implement the smallest useful change.
5. Run targeted tests.
6. Run full tests and lint.
7. Update the checkpoint if plan progress, verification status, next action, or risks changed.
8. Commit code, tests, and any useful checkpoint update together.
9. Perform or request a spec compliance review.
10. Perform or request a code quality review.
11. Fix review findings before moving to the next task.

## Checkpoint Standard

Update the current checkpoint before commits that change the project state in a way a fresh agent would need to know.

When updated, the checkpoint must include:

- Current objective.
- Completed work since the previous checkpoint.
- Files changed.
- Commands run and exact results.
- Current git branch and relevant commit IDs.
- Plan progress.
- Next single action.
- Risks, blockers, or uncertainties.

Use `docs/development/checkpoint-template.md` as the format reference.

If a commit is purely administrative or very small and does not materially change implementation progress, verification status, the next action, or risks, do not rewrite the checkpoint.

## Platform-Agnostic Orchestration

The preferred orchestration is:

- One implementation task at a time.
- Test-first development.
- Review after each task:
  - Spec compliance review.
  - Code quality review.
- Small commits.
- Checkpoint updates when state changes materially.

This can be performed by:

- One agent working inline.
- A supervising agent plus worker/reviewer agents.
- A human engineer plus AI reviewers.

The process does not require Codex-specific tools. If subagents, skills, or tool plugins are unavailable, perform the same steps manually and record the deviation in the checkpoint.

## Agent Platform Notes

Codex:

- May use local tools, worktrees, and subagents when available.
- Must still keep the checkpoint current.

Claude:

- Should treat `AGENTS.md` and this procedure as the project operating guide.
- May use its own task/review mechanisms if equivalent.

Gemini:

- Should follow the same task/checkpoint/review sequence.
- May use its own planning or coding tools if outputs are committed to the repo.

Human engineer:

- Can use the same documents as a lightweight development log and review checklist.

## Commit Standard

Commit messages should be concise and conventional where practical:

```text
feat: add review package storage
fix: validate evidence anchor geometry
chore: keep test tooling project-local
docs: update MVP checkpoint
```

Commits that materially change implementation state should include the checkpoint update. Trivial edits may skip checkpoint updates to preserve signal.

## Prohibited Shortcuts

- Do not rely on chat history as the only record of progress.
- Do not move to the next task with unresolved review findings.
- Do not skip verification because a prior agent reported success.
- Do not write live Confluence or SharePoint integrations during the MVP unless the plan is explicitly revised.
- Do not introduce full database/history architecture before the MVP asks for it.

## Resuming From A Fresh Session

A fresh agent should:

1. Read `AGENTS.md`.
2. Read this procedure.
3. Read the latest checkpoint.
4. Change into the MVP worktree.
5. Run the standard verification commands.
6. Continue from the checkpoint's next action.
