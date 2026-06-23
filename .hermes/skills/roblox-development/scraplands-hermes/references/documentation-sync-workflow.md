# Scraplands documentation sync workflow

Use this when Oz says docs/readmes are stale after a recent feature change, or asks to understand a commit and update all references.

## Trigger examples

- "Look up the git commit, understand what we implemented, and update all docs/scripts referencing old behavior."
- "Create a consistent readme for this system."
- "We changed how X works; docs still describe the old logic."

## Workflow

1. **Start from repo context.** Read `AGENTS.md`, `ai/README.md`, and relevant workflow/readme files as usual.
2. **Find the behavior-changing commit.** Use `git log --all --grep='<feature terms>' --regexp-ignore-case` and inspect the commit with `git show --stat` plus focused diffs for the system scripts.
3. **Identify source of truth in code.** For live-events/modifiers, look for shared config modules, replicated attributes, server-authoritative reward paths, and client display paths. Document the authoritative helpers/attributes, not a paraphrase from old docs.
4. **Search stale references broadly.** Search docs and scripts separately for old copy, hardcoded values, and old assumptions. For Gold Rush-style modifiers, search both player-facing phrases (`+50%`, `50%`, `1.5x`) and implementation names (`GoldRushValueMultiplier`, etc.).
5. **Create or update the canonical doc.** Put durable feature docs under the appropriate `Readmes/<domain>/` folder, then link them from:
   - the domain index (`Readmes/events/README.md`, progression index, etc.)
   - `ai/<domain>.md` routing docs when present
   - adjacent system docs that future agents will open first
6. **Fix stale current behavior, preserve history carefully.** It is fine to update old changelog wording when it currently misleads; mark it as a historical first implementation and point to the later superseding behavior instead of pretending the old change never happened.
7. **Patch code only for documentation/copy correctness.** If a script has stale fallback/player-facing copy that contradicts current config-driven behavior, replace it with config/attribute-driven copy or a neutral placeholder. Do not broaden into feature implementation unless Oz asked.
8. **Add concise changelog entries.** Use existing Scraplands README style with Date, Summary, Reason, Files, Author, Reviewed, Model.
9. **Verify.** Run `git diff --check`, run available Luau lint/parse checks on touched scripts, and search again for stale phrases. Treat remaining matches as acceptable only if they are intentional current variants/localization strings or explicitly historical changelog context.
10. **Report uncommitted/unrelated files.** Do not commit unless Oz explicitly asks. Call out unrelated dirty files separately.

## Gold Rush-specific notes from the 2026-06-21 doc sync

The implementation commit was `cfef2b73 [Alfred] Add Gold Rush bonus variants`.

Current Gold Rush is variant-based, not always a fixed `+50%` sell-value event. The canonical doc created for this is `Readmes/events/gold_rush.md`.

Authoritative pieces:

- `ReplicatedStorage/Scripts/GoldRushConfig.luau` defines variants and helpers.
- `HubGenerator.legacy.luau` rolls/applies the selected variant and replicates Store_3 attributes.
- `GoldBlockSellingHandler.legacy.luau` applies `GoldRushValueMultiplier` to Gold Block/Nugget sale value.
- `Extractor.luau` applies `GoldRushNuggetMultiplier` to nugget odds.
- `FurnaceStateManager.legacy.luau` and `PlayerInteraction.local.luau` apply/preview `GoldRushFurnaceSpeedMultiplier`.
- `GoldRushStoreStyling.local.luau` should show selected variant title/description from `Store_3`, not hardcode `+50%` as the default Gold Rush copy.

Intentional remaining `+50%` references are allowed for the `gold_fever` variant and localization/manifest entries for that variant. Stale references are wording that says or implies the entire Gold Rush feature is always/only/fixed `+50%` or only a sale-value event.

## Pitfalls

- Do not treat a missing CLI such as `gh` as durable project knowledge; use the repo helper if available, but do not encode environment failure as a rule.
- Do not mass-rewrite historical changelogs unless they actively mislead current readers. Prefer one clarifying parenthetical or a superseded-by note.
- Avoid broad `50%` cleanup that removes legitimate gamepass, Lucky Miner, localization, or variant-specific references.
