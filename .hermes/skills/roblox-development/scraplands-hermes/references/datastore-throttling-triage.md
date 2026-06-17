# Scraplands DataStore Throttling Triage

Use this when Oz reports Roblox output like:

- `DataStore request was added to queue. If request queue fills, further requests will be dropped`
- `StandardWriteGameServerThrottled`
- `API: UpdateAsync, Data Store: PlayerData_v2`
- `DataService timed out waiting for in-flight lock ... reason=PlayerLeaving`
- `PlayerMoneyManager: force-leave money save FAILED`
- `SaveCoordinator: subsystem save FAILED`

## Interpretation

This is usually **server/write-budget and per-key queue pressure**, not a long-lived account/user-level cooldown. The user id in `Key = <userId>` identifies the player data key being hammered; it does not mean that user has exhausted a personal daily allowance.

Budgets replenish over time, but warnings continue while the current server keeps issuing writes faster than Roblox can drain them. In Studio/live server sessions, queued retries can keep warnings alive for seconds to minutes after the burst.

If warnings include `[DataService] commit threw ... ReplicatedStorage.Scripts.PlayerDataService:<line>: attempt to index function with 'traceback'`, treat the traceback crash as the primary incident before tuning write pressure. In Luau modules, a local helper named `debug` shadows the global `debug` library, so `debug.traceback()` indexes the helper function and crashes commits. Rename the helper to `debugLog` (or similar), update call sites, then retest in a fresh Studio server.

## First root-cause hypothesis to check

Look for duplicate leave-time writes to `PlayerData_v2` for the same player:

1. A subsystem force-save calls `DataService.saveLegacy(... PlayerLeaving)`.
2. `SaveCoordinator` then runs `DataServicePending` / other subsystems.
3. `SaveCoordinator` finally runs `PlayerDataV2` terminal save.
4. Cleanup callbacks call `PlayerDataService.onPlayerRemoving(player)`, which may perform another dirty save.

This creates multiple `UpdateAsync` calls for the same key during the exact moment Roblox is least tolerant: player leave/shutdown.

## Scraplands-specific pattern from the Money incident

`PlayerMoneyManager.savePlayerMoneyForceLeave()` should not perform its own DataStore commit if it can safely sync `Money.Value` into the live v2 session and let the canonical terminal `PlayerDataV2` save persist once.

Safe shape:

- cancel money debounce
- snapshot current `Money.Value` into active world/session data
- clear/remove only pending `money` from the DataService pending bucket if needed
- return success/failure for the snapshot step
- let `PlayerDataV2` remain the single terminal leave save

If `DataService` has a pending `{ money = ... }` bucket, simply removing `Money`'s explicit `saveLegacy` is not enough; `DataServicePending` may still flush that pending payload and cause an extra v2 write. Add/use a narrow API such as `removePendingPayloadKeys(player, { "money" })` rather than clearing unrelated pending fields or ops.

## Cleanup split

If `SaveCoordinator` already ran `PlayerDataV2.save`, then `onPlayerRemoved` should call a cleanup-only function, not a second save-capable `PlayerDataService.onPlayerRemoving(player)` path.

Preferred split:

- `PlayerDataService.onPlayerRemoving(player)` — fallback path that may save if not managed by SaveCoordinator.
- `PlayerDataService.cleanupPlayerSession(player)` — stop heartbeat, release lock, clear session/load state, no DataStore writes.

## How to answer Oz quickly

If he asks whether the warnings mean he capped his user-level allowance:

> No — this is almost certainly current server/request-budget + per-key queue pressure, not a personal daily user cooldown. The key is your player-data key. It will keep warning while this server has queued retries or keeps issuing writes; a fresh server after the fix should drop the warnings quickly.

## Validation checklist

After a fix:

1. Stop the current Studio play session/server.
2. Start a fresh session.
3. Join, perform one money-changing action, leave.
4. Confirm no `force-leave money save FAILED`.
5. Confirm no `timed out waiting for in-flight lock reason=PlayerLeaving`.
6. Confirm only one canonical terminal `PlayerData_v2` leave save path.

If warnings continue in a fresh session, audit high-frequency gameplay save paths next: smelts, rewards, gold nuggets, daily boosts, device edits, and legacy `saveLegacy` callers that still force full v2 saves too often.
