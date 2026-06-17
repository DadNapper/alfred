#!/usr/bin/env python3
"""Scraplands public Roblox metrics monitor.

Fetches public Roblox endpoints for Scraplands [Beta], prints a concise report,
and stores the previous sample so each run can include deltas.
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

UNIVERSE_ID = 9056408258
PLACE_ID = 106937996439556
STATE_PATH = Path(os.path.expanduser("~/.hermes/state/scraplands_public_metrics.json"))
TIMEOUT = 20


def fetch_json(url: str) -> dict:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "HermesScraplandsPublicMetrics/1.0 (+Roblox public endpoints)",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        charset = resp.headers.get_content_charset() or "utf-8"
        return json.loads(resp.read().decode(charset))


def pct(numerator: float, denominator: float) -> str:
    if not denominator:
        return "n/a"
    return f"{(numerator / denominator) * 100:.1f}%"


def signed_delta(current: int | float | None, previous: int | float | None) -> str:
    if current is None or previous is None:
        return ""
    delta = current - previous
    if isinstance(delta, float):
        if abs(delta) < 0.05:
            return " (±0)"
        return f" ({delta:+.1f})"
    if delta == 0:
        return " (±0)"
    return f" ({delta:+,})"


def load_previous() -> dict | None:
    try:
        return json.loads(STATE_PATH.read_text())
    except FileNotFoundError:
        return None
    except Exception:
        return None


def save_current(sample: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(sample, indent=2, sort_keys=True))


def main() -> int:
    try:
        game = fetch_json(f"https://games.roblox.com/v1/games?universeIds={UNIVERSE_ID}")["data"][0]
        votes = fetch_json(f"https://games.roblox.com/v1/games/votes?universeIds={UNIVERSE_ID}")["data"][0]
        servers = fetch_json(
            f"https://games.roblox.com/v1/games/{PLACE_ID}/servers/Public?sortOrder=Desc&limit=100"
        )
    except (urllib.error.URLError, urllib.error.HTTPError, KeyError, IndexError, json.JSONDecodeError) as exc:
        print(f"Scraplands public metrics monitor failed: {type(exc).__name__}: {exc}")
        return 1

    server_rows = servers.get("data", [])
    active_servers = len(server_rows)
    sampled_capacity = sum(int(row.get("maxPlayers") or 0) for row in server_rows)
    sampled_playing = sum(int(row.get("playing") or 0) for row in server_rows)
    full_servers = sum(1 for row in server_rows if int(row.get("playing") or 0) >= int(row.get("maxPlayers") or 0) and int(row.get("maxPlayers") or 0) > 0)
    pings = [float(row.get("ping")) for row in server_rows if isinstance(row.get("ping"), (int, float))]
    fps_values = [float(row.get("fps")) for row in server_rows if isinstance(row.get("fps"), (int, float))]

    up = int(votes.get("upVotes") or 0)
    down = int(votes.get("downVotes") or 0)
    visits = int(game.get("visits") or 0)
    favorites = int(game.get("favoritedCount") or 0)
    playing = int(game.get("playing") or 0)

    sample = {
        "sampled_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "universe_id": UNIVERSE_ID,
        "place_id": PLACE_ID,
        "name": game.get("name"),
        "playing": playing,
        "visits": visits,
        "favorites": favorites,
        "up_votes": up,
        "down_votes": down,
        "like_ratio": round((up / (up + down)) * 100, 2) if (up + down) else None,
        "active_servers_sampled": active_servers,
        "sampled_playing": sampled_playing,
        "sampled_capacity": sampled_capacity,
        "full_servers_sampled": full_servers,
        "avg_ping": round(sum(pings) / len(pings), 1) if pings else None,
        "max_ping": round(max(pings), 1) if pings else None,
        "avg_fps": round(sum(fps_values) / len(fps_values), 1) if fps_values else None,
        "updated": game.get("updated"),
    }

    previous = load_previous()
    save_current(sample)

    prev = previous or {}
    lines = [
        "## Scraplands public metrics",
        f"- Sample: {sample['sampled_at']} UTC",
        f"- CCU: {playing}{signed_delta(playing, prev.get('playing'))}",
        f"- Visits: {visits:,}{signed_delta(visits, prev.get('visits'))}",
        f"- Favorites: {favorites:,}{signed_delta(favorites, prev.get('favorites'))}",
        f"- Votes: {up:,} up / {down:,} down — like ratio {sample['like_ratio']:.1f}%{signed_delta(sample['like_ratio'], prev.get('like_ratio')) if sample['like_ratio'] is not None else ''}",
        f"- Favorite rate: {pct(favorites, visits)} of visits",
        f"- Servers sampled: {active_servers} active, {full_servers} full, {sampled_playing}/{sampled_capacity} sampled capacity",
    ]
    if sample["avg_ping"] is not None or sample["avg_fps"] is not None:
        lines.append(f"- Server health sample: avg FPS {sample['avg_fps']}, avg ping {sample['avg_ping']}ms, max ping {sample['max_ping']}ms")
    lines.append(f"- Roblox updated: {sample['updated']}")

    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
