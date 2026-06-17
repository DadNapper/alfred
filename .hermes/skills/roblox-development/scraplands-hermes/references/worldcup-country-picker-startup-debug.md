# World Cup country picker startup debugging

Use this when the World Cup / Soccer Cup intro dialog or country/team picker does not appear on join after the event flag is enabled.

## Durable lesson

Do not conflate these three states:

- **Global event enabled**: Remote/Experience config says WorldCup is live.
- **Event access/unlocked**: player may see or use event systems; this can include tester bypasses and private-server overrides.
- **Country/team selection complete**: player has a saved or replicated `selectedCountryCode` / `WorldCupCountryCode`.

The country picker should be skipped only when country selection is actually complete or the event is globally off. It should not be skipped merely because `WorldCupIntroGate.isUnlocked()` returns true.

## Known pitfall from v520ed5ce follow-up

A fix can still fail if `SelectCountryGuiClient.presentWorldCupIntro()` exits on `WorldCupIntroGate.isUnlocked()`:

```lua
if selectionRuntimeDisabled or WorldCupIntroGate.isUnlocked() then
    return
end
```

That is wrong for picker presentation because `isUnlocked()` can return true for tester accounts or general event access. Tester bypass should unlock testing access, not mark onboarding/team selection complete.

## Investigation checklist

1. Search the country picker path for `isUnlocked()`, `isUnlockTimerComplete()`, `selectedCountryCode`, `WorldCupCountryCode`, and `selectionRuntimeDisabled`.
2. Verify the picker uses an explicit country-selected check before skipping dialog presentation.
3. Verify fresh first-time players after global event enable are not blocked forever behind pet-trial timing if the intended product behavior is “show picker at game start.”
4. Keep gameplay rewards/discovery/trading gated by selected country on the server; do not weaken `canDiscoverSoccerBallsForPlayer` just to make UI appear.
5. Validate four cases:
   - Tester with no selected country: join → loading ends → picker opens.
   - Non-tester fresh account with global flag on: join → loading ends → picker opens.
   - Returning player with selected country: picker does not open; event HUD/decor unlocks.
   - Global flag off: picker does not open.

## Cursor prompt shape

Tell Cursor:

```text
Fix World Cup country picker startup. Do not use WorldCupIntroGate.isUnlocked() to decide whether the picker should show; that helper includes tester/event access bypasses. For intro presentation, skip only if selectedCountryCode / WorldCupCountryCode is present or the runtime was explicitly disabled after completed selection. If global WorldCup is enabled and no country is selected, show SelectCountryGui after loading. Preserve server reward/discovery/trading gating by selected country.
```
