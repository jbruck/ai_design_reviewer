# Checkpoint Template

Use this template before every commit that changes project state. Keep it concise but complete enough for a fresh agent session to resume work.

## 1. Objective

State the current project goal and the active plan task.

## 2. Current Status

Completed since previous checkpoint:

- Itemize code, tests, docs, or configuration changes.

Partially complete:

- Itemize work that has started but has not passed review or verification.

Not started:

- Itemize remaining plan tasks.

## 3. Filesystem State

Files changed:

- `path/to/file.py` - brief purpose of change.

Relevant directories:

- `path/to/directory/` - why it matters.

Important diffs or content summaries:

- Summarize behavior, not every line.

## 4. Environment

- Shell:
- Worktree:
- Branch:
- Python:
- uv:
- Key environment variables:
- Verification command style:

## 5. Decisions And Assumptions

- Record decisions made during this increment.
- Record assumptions future agents should preserve.

## 6. Verification

Commands run:

```text
command -> result
```

Failures or skipped checks:

- Explain why and what to do next.

## 7. Remaining Plan

1. Next plan step.
2. Following plan step.
3. Later plan step.

## 8. Next Action

The single next command or operation to run.

## 9. Risks And Uncertainties

- Anything likely to cause failure.
- Any unresolved review finding.
- Any permission, dependency, or environment concern.

