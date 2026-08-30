#!/usr/bin/env python3
"""Компактный RU AdList для AdGuard DNS (лимит польз. правил ~1000).

Приоритет: сначала все исключения (снимают ложные блокировки),
затем adservers.txt (самый выверенный источник), затем general_block.txt,
и в последнюю очередь thirdparty.txt - на оставшееся место в лимите.
"""
import re
import urllib.request
from pathlib import Path

OUTPUT = Path("ru-adlist-dns.txt")
LIMIT = 950

BLOCK_TIERS = [
    ("adservers", "https://raw.githubusercontent.com/easylist/ruadlist/master/advblock/adservers.txt"),
    ("general_block", "https://raw.githubusercontent.com/easylist/ruadlist/master/advblock/general_block.txt"),
    ("thirdparty", "https://raw.githubusercontent.com/easylist/ruadlist/master/advblock/thirdparty.txt"),
]
ALLOW_SOURCES = [
    "https://raw.githubusercontent.com/easylist/ruadlist/master/advblock/whitelist.txt",
]

RULE_RE = re.compile(r"^(@@)?\|\|([a-z0-9.-]+)\^(?:\$.*)?$")


def download(url):
    req = urllib.request.Request(url, headers={"User-Agent": "ru-adlist-dns/2.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", errors="ignore")


def extract_block(text):
    result = set()
    for line in text.splitlines():
        m = RULE_RE.match(line.strip())
        if m and not m.group(1):
            result.add(m.group(2))
    return result


def extract_allow(text):
    result = set()
    for line in text.splitlines():
        m = RULE_RE.match(line.strip())
        if m and m.group(1):
            result.add(m.group(2))
    return result


def main():
    allow = set()
    for url in ALLOW_SOURCES:
        a = extract_allow(download(url))
        allow |= a
        print("OK allow: " + url + " - " + str(len(a)) + " исключений")

    exception_lines = []
    for d in sorted(allow):
        exception_lines.append("@@||" + d + "^")

    used = set(allow)
    block_lines = []
    stats = []
    budget = LIMIT - len(exception_lines)

    for name, url in BLOCK_TIERS:
        if budget <= 0:
            stats.append(name + ": 0 (бюджет исчерпан)")
            continue
        parsed = extract_block(download(url))
        candidates = sorted(parsed - used)
        take = candidates[:budget]
        for d in take:
            block_lines.append("||" + d + "^")
        used |= set(take)
        budget -= len(take)
        stats.append(name + ": доступно " + str(len(parsed)) + ", взято " + str(len(take)))
        print("OK block: " + url + " - доступно " + str(len(parsed)) + ", взято " + str(len(take)))

    lines = exception_lines + block_lines

    header = [
        "! RU AdList - компактная версия для AdGuard DNS (лимит " + str(LIMIT) + ")",
        "! Источник: https://github.com/easylist/ruadlist",
        "! Исключений: " + str(len(exception_lines)) + ", блокировок: " + str(len(block_lines)) + ", итого: " + str(len(lines)),
        "! Приоритет источников блокировки:",
    ]
    for s in stats:
        header.append("!   " + s)
    header.append("")

    OUTPUT.write_text("\n".join(header + lines) + "\n", encoding="utf-8")
    print("Готово: " + str(len(lines)) + " правил")


main()
