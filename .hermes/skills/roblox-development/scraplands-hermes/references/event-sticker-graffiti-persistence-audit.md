# Event Sticker / Graffiti Persistence Audit

Use when Oz asks for a sanity check around World Cup stickers, sticker packs/trades, soccer-ball redemption, graffiti/spray-can placement, or similar high-volume event reward paths.

## Why this matters

Event launch traffic can turn small persistence mistakes into DataStore pressure or player-visible progress loss. Solo private-server testing can catch issues cheaply before multi-player publish.

## Fast audit targets

Inspect server-authoritative paths first:

- `ServerScriptService/Scripts/EventDiscoveryService.luau` — soccer ball discovery/redeem → sticker grants.
- `ServerScriptService/Scripts/WorldCupStickerPackService.luau` — sticker pack grants/purchases.
- `ServerScriptService/Scripts/WorldCupStickerTradeService.luau` — player-to-player sticker trades and trade costs.
- `ServerScriptService/Scripts/GraffitiPlacementService.luau` — sticker placement/washoff/repaint, money charge, decals, and final save.
- `ServerScriptService/Scripts/WorldCupSoccerBallSellHandler.legacy.luau` — physical ball booth redemption.
- `ReplicatedStorage/Scripts/Events/WorldCupStickersConfig.luau` and `WorldCupStickerRoll.luau` — inventory normalization, unseen markers, duplicate handling.
- Persistence infrastructure: `PlayerDataService.luau`, `DataService.luau`, `Readmes/datastore/data_service.md`.

## Pitfalls to check

1. **Diagnostic shadowing**
   - If a module calls `debug.traceback()`, ensure the same scope does not define `local function debug`, `local debug = ...`, or `debug = function`.
   - Rename local helpers to `debugLog` / `logDebug` if needed.

2. **All-or-nothing sticker trade semantics**
   - Snapshot and rollback must cover sticker inventory, trade limits, live `Money`, and v2 `economy.money`.
   - Watch for cost application via `PlayerDataService.updateActiveWorldField(player, "economy.money", newBalance)` before both players' event states are persisted.
   - If persistence fails after cost application, restore both live values and v2 session state, or restructure so mutation occurs after all validations.

3. **Graffiti charge/decal/state ordering**
   - Paid repaint/washoff often charges money before decal/state persistence is fully proven.
   - If final `commitGraffitiPersistence` fails, confirm money, decal visuals, and in-memory graffiti state are rollback-safe or acceptably retried.
   - Free tutorial spray is lower risk but still must not corrupt saved state.

4. **Save pressure from visible customization spam**
   - Sticker placement/washoff may call `PlayerDataService.savePlayerData(player)` directly to make visible state durable.
   - Confirm there is a server-side cooldown/debounce, UI guard, or explicit reason immediate save is necessary. Avoid adding ad-hoc DataStore calls.

5. **Normalization duplicate branches**
   - Selene `if_same_then_else` often flags refactor leftovers. In event state normalization, combine equivalent cleanup branches without changing behavior.

## Targeted validation command

Run Selene on the touched event and persistence files:

```bash
selene \
  ServerScriptService/Scripts/EventDiscoveryService.luau \
  ServerScriptService/Scripts/WorldCupStickerPackService.luau \
  ServerScriptService/Scripts/WorldCupStickerTradeService.luau \
  ServerScriptService/Scripts/GraffitiPlacementService.luau \
  ServerScriptService/Scripts/WorldCupSoccerBallSellHandler.legacy.luau \
  ReplicatedStorage/Scripts/Events/WorldCupStickersConfig.luau \
  ReplicatedStorage/Scripts/Events/WorldCupStickerRoll.luau \
  ReplicatedStorage/Scripts/PlayerDataService.luau \
  ReplicatedStorage/Scripts/DataService.luau
```

Expected: no parse errors, no new persistence-related errors. Existing legacy `_G` warnings can be noted without broadening scope unless they are part of the bug.

## Studio smoke test

1. Fresh private server.
2. Redeem several soccer balls quickly.
3. Confirm sticker inventory/new indicators update and persist after rejoin.
4. Test duplicate and new sticker cases.
5. Place stickers on each unlocked host: house, car, silo, bot, drone.
6. Test repaint/washoff with enough coins and insufficient coins.
7. Rejoin and verify money, graffiti, and sticker inventory are consistent.
8. Confirm no `[DataService] commit threw`, no `debug.traceback` errors, and no DataStore queue warnings during normal use.
