#!/usr/bin/env python3
"""Scraplands Roblox analytics monitor.

Combines public Roblox endpoints with authenticated Creator Analytics API data.
Requires ~/.hermes/secrets/roblox_analytics.env containing ROBLOX_ROBLOSECURITY.
"""
from __future__ import annotations

import json
import os
import re
import statistics
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

UNIVERSE_ID = 9056408258
PLACE_ID = 106937996439556
STATE_PATH = Path(os.path.expanduser("~/.hermes/state/scraplands_analytics_monitor.json"))
SECRET_PATH = Path(os.path.expanduser("~/.hermes/secrets/roblox_analytics.env"))
TIMEOUT = 30
ANALYTICS_URL = (
    "https://apis.roblox.com/analytics-query-gateway/v1/metrics/"
    f"resource/RESOURCE_TYPE_UNIVERSE/id/{UNIVERSE_ID}"
)

CORE_METRICS = {
    "dau": "DailyActiveUsers",
    "visits": "Visits",
    "avg_ccu": "ConcurrentPlayers",
    "avg_session_min": "AverageSessionLengthMinutes",
    "playtime_hours": "TotalPlayTimeHours",
    "d1_retention": "D1Retention",
    "d7_retention": "D7Retention",
    "forward_d7_retention": "ForwardD7Retention",
    "revenue_robux": "DailyRevenue",
    "arpu": "AverageRevenuePerUser",
    "arppu": "AverageRevenuePerPayingUser",
    "paying_users": "PayingUsers",
    "payer_cvr": "PayingUsersCVR",
}


def read_cookie() -> str:
    try:
        text = SECRET_PATH.read_text()
    except FileNotFoundError:
        raise RuntimeError(f"Missing Roblox analytics cookie file: {SECRET_PATH}")
    match = re.search(r"^ROBLOX_ROBLOSECURITY=(['\"]?)(.*)\1\s*$", text.strip(), re.M)
    if not match:
        raise RuntimeError("ROBLOX_ROBLOSECURITY not found in cookie file")
    cookie = match.group(2).strip()
    if len(cookie) < 200:
        raise RuntimeError("ROBLOX_ROBLOSECURITY looks too short")
    return cookie


def fetch_json(url: str, headers: dict[str, str] | None = None, data: dict[str, Any] | None = None) -> dict[str, Any]:
    body = json.dumps(data).encode("utf-8") if data is not None else None
    request_headers = {
        "User-Agent": "HermesScraplandsAnalytics/1.0",
        "Accept": "application/json",
    }
    if data is not None:
        request_headers["Content-Type"] = "application/json"
    if headers:
        request_headers.update(headers)
    req = urllib.request.Request(url, data=body, headers=request_headers, method="POST" if data is not None else "GET")
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        charset = resp.headers.get_content_charset() or "utf-8"
        return json.loads(resp.read().decode(charset))


