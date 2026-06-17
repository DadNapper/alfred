# GitHub task tracking transition — 2026-06-17

Use this reference when maintaining Scraplands workflow docs/skills after the move from repo-local task files to GitHub Issues + GitHub Project.

## Durable decision

GitHub Issues + the Scraplands GitHub Project are the source of truth for actionable bugs, features, and tech debt.

The repo-local `ai/tasks/` workflow is retired:

- Do not create `ai/tasks/active/`, `ai/tasks/testing/`, or `ai/tasks/published/`.
- Do not recreate `ai/tasks/` for long Cursor handoffs.
- Put implementation context in the GitHub issue body or issue comments.
- Use GitHub labels/project fields for priority and status.
- Every implementation issue should include a Cursor model hint both in the body (`## Model` / `Model: auto|medium|premium`) and as a matching `model:*` label.

## Oz → Cursor bug-fix handoff

Oz's default bug-fix path is:

1. Open the canonical GitHub issue.
2. Copy the GitHub issue URL/body into Cursor.
3. Cursor implements from that issue context, reading linked Scraplands docs/scripts first.
4. Cursor/Hermes links commits or PRs back to the issue.
5. Hermes closes the issue only after the fix is verified and published/live.

If Hermes needs to add more implementation detail, add it as a GitHub issue comment so the handoff stays attached to the canonical issue.

## Closure gate

Do not close a bug because code was written, committed, or linked. Close only when there is publish/live evidence, such as:

- Oz confirms the fix is published/live.
- The release/publish workflow clearly includes the fix.
- A publish batch maps the commit/PR to the issue and Oz asked Hermes to close resolved bugs.

Close comment should include issue/commit/PR evidence and validation notes.

## Skill/doc maintenance checklist

When future workflow docs mention local tasks, replace with GitHub language:

- `ai/tasks/active` → GitHub issue with `status:ready`
- `ai/tasks/testing` → GitHub issue/Project `In Progress` or `Needs Review`
- `ai/tasks/published` → closed GitHub issue with release evidence
- `ready_for_cursor` → issue is scoped and ready for Oz to copy into Cursor

Historical migration reports may mention `ai/tasks/` as source material; that is OK when clearly historical, not an active workflow instruction.
