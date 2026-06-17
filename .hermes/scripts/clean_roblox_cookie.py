#!/usr/bin/env python3
"""Extract a .ROBLOSECURITY value from a pasted cookie dump.

Usage:
  python3 ~/.hermes/scripts/clean_roblox_cookie.py ~/.hermes/secrets/roblox_cookie_raw.txt

Writes ~/.hermes/secrets/roblox_analytics.env with ROBLOX_ROBLOSECURITY='...'.
Does not print the cookie value.
"""
from __future__ import annotations

import os
import re
import stat
import sys
from pathlib import Path

HOME = Path.home()
OUT = HOME / ".hermes" / "secrets" / "roblox_analytics.env"


def shell_single_quote(value: str) -> str:
    return "'" + value.replace("'", "'\"'\"'") + "'"


def clean_token(s: str) -> str:
    s = s.strip().strip('"').strip("'").strip()
    # Remove optional cookie assignment prefix.
    for prefix in (".ROBLOSECURITY=", "ROBLOSECURITY="):
        if s.startswith(prefix):
            s = s[len(prefix):].strip()
    # Stop at common cookie separators / metadata if present.
    for sep in [";", "\t.roblox.com", " .roblox.com", "\n"]:
        if sep in s:
            s = s.split(sep, 1)[0].strip()
    return s.strip().strip('"').strip("'").strip()


def extract(text: str) -> str | None:
    # Best case: direct assignment in any pasted format.
    m = re.search(r"(?:^|[\s;])(?:\.)?ROBLOSECURITY\s*=\s*(['\"]?)([^'\";\n\r\t ]{200,})\1", text, re.IGNORECASE)
    if m:
        return clean_token(m.group(2))

    lines = [line.strip() for line in text.splitlines() if line.strip()]

    # Browser table/export/Netscape formats: line contains .ROBLOSECURITY, value is usually last field.
    for line in lines:
        if ".ROBLOSECURITY" in line or "ROBLOSECURITY" in line:
            parts = re.split(r"\t+|\s{2,}", line)
            candidates = list(reversed(parts)) + [line]
            for part in candidates:
                token = clean_token(part)
                if len(token) > 200 and not token.lower().startswith(".roblox.com"):
                    return token

    # Fallback: find Roblox warning-format token.
    m = re.search(r"(_\|WARNING:[^\s;'\"]{200,})", text)
    if m:
        return clean_token(m.group(1))

    # Fallback: if whole file is just the token.
    whole = clean_token(text)
    if len(whole) > 200:
        return whole
    return None


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: clean_roblox_cookie.py RAW_COOKIE_DUMP_FILE")
        return 2
    raw_path = Path(sys.argv[1]).expanduser()
    text = raw_path.read_text(errors="replace")
    token = extract(text)
    if not token:
        print("Could not find a plausible .ROBLOSECURITY value in the raw file.")
        return 1
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(f"ROBLOX_ROBLOSECURITY={shell_single_quote(token)}\n")
    os.chmod(OUT, stat.S_IRUSR | stat.S_IWUSR)
    print(f"Wrote {OUT}")
    print(f"Cookie length: {len(token)}")
    print(f"Looks like classic warning format: {'yes' if token.startswith('_|WARNING:') else 'no'}")
    print("Cookie value was not printed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
