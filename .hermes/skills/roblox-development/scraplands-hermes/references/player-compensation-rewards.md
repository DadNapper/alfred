# Player Compensation Rewards

Use this when Oz asks to reward players for bug reports, apology grants, lost progress/resources, in-game money loss, or wasted Robux.

## Eligibility rule

Do **not** add every bug reporter to compensation lists. Filter to players who likely experienced direct loss or wasted value:

- lost progress / rollback after rejoin
- lost miners, drills, tools, inventory, ores, gold, scrap, portals, or unlocks
- in-game money/currency removed, rolled back, not credited, or wrongly spent
- Robux purchase charged but not fulfilled, wasted, or no-op
- resource-generation bugs where the player lost usable value or had to restart and lose inventory

Usually exclude:

- lag/FPS-only reports
- UI stuck/missing buttons without resource loss
- movement/control lock without lost value
- suggestions/ideas/general balance complaints
- exploit reports that did not harm the reporter
- tutorial/text/layout issues
- spam/test/non-actionable rows

## Implementation guardrail

For player-specific apology/compensation rewards in Scraplands, prefer `PlayerSpecificCommunications.legacy.luau` and keep writes v2-first:

1. Dedupe UserIds before adding them to `FEEDBACK_BUG_APOLOGY_USER_IDS`.
2. Grant compensation into the player's **highest/latest unlocked world** currency bucket, not necessarily the currently active world.
   - Resolve with `WorldManager.getHighestUnlockedWorldId(data)`.
   - Write via `PlayerDataService.updateWorldField(player, rewardWorldId, "economy.money", newBalance)`.
3. Resolve player-facing currency copy with `CurrencyLabelResolver`:
   - `CurrencyLabelResolver.getCurrencyLabelForWorld(rewardWorldId)`.
   - Use a `{currencyLabel}` token in notification source text/localization.
4. Persist the one-time shown/claimed flag in the same successful save path as the reward when possible, so the player is not marked rewarded before the grant actually saves.
5. If the rewarded world is also the active world, update the runtime `Money` IntValue after the v2 save succeeds so the HUD/InventoryToast reflects the new balance.
6. Update localization source and the UX/localization manifest whenever changing player-facing copy.

## Verification checklist

- Count new added users and total eligible users.
- Confirm zero duplicate UserIds.
- Run targeted Selene on touched Luau scripts.
- Verify the localization source row contains the same source string and tokens used by code.
- Remind Oz to Script Sync changed server scripts into Studio before publishing.
