# Latest feedback → GitHub issue pass (2026-06-21)

Use this as a compact example for small post-publish feedback batches where only a few `status = new` rows exist.

## Input snapshot

- Google Sheets status counts before triage: `fixed = 138`, `wont_fix = 269`, `triaged = 383`, `new = 2`.
- New rows:
  - Row 792 — Bug — v6747 — PC — “Collector drone never launched despite multiple nuggets and open spaces to put them.”
  - Row 793 — Feedback — v6747 — “eee”

## Actions taken

1. Snapshot all feedback locally before mutating the sheet.
2. Search GitHub for duplicates using system/root-cause terms (`collector`, `drone`, `gold nugget`, `nugget drone`, `gold drone`).
3. Create one root-cause issue for the actionable row instead of treating it as a one-off report:
   - GitHub #51: `Bug: Collector drone stays idle despite nuggets and open storage`
   - Labels: `priority:p1`, `status:ready`, `type:bug`, `source:player-feedback`, `area:automation`, `area:drones`, `area:gold`, `model:premium`
   - Body included row/version evidence, likely files, investigation plan, acceptance checks, constraints, and `## Model\nModel: premium`.
4. Update sheet rows:
   - Row 792 → `triaged`, notes link GitHub #51.
   - Row 793 → `wont_fix`, notes `Non-actionable feedback`.
5. Verify status counts after write: `fixed = 138`, `wont_fix = 270`, `triaged = 384`, `new = 0`.
6. Write repo triage summary at `ai/triage/feedback_triage_2026_06_21.md`.

## Durable lessons

- For a small new-row batch, still do the full loop: snapshot → duplicate search → create/update GitHub → update sheet → verify counts/new rows → write concise triage summary.
- Non-actionable single-token rows should be marked `wont_fix` with a direct note; do not spend investigation time.
- If GitHub Projects v2 status movement is unavailable or not configured, apply fallback `status:*` labels and explicitly state that Project status was not moved. Do not block issue creation on Projects access.
- When creating a Cursor-ready player-feedback issue, include implementation starting points from code/docs and an explicit model hint/label; GitHub issue body is the canonical handoff.
