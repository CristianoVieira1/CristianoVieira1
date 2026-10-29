#!/usr/bin/env python3
"""Build Developer OS activity assets from public GitHub data.

No tokens. No invented metrics. Existing files are replaced only after a
successful fetch, so a network failure cannot blank the profile.
"""

from __future__ import annotations

import json
import os
import re
import sys
import urllib.request
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "assets"
README = ROOT / "README.md"
USER = os.environ.get("GITHUB_PROFILE", "CristianoVieira1")
UA = {"User-Agent": "cristiano-vieira-profile", "Accept": "application/vnd.github+json"}

SANS = 'ui-sans-serif, system-ui, -apple-system, "Segoe UI", Helvetica, Arial, sans-serif'
LEVELS = ["#10182A", "#155E75", "#0891B2", "#38BDF8", "#C4B5FD"]


CACHE = Path(__file__).resolve().parent / "language-cache.json"


def fetch_json(url: str):
    headers = dict(UA)
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token and "api.github.com" in url:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=40) as response:
        return json.load(response)


def esc(value: str) -> str:
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def pretty_day(iso: str) -> str:
    return datetime.strptime(iso, "%Y-%m-%d").strftime("%b %-d, %Y")


def panel(width: int, height: int, title: str, desc: str, body: str) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
  <title id="title">{esc(title)}</title>
  <desc id="desc">{esc(desc)}</desc>
  <defs>
    <linearGradient id="accent" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#38BDF8"/>
      <stop offset="0.55" stop-color="#22D3EE"/>
      <stop offset="1" stop-color="#8B5CF6"/>
    </linearGradient>
    <pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse">
      <path d="M32 0H0V32" fill="none" stroke="#132033" stroke-width="1"/>
    </pattern>
    <clipPath id="panel"><rect width="{width}" height="{height}" rx="20"/></clipPath>
    <style><![CDATA[
      text {{ font-family: {SANS}; }}
    ]]></style>
  </defs>
  <g clip-path="url(#panel)">
    <rect width="{width}" height="{height}" fill="#080B14"/>
    <rect width="{width}" height="{height}" fill="url(#grid)" opacity="0.4"/>
    <rect x="28" y="0" width="{max(width - 56, 0)}" height="2" fill="url(#accent)" opacity="0.9"/>
    {body}
  </g>
  <rect x="0.75" y="0.75" width="{width - 1.5}" height="{height - 1.5}" rx="20" fill="none" stroke="#16304A"/>
