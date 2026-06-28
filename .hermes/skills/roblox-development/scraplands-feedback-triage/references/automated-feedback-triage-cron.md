# Automated feedback triage cron pattern

Use when Oz wants Scraplands feedback triage to run automatically instead of only on demand.

## Recommended cadence

| Cadence | Purpose |
|---|---|
| Daily morning | Default: triage new Google Sheet rows, update GitHub issues, write/push a concise `ai/triage` summary. |
| Every 6h for 24–48h after major publish | Temporary high-frequency regression watch. Prefer a separate temporary cron or manual runs, then remove/pause. |
| On demand | Keep supporting Oz’s “triage latest” requests for launch/support moments. |
| Weekly cleanup | Review duplicates, stale triaged issues, and closed/fixed rows; do not mix this with the daily new-row pass unless asked. |

## Cron job shape

Use an LLM-driven cron job, not `no_agent=True`, because the task requires duplicate search, classification judgment, GitHub issue creation/update, and safe git decisions.

Recommended schedule:

```text
0 15 * * *
```

This is 15:00 UTC, roughly 8am Pacific during PDT.

Recommended skills:

```text
scraplands-feedback-triage
github-operations
scraplands-git-workflow
scraplands-telegram-topics
```

Recommended toolsets:

```text
terminal,file,web
```

Recommended workdir:

```text
/home/alfred/projects/scraplands
```

## Required behavior

1. Read all `status = new` Sheet rows across Bug/Feedback/Idea.
2. If no new rows exist, do not edit files, do not commit, and do not push. Deliver only a concise no-op summary plus status counts.
3. If rows exist:
   - Snapshot/read rows before mutating.
   - Search GitHub by root-cause/system terms before creating issues.
   - Create/update one GitHub issue per actionable root-cause class.
   - Update Sheet status/notes with canonical GitHub URLs or non-actionable/duplicate rationale.
   - Re-read and verify new count, status counts, and updated row notes.
   - Write/update `ai/triage/feedback_triage_<YYYY-MM-DD>_auto.md`.
4. Commit and push intended triage summary files to `main` as part of the same triage task; do not leave completed triage summaries sitting uncommitted for Oz to discover later.
5. Commit/push only if the working tree is clean except intended triage summary files.
6. If unrelated dirty files exist, do not commit/push; report the blocker and leave triage side effects visible in Sheets/GitHub.

## Git safety

Before committing, inspect:

```bash
git status --short
git diff --stat
git diff --name-only
```

Remove generated artifacts such as:

```text
__pycache__/
*.pyc
```

Only ship intended `ai/triage` summary files. Verify remote main after push before claiming success.

## Project v2 pitfall

Project v2 movement may fail if `SCRAPLANDS_PROJECT_NUMBER` / Project field env config is unavailable. Do not block issue creation on this. Apply fallback `status:*` labels and report that Project movement was unavailable.

## Final report shape

Keep Oz-facing output terse:

```text
Model: <model>
Processed: <N> new rows
GitHub: #<issue> ...
Sheets: new_count <N>, status_counts {...}
Git: <commit SHA> pushed / or blocker
```
