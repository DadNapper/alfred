# Feedback → GitHub Issues Pattern (2026-06-17)

Use when a small batch of fresh Google Sheet feedback has already been triaged and Oz asks to create tickets/issues and ship them.

## Pattern

1. Start from the triaged sheet rows and existing GitHub issues; do not re-triage from scratch.
2. Search GitHub before creating anything:
   - symptoms / system keywords
   - likely root cause
   - related shipped issue titles
3. Create or update one GitHub issue per actionable root-cause class, including non-P0 QoL/UX work if Oz asked for the whole triaged batch.
4. Use labels:
   - `priority:p0` for data loss, high-value item loss, core-loop inventory/economy regressions, or multi-system race bugs
   - `priority:p1` for session-ending UI/control softlocks without confirmed data loss
   - `priority:p2` for QoL or visual/progression clarity issues
   - `type:bug`, `source:player-feedback`, relevant `area:*`, and `status:ready` or `status:backlog`
5. Issue structure:
   - Goal / Summary
   - Why priority
   - Player evidence with row/version references
   - Hypothesis / product direction
   - Non-negotiable constraints
   - Required readings / Cursor attachments
   - likely scripts/files to inspect
   - investigation plan
   - acceptance criteria
   - out-of-scope guardrails
6. Update Google Sheet status/notes with the GitHub issue URL when appropriate.
7. If Oz wants Cursor to fix it, default handoff is: copy the GitHub issue URL/body into Cursor.
8. Add extra implementation detail as GitHub issue comments, not local `ai/tasks/` files.

## Concrete split from the session

Rows `767`–`768` became one P0 issue: gold furnace/conveyor/carry jam regression.

Row `769` became one P0 issue: pickaxe + pet nearby inventory not added regression.

Row `766` became one P1 issue: respawn menus break and require rejoin.

Rows `765` and `770` became P2 issues: stable pickaxe hotbar slot and Meadows research maxed/star display mismatch.

## Pitfall

Do not create only the P0 issues when Oz asks for the whole triaged batch. Include actionable P1/P2 issues too, but make their priority/model-risk clear so Cursor starts with the P0s.