</svg>
"""


def streaks(days: list[dict]) -> dict:
    longest = current = 0
    longest_range = None
    start = None
    for item in days:
        if item["count"] > 0:
            if current == 0:
                start = item["date"]
            current += 1
            if current > longest:
                longest = current
                longest_range = (start, item["date"])
        else:
            current = 0

    # Today can still be empty. A streak is current only if it reaches today or yesterday.
    active = 0
    end_index = len(days) - 1
    if days and days[-1]["count"] == 0 and len(days) > 1:
        end_index = len(days) - 2
    if days and days[end_index]["count"] > 0:
        cursor = end_index
        while cursor >= 0 and days[cursor]["count"] > 0:
            active += 1
            cursor -= 1
    latest = next((item["date"] for item in reversed(days) if item["count"] > 0), None)
    return {
        "longest": longest,
        "longest_range": longest_range,
        "current": active,
        "latest": latest,
        "active_days": sum(1 for item in days if item["count"] > 0),
        "total": sum(item["count"] for item in days),
    }


def load_activity() -> tuple[list[dict], dict, list[tuple[str, int, float]]]:
    payload = fetch_json(f"https://github-contributions-api.jogruber.de/v4/{USER}?y=last")
    days = payload["contributions"]
    if not days:
        raise SystemExit("Contribution calendar was empty.")
    summary = streaks(days)
    totals: dict[str, int] = defaultdict(int)
    try:
        repos = fetch_json(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner")
        if isinstance(repos, dict):
            raise RuntimeError(repos.get("message", "GitHub API error"))
        for repo in repos:
            if repo.get("fork"):
                continue
            languages = fetch_json(repo["languages_url"])
            for name, nbytes in languages.items():
                totals[name] += int(nbytes)
        CACHE.write_text(json.dumps(totals, indent=2), encoding="utf-8")
    except Exception as error:
        if not CACHE.exists():
            raise SystemExit(f"Language data unavailable: {error}") from error
        print(f"Using cached language bytes ({error})", file=sys.stderr)
        totals = defaultdict(int, json.loads(CACHE.read_text(encoding="utf-8")))
    grand = sum(totals.values()) or 1
    ranked = [
        (name, nbytes, 100 * nbytes / grand)
        for name, nbytes in sorted(totals.items(), key=lambda item: -item[1])
    ]
    return days, summary, ranked[:6]


def metrics_svg(summary: dict, width: int, mobile: bool) -> str:
    total = f"{summary['total']:,}"
    active = f"{summary['active_days']:,}"
    longest = str(summary["longest"])
    latest = pretty_day(summary["latest"]) if summary["latest"] else "—"
    span = ""
    if summary["longest_range"]:
        start = datetime.strptime(summary["longest_range"][0], "%Y-%m-%d")
        end = datetime.strptime(summary["longest_range"][1], "%Y-%m-%d")
        if start.year == end.year:
            span = f"{start.strftime('%b %-d')} – {end.strftime('%b %-d, %Y')}"
        else:
            span = f"{pretty_day(summary['longest_range'][0])} – {pretty_day(summary['longest_range'][1])}"
    caption = (
        f"Current public streak: {summary['current']} days. "
        f"Latest contribution {latest}."
    )
    title = f"{total} public contributions in the last 12 months"
    if mobile:
        rows = [
            (total, "Contributions", "last 12 months"),
            (active, "Active days", "with public activity"),
            (longest, "Longest streak", span or "consecutive days"),
        ]
        blocks = []
        y = 72
        for value, label, hint in rows:
            blocks.append(
                f'<text x="28" y="{y}" fill="#F8FAFC" font-size="34" font-weight="700">{esc(value)}</text>'
                f'<text x="28" y="{y + 26}" fill="#94A3B8" font-size="15">{esc(label)}</text>'
                f'<text x="28" y="{y + 46}" fill="#64748B" font-size="13">{esc(hint)}</text>'
            )
            y += 86
        body = f"""
        <text x="28" y="34" fill="#22D3EE" font-size="12" letter-spacing="1.8">PUBLIC ACTIVITY</text>
        {''.join(blocks)}
        <text x="28" y="332" fill="#64748B" font-size="13">Current streak: {summary['current']} days</text>
        <text x="28" y="352" fill="#64748B" font-size="13">Latest contribution {esc(latest)}</text>
        """
        return panel(width, 376, title, caption, body)

    columns = [
        (total, "Contributions", "last 12 months"),
        (active, "Active days", "with public activity"),
        (longest, "Longest streak", span or "consecutive days"),
    ]
    centers = [170, 450, 730]
    parts = [
        '<text x="32" y="40" fill="#22D3EE" font-size="12" letter-spacing="2.2">PUBLIC ACTIVITY</text>',
        '<text x="868" y="40" text-anchor="end" fill="#64748B" font-size="12" letter-spacing="1.6">LAST 12 MONTHS</text>',
    ]
    for (value, label, hint), cx in zip(columns, centers):
        parts.append(f'<text x="{cx}" y="118" text-anchor="middle" fill="#F8FAFC" font-size="42" font-weight="700">{esc(value)}</text>')
        parts.append(f'<text x="{cx}" y="150" text-anchor="middle" fill="#94A3B8" font-size="15">{esc(label)}</text>')
        parts.append(f'<text x="{cx}" y="172" text-anchor="middle" fill="#64748B" font-size="12">{esc(hint)}</text>')
    parts.append(f'<text x="450" y="206" text-anchor="middle" fill="#64748B" font-size="13">{esc(caption)}</text>')
    return panel(900, 228, title, caption, "\n".join(parts))


def languages_svg(ranked: list[tuple[str, int, float]], mobile: bool) -> str:
    shown = ranked[:6]
    title = "Languages detected in public repositories, by bytes of code"
    shares = ", ".join(f"{name} {share:.0f}%" for name, _, share in shown)
    if mobile:
        parts = ['<text x="24" y="34" fill="#22D3EE" font-size="12" letter-spacing="1.6">PUBLIC CODE</text>']
        y = 68
        max_share = max((share for _, _, share in shown), default=1)
        for name, _, share in shown:
            width = 24 + (352 * share / max_share)
            parts.append(f'<text x="24" y="{y}" fill="#F8FAFC" font-size="16" font-weight="700">{esc(name)}</text>')
            parts.append(f'<text x="376" y="{y}" text-anchor="end" fill="#94A3B8" font-size="14">{share:.0f}%</text>')
            parts.append(f'<rect x="24" y="{y + 10}" width="352" height="7" rx="3.5" fill="#10182A"/>')
            parts.append(f'<rect x="24" y="{y + 10}" width="{width - 24:.1f}" height="7" rx="3.5" fill="url(#accent)"/>')
            y += 58
        return panel(400, y + 8, title, shares, "\n".join(parts))

    parts = [
        '<text x="32" y="42" fill="#22D3EE" font-size="12" letter-spacing="2">PUBLIC REPOSITORIES</text>',
        '<text x="868" y="42" text-anchor="end" fill="#64748B" font-size="12">BY BYTES OF CODE</text>',
    ]
    y = 86
    max_share = max((share for _, _, share in shown), default=1)
    for name, _, share in shown:
        bar = 520 * share / max_share
        parts.append(f'<text x="32" y="{y}" fill="#F8FAFC" font-size="16">{esc(name)}</text>')
        parts.append(f'<rect x="210" y="{y - 12}" width="520" height="8" rx="4" fill="#10182A"/>')
        parts.append(f'<rect x="210" y="{y - 12}" width="{bar:.1f}" height="8" rx="4" fill="url(#accent)"/>')
        parts.append(f'<text x="868" y="{y}" text-anchor="end" fill="#94A3B8" font-size="14">{share:.0f}%</text>')
        y += 36
    return panel(900, 300, title, shares, "\n".join(parts))


def contribution_grid(days: list[dict], summary: dict) -> str:
    parsed = [(datetime.strptime(item["date"], "%Y-%m-%d").date(), item) for item in days]
    step = 13
    origin_x = 46
    origin_y = 28
    columns: list[list[tuple[date, dict] | None]] = []
    current: list[tuple[date, dict] | None] = [None] * 7
    for day, item in parsed:
        row = (day.weekday() + 1) % 7  # Sunday = 0
        if row == 0 and any(cell is not None for cell in current):
            columns.append(current)
            current = [None] * 7
        current[row] = (day, item)
    if any(cell is not None for cell in current):
        columns.append(current)

    cells = []
    month_labels = []
    last_month = None
    last_label_x = -100
    for col, week in enumerate(columns):
        x = origin_x + col * step
        for row, cell in enumerate(week):
            if cell is None:
                continue
            day, item = cell
            color = LEVELS[min(int(item.get("level", 0)), 4)]
            y = origin_y + row * step
            cells.append(
                f'<rect x="{x}" y="{y}" width="10" height="10" rx="2" fill="{color}">'
                f'<title>{esc(pretty_day(item["date"]))}: {item["count"]} contributions</title></rect>'
            )
            if day.day <= 7 and (day.year, day.month) != last_month and x - last_label_x >= 32:
                last_month = (day.year, day.month)
                last_label_x = x
                month_labels.append(
                    f'<text x="{x}" y="16" fill="#64748B" font-size="11">{day.strftime("%b")}</text>'
                )
    width = origin_x + len(columns) * step + 24
    height = 168
    day_labels = [(1, "Mon"), (3, "Wed"), (5, "Fri")]
    labels = [
        f'<text x="8" y="{origin_y + row * step + 9}" fill="#64748B" font-size="10">{name}</text>'
        for row, name in day_labels
    ]
    legend_x = width - 168
    legend = [f'<text x="{legend_x}" y="154" fill="#64748B" font-size="11">Less</text>']
    for index, color in enumerate(LEVELS):
        legend.append(
            f'<rect x="{legend_x + 32 + index * 16}" y="145" width="10" height="10" rx="2" fill="{color}"/>'
        )
    legend.append(f'<text x="{legend_x + 116}" y="154" fill="#64748B" font-size="11">More</text>')
    total = f"{summary['total']:,}"
    desc = f"{total} public contributions from {pretty_day(days[0]['date'])} to {pretty_day(days[-1]['date'])}."
    body = "\n".join(month_labels + labels + cells + legend)
    # Custom frame because the grid is wider than the standard metric panels and shorter.
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
  <title id="title">Public contribution graph</title>
  <desc id="desc">{esc(desc)}</desc>
  <style><![CDATA[ text {{ font-family: {SANS}; }} ]]></style>
  <rect width="{width}" height="{height}" rx="20" fill="#080B14"/>
  <rect x="0.75" y="0.75" width="{width - 1.5}" height="{height - 1.5}" rx="20" fill="none" stroke="#16304A"/>
  {body}
</svg>
"""


