#!/usr/bin/env python3
"""Компактный RU AdList для AdGuard DNS (лимит польз. правил ~1000)."""
from future import annotations
import re
import urllib.request
from pathlib import Path

OUTPUT = Path("ru-adlist-dns.txt")
LIMIT = 950  # с запасом от лимита AdGuard в 1000

BLOCK_SOURCES = [
    "https://raw.githubusercontent.com/easylist/ruadlist/master/advblock/adservers.txt",
    "https://raw.githubusercontent.com/easylist/ruadlist/master/advblock/general_block.txt",
    "https://raw.githubusercontent.com/easylist/ruadlist/master/advblock/thirdparty.txt",
]
ALLOW_SOURCES = [
    "https://raw.githubusercontent.com/easylist/ruadlist/master/advblock/whitelist.txt",
]

RULE_RE = re.compile(r"^(@@)?\|\|([a-z0-9.-]+)\^$")

def download(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "ru-adlist-dns/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", errors="ignore")

def extract(text: str) -> tuple[set[str], set[str]]:
    block, allow = set(), set()
    for line in text.splitlines():
        m = RULE_RE.match(line.strip())
        if not m:
            continue
        (allow if m.group(1) else block).add(m.group(2))
    return block, allow

def main() -> None:
    block: set[str] = set()
    allow: set[str] = set()

    for url in BLOCK_SOURCES:
        b, a = extract(download(url))
        block |= b
        allow |= a
        print(f"OK: {url} — {len(b)} блокировок")

    for url in ALLOW_SOURCES:
        b, a = extract(download(url))
        allow |= a | b
        print(f"OK: {url} — {len(a) + len(b)} исключений")

    allow -= block  # без дублей
    lines = [f"@@||{d}^" for d in sorted(allow)]

    remaining = LIMIT - len(lines)
    if remaining > 0:
        lines += [f"||{d}^" for d in sorted(block)[:remaining]]
    lines = lines[:LIMIT]

    header = [
        f"! RU AdList — компактная версия для AdGuard DNS (лимит {LIMIT})",
        "! Источник: https://github.com/easylist/ruadlist",
        f"! Исключений: {len(allow)}, итого правил: {len(lines)}",
        "",
    ]
    OUTPUT.write_text("\n".join(header + lines) + "\n", encoding="utf-8")
    print(f"Готово: {len(lines)} правил")

if name == "main":
    main()
