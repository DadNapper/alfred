# Roblox Creator Analytics access for Scraplands

Use this when Oz asks Hermes to read, monitor, or summarize Scraplands Roblox Analytics / Creator Hub metrics.

## Auth source

A dedicated read-only Roblox analytics account is authenticated on the VPS via:

```text
~/.hermes/secrets/roblox_analytics.env
ROBLOX_ROBLOSECURITY='<.ROBLOSECURITY cookie value>'
```

Treat the cookie as sensitive:
- never print it
- never paste it into Telegram
- never commit it
- keep file permissions `600`

If Oz provides a raw browser cookie dump, clean it on the VPS rather than in chat. A helper script may exist at:

```text
~/.hermes/scripts/clean_roblox_cookie.py
```

It extracts the `.ROBLOSECURITY` value from raw cookie text and writes `~/.hermes/secrets/roblox_analytics.env` without printing the cookie.

## Verified API pattern

Authenticated Creator Analytics data can be queried through Roblox's dashboard backend:

```text
POST https://apis.roblox.com/analytics-query-gateway/v1/metrics/resource/RESOURCE_TYPE_UNIVERSE/id/9056408258
```

Required request shape:

```json
{
  "resourceType": "RESOURCE_TYPE_UNIVERSE",
  "resourceId": "9056408258",
  "query": {
    "resourceType": "RESOURCE_TYPE_UNIVERSE",
    "resourceId": "9056408258",
    "metric": "DailyActiveUsers",
    "granularity": "METRIC_GRANULARITY_ONE_DAY",
    "startTime": "2026-06-01T00:00:00Z",
    "endTime": "2026-06-16T00:00:00Z",
    "limit": 1000
  }
}
```

Important enum values discovered:
- resource type: `RESOURCE_TYPE_UNIVERSE` (not `Universe`)
- daily granularity: `METRIC_GRANULARITY_ONE_DAY` (not `OneDay`)

CSRF handling:
1. First POST may return `403` with `X-CSRF-TOKEN` / `x-csrf-token`.
2. Retry the same POST with header `x-csrf-token: <token>`.

Useful verified metrics:
- `DailyActiveUsers`
- `Visits`
- `ConcurrentPlayers`
- `AverageSessionLengthMinutes`
- `TotalPlayTimeHours`
- `D1Retention`
- `D7Retention`
- `ForwardD7Retention`
- `DailyRevenue`
- `AverageRevenuePerUser`
- `AverageRevenuePerPayingUser`
- `PayingUsers`
- `PayingUsersCVR`

Metrics that returned not found during setup:
- `PayerConversionRate`
- `PlaytimeMinutes`
- `QualifiedPlayThroughRate`

## Monitor script

The current authenticated monitor script lives at:

```text
~/.hermes/scripts/scraplands_analytics_monitor.py
```

It combines:
- public Roblox endpoints: CCU, visits, favorites, votes, server FPS/ping/capacity
- Creator Analytics: DAU, visits, avg CCU, session length, playtime, D1/D7 retention, revenue, ARPU, paying users, payer conversion
- a concise executive-analysis paragraph

The scheduled cron job replacing the old public-only monitor is named:

```text
Scraplands analytics monitor
```

It runs script-only (`no_agent=true`) every 12 hours and delivers stdout verbatim.

## Output preference

For Oz, keep monitor output readable and skimmable:
- use Markdown bullets, not dense paragraph lines
- include a short executive-analysis paragraph
- compare Creator Analytics metrics to a recent baseline
- call out current public CCU/server health separately from latest complete-day analytics

## Pitfalls

- Creator Analytics is lagged / daily; prefer latest complete day and avoid overreacting to same-day partials.
- The dashboard HTML can load without direct browser auth while API auth works via cookie; prefer the API for monitor automation.
- Do not reintroduce DataStore-backed analytics to solve monitoring gaps. Scraplands analytics must not compete with player-data saves.
- Some metrics have short retention windows; do not request ranges longer than Roblox allows for that metric.
