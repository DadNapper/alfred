# Post-publish fixed-status update — GitHub workflow

Use when Oz says recently published fixes should be reflected in GitHub and the Google feedback triage sheet.

## Trigger

Oz says a fix is published/live, or asks Hermes to close/update bugs after a publish.

## Workflow

1. Load `scraplands-git-workflow`, `scraplands-feedback-triage`, and relevant Scraplands orchestration context.
2. Pull latest through the project workflow (`./shellScripts/update.sh` from `~/projects/scraplands`), not ad-hoc git pull.
3. Inspect recent commits/PRs and linked GitHub issues:
   - `git log --oneline --decorate -n 12 -- ServerScriptService StarterPlayerScripts ReplicatedStorage Readmes ai`
   - GitHub issue links in commit/PR bodies (`Fixes #...`, `Closes #...`) or issue comments
   - issue body/comments for evidence rows and shipped-change scope
4. Snapshot the sheet before mutating it when sheet updates are involved:
   - Save JSON under `/home/alfred/.hermes/tmp/scraplands_feedback_snapshots/`.
5. Use `/home/alfred/.hermes/integrations/google_sheets.py` with `PYTHONPATH=/home/alfred/.hermes/integrations`.
6. For each issue that is truly published:
   - comment with publish evidence and validation notes
   - move Project Status to Done / fallback `status:done` when Project API scopes allow
   - close the GitHub issue
7. Batch-update only `status` and `notes` for feedback rows that clearly match the published issue scope.
8. Re-read GitHub/search output and the sheet; verify touched rows are `fixed`/`released` as appropriate with non-empty notes.

## Note style that works

Use concise cluster notes with issue numbers, commit IDs, and shipped mechanism, e.g.:

```text
Fixed: ore collect/sell/backpack stuck-state cluster. Published via GitHub issue #123 and commit 81fcecc5 (InventoryReady gate before PickOre, device-aware PickOre validation, AddOre prevalidated world path, pickaxe batch flush on death/unequip/respawn, AccessTrader sell-state reset). Covers mined ores not entering backpack, no-ore-after-minutes, death/reset requiring rejoin before selling, and storage/tank desync reports included in the issue.
```

If an existing note starts with a translation block, preserve it and append the fixed note after a blank line.

## Pitfalls

- Do not close a GitHub issue just because code was written; close only after Oz confirms it is published/live or release evidence proves it.
- Do not mark broad persistence/miner-loss rows fixed unless the published issue directly addresses them; keep high-risk progress-loss reports triaged when the match is not exact.
- Do not rely only on commit titles; read issue evidence and implementation notes.
- Do not update repo files for sheet-only triage unless Oz asks; keep git status clean.
