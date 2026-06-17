# World Cup / Seasonal Live-Ops Patterns

Session-derived patterns for Scraplands seasonal events, especially World Cup/Soccer Cup rollout and testing.

## Roblox Experience Events vs game logic

Roblox Experience Events are promotion/discovery/reminder surfaces. They do not automatically enable gameplay. Scraplands gameplay must remain controlled by server-side config/code:

- event spawns
- rewards/stickers
- shops/booths
- collection permissions
- onboarding/team selection
- economy effects

Roblox SocialService event metadata can be useful for UI copy/timing, but it should not be the authoritative gameplay switch for near-term live ops.

## Avoid tester/community server-wide leaks

Do **not** implement tester/community rollout as:

```lua
for _, player in Players:GetPlayers() do
    if isTester(player.UserId) then
        return true
    end
end
```

That makes one eligible player turn on event mode for every public-server player. For public mixed servers, use explicit per-player eligibility:

```lua
WorldCupEventConfig.isEnabledForPlayer(player)
```

Server authorization paths for collection/rewards/trading must require an explicit `player` and reject non-eligible players. Client visibility/UI can be friendlier, but server reward paths are authoritative.

## Private-server event testing pattern

For reliable full-server event testing, prefer an approved private-server-owner override over per-player tester mode:

```lua
return game.PrivateServerId ~= ""
    and game.PrivateServerOwnerId ~= 0
    and TesterAccounts.isWorldCupTestPrivateServerOwner(game.PrivateServerOwnerId)
```

Use this to enable the whole event in an isolated private server while the public Experience Config flag remains false. Everyone invited into that private server can test full server-level systems (booth, balls, graffiti, team selection), but public matchmaking is not affected.

This is better than per-player gating when testing world/server-level systems, because shared physical spawns and replicated flags behave like launch without leaking to public servers.

## Country/team picker pitfall

Do not treat “World Cup unlocked” as equivalent to “country selection complete.” Tester/private-server bypasses may unlock access while the player still needs the required country picker. Suppress the picker only when the actual event state has a selected country, e.g. `selectedCountryCode` is present.

If a GUI may not be cloned/ready at boot, retry presentation and avoid marking intro presentation complete until the GUI is actually shown or country selection is already complete.

## Ball discovery pacing pattern

For powerful players, raw mining throughput can overwhelm effort thresholds. Prefer **soft progression-aligned pacing** over hard bans or “punish powerful players” scaling:

- first onboarding ball remains fast/guaranteed
- normal balls use existing effort threshold
- after a ball award, require a minimum interval before another award
- if effort reaches threshold during cooldown, hold progress at threshold and award on the next qualifying action after cooldown
- old worlds should still be eligible, but less efficient for advanced players
- passive/auto miner contribution should be reduced separately from world relevance

This keeps upgrades feeling good while preventing maxed players from printing event rewards at one ball per minute or optimally farming World 1 after unlocking later worlds.

Current implemented reference values from the World Cup session:

- `WorldCupEventConfig.MinSecondsBetweenBallAwards = 180`
- store `discovery.lastSoccerBallAwardedAt`
- helper: `WorldCupEventConfig.getRemainingBallAwardCooldown(discovery, nowUnix)`

Recommended next-step pacing model for advanced-player old-world farming:

- world relevance multiplier based on source world vs highest unlocked world:
  - highest unlocked world: `1.00x`
  - one world behind: `0.50x`
  - two+ worlds behind: `0.20x`
  - unknown source world: safe fallback, usually `1.00x` to avoid accidental breakage
- source multiplier:
  - manual/active collection: `1.00x`
  - passive miner / auto-collect: about `0.20x`
  - dev command/testing: `1.00x`
  - first-ball onboarding guarantee: unaffected
- formula: `finalEventEffort = baseEffort × tierMultiplier × sourceMultiplier × worldRelevanceMultiplier`

Implementation anchors discovered in repo:

- `Extractor:getMineSpawnContext()` already returns `WorldId`.
- Extractor collection flow adds `DeviceTier`, `Depth`, and `LevelName` before `EventDiscoveryService.OnMineCell(...)`.
- `WorldManager.getHighestUnlockedWorldId(data)` and `WorldManager.getWorldConfig(worldId).order` exist for comparing source vs highest unlocked world.
- Prefer config/helper functions in `WorldCupEventConfig`; avoid new persistent fields for this runtime pacing change.

## Launch/restart operational note

Config/code fixes do not automatically rewrite old live servers. If an event leak matters, publish/sync the fixed version and shut down active servers so players rejoin fresh patched servers. If the leak is harmless, it is usually acceptable to let old servers age out naturally.