def replace_marker(text: str, name: str, payload: str) -> str:
    pattern = re.compile(
        rf"<!-- {name}:start -->.*?<!-- {name}:end -->",
        re.DOTALL,
    )
    block = f"<!-- {name}:start -->\n{payload}\n<!-- {name}:end -->"
    if not pattern.search(text):
        return text
    return pattern.sub(block, text, count=1)


def caption(summary: dict, ranked: list[tuple[str, int, float]]) -> tuple[str, str]:
    latest = pretty_day(summary["latest"]) if summary["latest"] else "—"
    span = "—"
    if summary["longest_range"]:
        span = f"{pretty_day(summary['longest_range'][0])} – {pretty_day(summary['longest_range'][1])}"
    activity = (
        f'<p align="center"><sub>{summary["total"]:,} public contributions in the last 12 months'
        f" · {summary['active_days']} active days"
        f" · longest streak {summary['longest']} days ({span})"
        f" · current streak {summary['current']} days"
        f" · latest contribution {latest}</sub></p>"
    )
    shares = " · ".join(f"{name} {share:.0f}%" for name, _, share in ranked[:6])
    languages = (
        '<p align="center"><sub>Language share in public repositories, by bytes: '
        f"{esc(shares)}</sub></p>"
    )
    return activity, languages


def write_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)


def main() -> None:
    days, summary, ranked = load_activity()
    write_atomic(ASSETS / "activity-metrics.svg", metrics_svg(summary, 900, False))
    write_atomic(ASSETS / "activity-metrics-mobile.svg", metrics_svg(summary, 400, True))
    write_atomic(ASSETS / "languages.svg", languages_svg(ranked, False))
    write_atomic(ASSETS / "languages-mobile.svg", languages_svg(ranked, True))
    write_atomic(ASSETS / "contribution-grid.svg", contribution_grid(days, summary))
    activity_caption, language_caption = caption(summary, ranked)
    if README.exists():
        updated = replace_marker(README.read_text(encoding="utf-8"), "activity", activity_caption)
        updated = replace_marker(updated, "languages", language_caption)
        write_atomic(README, updated)
    print(activity_caption)
    print(language_caption)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:  # noqa: BLE001 — surface a single actionable failure
        print(f"Activity generation failed: {error}", file=sys.stderr)
        sys.exit(1)