def analytics_post(cookie: str, payload: dict[str, Any], csrf: str | None = None) -> tuple[dict[str, Any], str | None]:
    headers = {
        "Cookie": f".ROBLOSECURITY={cookie}",
        "Origin": "https://create.roblox.com",
        "Referer": "https://create.roblox.com/",
        "User-Agent": "Mozilla/5.0 HermesScraplandsAnalytics/1.0",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    if csrf:
        headers["x-csrf-token"] = csrf
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(ANALYTICS_URL, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return json.loads(resp.read().decode("utf-8")), csrf
    except urllib.error.HTTPError as exc:
        token = exc.headers.get("x-csrf-token") or exc.headers.get("X-CSRF-TOKEN")
        if exc.code == 403 and token and not csrf:
            return analytics_post(cookie, payload, token)
        detail = exc.read().decode("utf-8", "replace")[:500]
        raise RuntimeError(f"Creator Analytics request failed HTTP {exc.code}: {detail}") from exc


def query_metric(cookie: str, metric: str, start: datetime, end: datetime) -> list[dict[str, Any]]:
    payload = {
        "resourceType": "RESOURCE_TYPE_UNIVERSE",
        "resourceId": str(UNIVERSE_ID),
        "query": {
            "resourceType": "RESOURCE_TYPE_UNIVERSE",
            "resourceId": str(UNIVERSE_ID),
            "metric": metric,
            "granularity": "METRIC_GRANULARITY_ONE_DAY",
            "startTime": start.isoformat().replace("+00:00", "Z"),
            "endTime": end.isoformat().replace("+00:00", "Z"),
            "limit": 1000,
        },
    }
    response, _csrf = analytics_post(cookie, payload)
    values = response.get("operation", {}).get("queryResult", {}).get("values", [])
    if not values:
        return []
    return values[0].get("dataPoints", []) or []


def fetch_public() -> dict[str, Any]:
    game = fetch_json(f"https://games.roblox.com/v1/games?universeIds={UNIVERSE_ID}")["data"][0]
    votes = fetch_json(f"https://games.roblox.com/v1/games/votes?universeIds={UNIVERSE_ID}")["data"][0]
    servers = fetch_json(f"https://games.roblox.com/v1/games/{PLACE_ID}/servers/Public?sortOrder=Desc&limit=100")
    rows = servers.get("data", [])
    pings = [float(row.get("ping")) for row in rows if isinstance(row.get("ping"), (int, float))]
    fps_values = [float(row.get("fps")) for row in rows if isinstance(row.get("fps"), (int, float))]
    up = int(votes.get("upVotes") or 0)
    down = int(votes.get("downVotes") or 0)
    return {
        "name": game.get("name"),
        "playing": int(game.get("playing") or 0),
        "visits": int(game.get("visits") or 0),
        "favorites": int(game.get("favoritedCount") or 0),
        "up_votes": up,
        "down_votes": down,
        "like_ratio": (up / (up + down)) * 100 if (up + down) else None,
        "server_count_sampled": len(rows),
        "full_servers_sampled": sum(
            1 for row in rows if int(row.get("maxPlayers") or 0) > 0 and int(row.get("playing") or 0) >= int(row.get("maxPlayers") or 0)
        ),
        "sampled_playing": sum(int(row.get("playing") or 0) for row in rows),
        "sampled_capacity": sum(int(row.get("maxPlayers") or 0) for row in rows),
        "avg_ping": round(sum(pings) / len(pings), 1) if pings else None,
        "max_ping": round(max(pings), 1) if pings else None,
        "avg_fps": round(sum(fps_values) / len(fps_values), 1) if fps_values else None,
        "updated": game.get("updated"),
    }


def load_previous() -> dict[str, Any]:
    try:
        return json.loads(STATE_PATH.read_text())
    except Exception:
        return {}


def save_current(sample: dict[str, Any]) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(sample, indent=2, sort_keys=True))


def latest_complete(points: list[dict[str, Any]]) -> dict[str, Any] | None:
    valid = [p for p in points if p.get("value") is not None]
    return valid[-1] if valid else None


def previous_window(points: list[dict[str, Any]], days: int = 7) -> list[float]:
    valid = [float(p["value"]) for p in points if p.get("value") is not None]
    return valid[-(days + 1):-1] if len(valid) > 1 else []


def pct_change(current: float | int | None, baseline: float | int | None) -> float | None:
    if current is None or baseline in (None, 0):
        return None
    return ((float(current) - float(baseline)) / float(baseline)) * 100


def fmt_num(value: float | int | None, decimals: int = 0) -> str:
    if value is None:
        return "n/a"
    if decimals == 0:
        return f"{float(value):,.0f}"
    return f"{float(value):,.{decimals}f}"


def fmt_pct(value: float | int | None, already_percent: bool = False) -> str:
    if value is None:
        return "n/a"
    pct_value = float(value) if already_percent else float(value) * 100
    return f"{pct_value:.1f}%"


def fmt_delta_pct(delta: float | None) -> str:
    if delta is None:
        return "n/a"
    if abs(delta) < 0.05:
        return "±0%"
    return f"{delta:+.1f}%"


def signed_delta(current: int | float | None, previous: int | float | None, decimals: int = 0) -> str:
    if current is None or previous is None:
        return ""
    delta = float(current) - float(previous)
    if abs(delta) < 0.0001:
        return " (±0)"
    if decimals == 0:
        return f" ({delta:+,.0f})"
    return f" ({delta:+,.{decimals}f})"


def build_analysis(public: dict[str, Any], analytics: dict[str, Any], previous: dict[str, Any]) -> str:
    dau = analytics.get("dau", {}).get("latest_value")
    dau_base = analytics.get("dau", {}).get("baseline")
    d1 = analytics.get("d1_retention", {}).get("latest_value")
    session = analytics.get("avg_session_min", {}).get("latest_value")
    session_base = analytics.get("avg_session_min", {}).get("baseline")
    revenue = analytics.get("revenue_robux", {}).get("latest_value")
    avg_ccu = analytics.get("avg_ccu", {}).get("latest_value")
    public_ccu = public.get("playing")
    fps = public.get("avg_fps")
    ping = public.get("avg_ping")

    dau_delta = pct_change(dau, dau_base)
    session_delta = pct_change(session, session_base)
    health = "stable"
    if dau_delta is not None and dau_delta <= -20:
        health = "down vs recent baseline"
    elif dau_delta is not None and dau_delta >= 20:
        health = "up vs recent baseline"
    elif d1 is not None and d1 < 0.07:
        health = "soft on retention"

    perf = "server sample looks healthy" if (fps is None or fps >= 55) and (ping is None or ping <= 120) else "server sample needs a look"
    return (
        f"Overall health is **{health}**: latest complete-day DAU is {fmt_num(dau)} "
        f"({fmt_delta_pct(dau_delta)} vs 7-day baseline), D1 retention is {fmt_pct(d1)}, "
        f"and avg session is {fmt_num(session, 1)} min ({fmt_delta_pct(session_delta)}). "
        f"Current public CCU is {fmt_num(public_ccu)} vs Creator avg CCU {fmt_num(avg_ccu, 1)} on the latest complete day; "
        f"{perf}. Revenue was {fmt_num(revenue)} Robux, so the implication is: watch acquisition/returning traffic first, "
        f"then validate whether funnel/event changes are improving D1 and session depth."
    )


def main() -> int:
    sampled_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    previous = load_previous()

    try:
        public = fetch_public()
    except Exception as exc:
        public = {"error": f"{type(exc).__name__}: {exc}"}

    analytics: dict[str, Any] = {}
    errors: list[str] = []
    try:
        cookie = read_cookie()
        end = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        start = end - timedelta(days=21)
        for key, metric in CORE_METRICS.items():
            try:
                points = query_metric(cookie, metric, start, end)
                latest = latest_complete(points)
                window = previous_window(points)
                baseline = statistics.mean(window) if window else None
                analytics[key] = {
                    "metric": metric,
                    "latest_date": latest.get("time", "")[:10] if latest else None,
                    "latest_value": latest.get("value") if latest else None,
                    "baseline": baseline,
                    "points": points,
                }
            except Exception as exc:
                errors.append(f"{metric}: {type(exc).__name__}: {exc}")
    except Exception as exc:
        errors.append(f"auth/setup: {type(exc).__name__}: {exc}")

    sample = {"sampled_at": sampled_at, "public": public, "analytics": analytics, "errors": errors}
    save_current(sample)

    prev_public = previous.get("public", {}) if previous else {}
    latest_date = next((v.get("latest_date") for v in analytics.values() if v.get("latest_date")), "n/a")

    lines = [
        "## Scraplands analytics monitor",
        f"- Sample: {sampled_at} UTC",
        f"- Creator Analytics date: {latest_date} (latest complete day)",
    ]

    if public.get("error"):
        lines.append(f"- Public Roblox metrics: failed — {public['error']}")
    else:
        like_ratio = public.get("like_ratio")
        lines.extend(
            [
                f"- Public now: CCU {fmt_num(public.get('playing'))}{signed_delta(public.get('playing'), prev_public.get('playing'))}; visits {fmt_num(public.get('visits'))}{signed_delta(public.get('visits'), prev_public.get('visits'))}; favorites {fmt_num(public.get('favorites'))}{signed_delta(public.get('favorites'), prev_public.get('favorites'))}",
                f"- Public sentiment: {fmt_num(public.get('up_votes'))} up / {fmt_num(public.get('down_votes'))} down — like ratio {fmt_pct(like_ratio, already_percent=True)}{signed_delta(like_ratio, prev_public.get('like_ratio'), 1)}",
                f"- Server sample: {fmt_num(public.get('server_count_sampled'))} active, {fmt_num(public.get('full_servers_sampled'))} full, {fmt_num(public.get('sampled_playing'))}/{fmt_num(public.get('sampled_capacity'))} sampled capacity; avg FPS {fmt_num(public.get('avg_fps'), 1)}, avg ping {fmt_num(public.get('avg_ping'), 1)}ms, max ping {fmt_num(public.get('max_ping'), 1)}ms",
            ]
        )

    if analytics:
        def row(key: str, label: str, formatter: str = "num", decimals: int = 0) -> str:
            item = analytics.get(key, {})
            value = item.get("latest_value")
            baseline = item.get("baseline")
            delta = pct_change(value, baseline)
            if formatter == "pct":
                value_text = fmt_pct(value)
                base_text = fmt_pct(baseline)
            else:
                value_text = fmt_num(value, decimals)
                base_text = fmt_num(baseline, decimals)
            return f"- {label}: {value_text} ({fmt_delta_pct(delta)} vs 7-day baseline {base_text})"

        lines.extend(
            [
                row("dau", "DAU"),
                row("visits", "Creator visits"),
                row("avg_ccu", "Avg CCU", decimals=1),
                row("avg_session_min", "Avg session", decimals=1) + " min",
                row("playtime_hours", "Total playtime", decimals=1) + " hours",
                row("d1_retention", "D1 retention", "pct"),
                row("d7_retention", "D7 retention", "pct"),
                row("revenue_robux", "Revenue" ) + " Robux",
                row("arpu", "ARPU", decimals=2) + " Robux/user",
                row("paying_users", "Paying users"),
                row("payer_cvr", "Payer conversion", "pct"),
            ]
        )
        lines.append(f"- Executive analysis: {build_analysis(public, analytics, previous)}")
    else:
        lines.append("- Creator Analytics: unavailable")

    if errors:
        lines.append("- Analytics warnings: " + " | ".join(errors[:3]))

    print("\n".join(lines))
    return 0 if analytics or not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
