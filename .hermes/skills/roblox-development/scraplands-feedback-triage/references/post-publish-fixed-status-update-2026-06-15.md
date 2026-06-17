# Post-publish fixed-status update — 2026-06-15

Session pattern captured for future Scraplands feedback-sheet updates after Oz publishes fixes.

## Trigger

Oz says recently published fixes should be reflected in the Google feedback triage sheet.

## What worked

1. Load `scraplands-git-workflow`, `scraplands-feedback-triage`, and relevant Scraplands orchestration context.
2. Pull latest through the project workflow (`./shellScripts/update.sh` from `~/projects/scraplands`), not ad-hoc git pull.
3. Inspect recent published task files and commits:
   - `git log --oneline --decorate -n 12 -- ai/tasks/published ServerScriptService StarterPlayerScripts ReplicatedStorage`
   - `git log --name-status --oneline -n 8 -- ai/tasks/published`
   - Read matching `ai/tasks/published/*.md` files for evidence rows and shipped-change scope.
4. Snapshot the sheet before mutating it:
   - Save JSON under `/home/alfred/.hermes/tmp/scraplands_feedback_snapshots/`.
5. Use `/home/alfred/.hermes/integrations/google_sheets.py` with `PYTHONPATH=/home/alfred/.hermes/integrations`.
6. Batch-update only `status` and `notes` for rows that clearly match the published task scope.
7. Re-read the sheet and verify every touched row is `fixed` with non-empty notes; report status-count changes and touched clusters.

## Note style that worked

Use concise cluster notes with commit IDs and shipped mechanism, e.g.:

```text
Fixed: ore collect/sell/backpack stuck-state cluster. Published in 81fcecc5 (InventoryReady gate before PickOre, device-aware PickOre validation, AddOre prevalidated world path, pickaxe batch flush on death/unequip/respawn, AccessTrader sell-state reset). Covers mined ores not entering backpack, no-ore-after-minutes, death/reset requiring rejoin before selling, and storage/tank desync reports included in the P0 task.
```

If an existing note starts with a translation block, preserve it and append the fixed note after a blank line.

## Example clusters from this session

- Money / sell proceeds / rollback / world-scoped balance contamination → commit `665c4be4`, task `p0-money-currency-rollback`.
- Ore collect / backpack / sell stuck-state → commit `81fcecc5`, task `p0-ore-sell-backpack-stuck`.
- Pet follow / wagon / Shiba selling-stuck symptoms → commits `5957fd6c` / `f62da3e6`.

## Pitfalls

- Do not mark broad persistence/miner-loss rows fixed unless the published task directly addresses them; keep high-risk progress-loss reports triaged when the match is not exact.
- Do not rely only on commit titles; read published task evidence rows and implementation notes.
- Do not update repo files for sheet-only triage unless Oz asks; keep git status clean.
