#!/usr/bin/env python3
"""Generate the static Developer OS illustrations. Data cards are separate."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "assets"

BASE_CSS = """
text { font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Helvetica, Arial, sans-serif; }
.mono { font-family: ui-monospace, "SF Mono", SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace; }
.spin, .spin-rev, .drift, .sweep, .trace, .pulse, .caret, .ln {
  transform-box: fill-box;
  transform-origin: center;
}
.sweep, .trace { transform-box: view-box; }
.spin { animation: spin 28s linear infinite; }
.spin-rev { animation: spin 42s linear infinite reverse; }
.drift { animation: drift 12s ease-in-out infinite; }
.sweep { animation: sweep 9.5s ease-in-out infinite; }
.trace { stroke-dasharray: 36 220; animation: travel 8s linear infinite; }
.pulse { animation: pulse 2.8s ease-in-out infinite; }
.caret { animation: blink 1.15s steps(1, end) infinite; }
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes drift {
  0%, 100% { transform: translateY(0); opacity: .28; }
  50% { transform: translateY(-12px); opacity: .9; }
}
@keyframes sweep {
  0% { transform: translateX(0); }
  62%, 100% { transform: translateX(1500px); }
}
@keyframes travel { to { stroke-dashoffset: -512; } }
@keyframes pulse { 0%, 100% { opacity: .35; } 50% { opacity: 1; } }
@keyframes blink { 50% { opacity: 0; } }
@media (prefers-reduced-motion: reduce) {
  .motion { animation: none !important; }
}
"""


def esc(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def document(width: int, height: int, title: str, desc: str, body: str, css: str = "") -> str:
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
  <title id="title">{esc(title)}</title>
  <desc id="desc">{esc(desc)}</desc>
  <defs>
    <linearGradient id="accent" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#38BDF8"/>
      <stop offset="0.5" stop-color="#22D3EE"/>
      <stop offset="1" stop-color="#8B5CF6"/>
    </linearGradient>
    <linearGradient id="sheen" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#F8FAFC" stop-opacity="0.08"/>
      <stop offset="1" stop-color="#F8FAFC" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="sweepGrad" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#38BDF8" stop-opacity="0"/>
      <stop offset="0.5" stop-color="#F8FAFC" stop-opacity="0.7"/>
      <stop offset="1" stop-color="#8B5CF6" stop-opacity="0"/>
    </linearGradient>
    <radialGradient id="aura" cx="50%" cy="46%" r="58%">
      <stop offset="0" stop-color="#1D4ED8" stop-opacity="0.34"/>
      <stop offset="0.42" stop-color="#22D3EE" stop-opacity="0.08"/>
      <stop offset="1" stop-color="#080B14" stop-opacity="0"/>
    </radialGradient>
    <filter id="soft" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="8"/>
    </filter>
    <pattern id="grid" width="48" height="48" patternUnits="userSpaceOnUse">
      <path d="M48 0H0V48" fill="none" stroke="#132033" stroke-width="1"/>
    </pattern>
    <clipPath id="frame"><rect width="{width}" height="{height}" rx="24"/></clipPath>
    <style><![CDATA[
{BASE_CSS}
{css}
    ]]></style>
  </defs>
  {body}
</svg>
"""


def save(name: str, content: str) -> None:
    (OUT / name).write_text(content, encoding="utf-8")


def reveal_css(count: int) -> str:
    """Hold the finished terminal first, then clear and retype.

    Frame 0 is fully readable, so a renderer that freezes the first frame
    still shows every command.
    """
    rules = []
    slot = 32 / max(count, 1)
    for index in range(count):
        hidden_until = round(58 + index * slot, 2)
        shown = round(min(96, hidden_until + max(2.2, slot * 0.75)), 2)
        rules.append(
            f".l{index} {{ animation: rev{index} 20s linear infinite; }}\n"
            f"@keyframes rev{index} {{\n"
            f"  0%, 46% {{ clip-path: inset(0 0 0 0); }}\n"
            f"  52%, {hidden_until}% {{ clip-path: inset(0 100% 0 0); }}\n"
            f"  {shown}%, 100% {{ clip-path: inset(0 0 0 0); }}\n"
            f"}}"
        )
    return "\n".join(rules)


def stage(width: int, height: int) -> str:
    return f"""
    <g clip-path="url(#frame)">
      <rect width="{width}" height="{height}" fill="#080B14"/>
      <rect width="{width}" height="{height}" fill="url(#grid)" opacity="0.55"/>
      <rect width="{width}" height="{height}" fill="url(#aura)"/>
      <rect width="{width}" height="120" fill="url(#sheen)"/>
      <rect class="motion sweep" x="-220" y="0" width="160" height="{height}" fill="url(#sweepGrad)" opacity="0.28"/>
    </g>
    <rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="24" fill="none" stroke="#16304A"/>
    <rect x="10" y="10" width="{width - 20}" height="{height - 20}" rx="18" fill="none" stroke="url(#accent)" stroke-opacity="0.35" class="motion trace"/>
    """


def corners(width: int, height: int, inset: int = 28) -> str:
    a, b = inset, inset + 22
    right = width - inset
    bottom = height - inset
    color = 'stroke="#38BDF8" stroke-opacity="0.75" stroke-width="1.4" fill="none"'
    return f"""
    <path d="M{a} {b} V{a} H{b}" {color}/>
    <path d="M{right - 22} {a} H{right} V{b}" {color}/>
    <path d="M{a} {bottom - 22} V{bottom} H{b}" {color}/>
    <path d="M{right} {bottom - 22} V{bottom} H{right - 22}" {color}/>
    """


def particles(points: list[tuple[int, int, str, float]]) -> str:
    parts = []
    for index, (x, y, color, delay) in enumerate(points):
        duration = 10 + (index % 5) * 1.6
        parts.append(
            f'<circle class="motion drift" cx="{x}" cy="{y}" r="{1.4 + (index % 3) * 0.45:.2f}" '
            f'fill="{color}" style="animation-duration:{duration:.1f}s; animation-delay:-{delay:.1f}s"/>'
        )
    return "\n".join(parts)


def hero() -> None:
    w, h = 1040, 600
    rings = """
    <g class="motion spin">
      <ellipse cx="520" cy="250" rx="250" ry="78" fill="none" stroke="#38BDF8" stroke-opacity="0.28"/>
      <circle cx="770" cy="250" r="3.2" fill="#22D3EE"/>
    </g>
    <g class="motion spin-rev">
      <ellipse cx="520" cy="250" rx="188" ry="118" fill="none" stroke="#8B5CF6" stroke-opacity="0.32"/>
      <circle cx="520" cy="132" r="2.6" fill="#C4B5FD"/>
    </g>
    """
    circuits = """
    <g fill="none" stroke-linecap="square">
      <path d="M48 168 H150 L190 128 H280" stroke="#164E63" stroke-width="1.2"/>
      <path d="M96 48 V120 L132 156 V210" stroke="#164E63" stroke-width="1.2"/>
      <path d="M992 430 H890 L850 470 H760" stroke="#164E63" stroke-width="1.2"/>
      <path d="M944 552 V470 L908 434 V360" stroke="#164E63" stroke-width="1.2"/>
      <path class="motion trace" d="M48 168 H150 L190 128 H280" stroke="#22D3EE" stroke-width="1.4"/>
      <path class="motion trace" d="M992 430 H890 L850 470 H760" stroke="#8B5CF6" stroke-width="1.4"/>
    </g>
    <path d="M168 154 V166 M162 160 H174" stroke="#38BDF8" stroke-opacity="0.45" fill="none"/>
    <path d="M860 214 V226 M854 220 H866" stroke="#22D3EE" stroke-opacity="0.4" fill="none"/>
    <path d="M210 470 V482 M204 476 H216" stroke="#8B5CF6" stroke-opacity="0.45" fill="none"/>
    """
    chips = [(335, "MOBILE", 112), (459, "WEB", 84), (555, "FULL STACK", 150)]
    chip_svg = []
    for x, label, width in chips:
        chip_svg.append(
            f'<rect x="{x}" y="346" width="{width}" height="34" rx="17" fill="#0C1222" stroke="#1E3A5F"/>'
            f'<text x="{x + width / 2}" y="368" text-anchor="middle" fill="#F8FAFC" font-size="12" letter-spacing="1.4">{label}</text>'
        )
    body = f"""
    {stage(w, h)}
    {corners(w, h)}
    {rings}
    {circuits}
    {particles([
        (120, 150, "#22D3EE", 0), (210, 430, "#8B5CF6", 2), (860, 120, "#38BDF8", 1),
        (930, 360, "#22D3EE", 3), (640, 96, "#C4B5FD", 1.4), (300, 520, "#38BDF8", 2.6),
        (80, 320, "#22D3EE", 4), (980, 230, "#8B5CF6", 0.8), (470, 520, "#67E8F9", 3.2),
        (760, 500, "#38BDF8", 1.8), (390, 120, "#22D3EE", 2.2), (700, 430, "#8B5CF6", 4.4),
    ])}
    <text x="48" y="58" fill="#94A3B8" font-size="13" letter-spacing="3.2">DEVELOPER OS</text>
    <text x="992" y="58" text-anchor="end" fill="#38BDF8" font-size="13" letter-spacing="2.4">2026</text>
    <text x="520" y="214" text-anchor="middle" fill="#38BDF8" font-size="54" font-weight="700" letter-spacing="1.5" filter="url(#soft)" opacity="0.45">CRISTIANO VIEIRA</text>
    <text x="520" y="214" text-anchor="middle" fill="#F8FAFC" font-size="54" font-weight="700" letter-spacing="1.5">CRISTIANO VIEIRA</text>
    <text x="520" y="268" text-anchor="middle" fill="#7DD3FC" font-size="26" letter-spacing="0.6">Senior Software Engineer</text>
    {''.join(chip_svg)}
    <text x="520" y="442" text-anchor="middle" fill="#E2E8F0" font-size="20" letter-spacing="2.2">Build. Innovate. Scale.</text>
    <rect x="364" y="492" width="312" height="36" rx="18" fill="#0C1222" stroke="#1E3A5F"/>
    <circle class="motion pulse" cx="390" cy="510" r="4.5" fill="#34D399"/>
    <text x="406" y="515" fill="#E2E8F0" font-size="14">Available for new opportunities</text>
    """
    save("hero.svg", document(
        w, h,
        "Cristiano Vieira — Senior Software Engineer",
        "Developer OS 2026. Mobile, Web, and Full Stack. Build. Innovate. Scale. Available for new opportunities.",
        body,
    ))


def hero_mobile() -> None:
    w, h = 400, 700
    body = f"""
    {stage(w, h)}
    {corners(w, h, 18)}
    <g class="motion spin">
      <ellipse cx="200" cy="250" rx="150" ry="64" fill="none" stroke="#38BDF8" stroke-opacity="0.3"/>
      <circle cx="350" cy="250" r="3" fill="#22D3EE"/>
    </g>
    <g class="motion spin-rev">
      <ellipse cx="200" cy="250" rx="104" ry="104" fill="none" stroke="#8B5CF6" stroke-opacity="0.28"/>
      <circle cx="200" cy="146" r="2.5" fill="#C4B5FD"/>
    </g>
    {particles([(40, 120, "#22D3EE", 0), (340, 160, "#8B5CF6", 1), (60, 560, "#38BDF8", 2), (330, 520, "#22D3EE", 1.5), (200, 80, "#C4B5FD", 3)])}
    <text x="24" y="48" fill="#94A3B8" font-size="12" letter-spacing="2.4">DEVELOPER OS</text>
    <text x="376" y="48" text-anchor="end" fill="#38BDF8" font-size="12" letter-spacing="1.8">2026</text>
    <text x="200" y="210" text-anchor="middle" fill="#38BDF8" font-size="42" font-weight="700" filter="url(#soft)" opacity="0.5">CRISTIANO</text>
    <text x="200" y="210" text-anchor="middle" fill="#F8FAFC" font-size="42" font-weight="700" letter-spacing="1">CRISTIANO</text>
    <text x="200" y="262" text-anchor="middle" fill="#38BDF8" font-size="42" font-weight="700" filter="url(#soft)" opacity="0.5">VIEIRA</text>
    <text x="200" y="262" text-anchor="middle" fill="#F8FAFC" font-size="42" font-weight="700" letter-spacing="3">VIEIRA</text>
    <text x="200" y="318" text-anchor="middle" fill="#7DD3FC" font-size="18">Senior Software Engineer</text>
    <rect x="28" y="352" width="108" height="32" rx="16" fill="#0C1222" stroke="#1E3A5F"/>
    <rect x="146" y="352" width="78" height="32" rx="16" fill="#0C1222" stroke="#1E3A5F"/>
    <rect x="234" y="352" width="140" height="32" rx="16" fill="#0C1222" stroke="#1E3A5F"/>
    <text x="82" y="373" text-anchor="middle" fill="#F8FAFC" font-size="12" letter-spacing="1">MOBILE</text>
    <text x="185" y="373" text-anchor="middle" fill="#F8FAFC" font-size="12" letter-spacing="1">WEB</text>
    <text x="304" y="373" text-anchor="middle" fill="#F8FAFC" font-size="12" letter-spacing="1">FULL STACK</text>
    <text x="200" y="460" text-anchor="middle" fill="#E2E8F0" font-size="16" letter-spacing="0.8">Build. Innovate. Scale.</text>
    <rect x="42" y="520" width="316" height="40" rx="20" fill="#0C1222" stroke="#1E3A5F"/>
    <circle class="motion pulse" cx="68" cy="540" r="4.5" fill="#34D399"/>
    <text x="84" y="545" fill="#E2E8F0" font-size="13">Available for new opportunities</text>
    """
    save("hero-mobile.svg", document(
        w, h,
        "Cristiano Vieira — Senior Software Engineer",
        "Developer OS 2026. Mobile, Web, and Full Stack. Build. Innovate. Scale. Available for new opportunities.",
        body,
    ))


def terminal_lines(specs: list[tuple[str, str, str]], size: int, y0: int, step: int) -> str:
    groups = []
    for index, (kind, symbol, value) in enumerate(specs):
        color = "#22D3EE" if kind == "cmd" else "#C4B5FD"
        value_color = "#F8FAFC" if kind == "cmd" else "#E2E8F0"
        y = y0 + index * step
        caret = ""
        if index == len(specs) - 1:
            caret = f'<rect class="motion caret" x="62" y="{y - 13}" width="9" height="{size}" rx="1" fill="#22D3EE"/>'
        groups.append(
            f'<g class="motion ln l{index}">'
            f'<text class="mono" x="36" y="{y}" fill="{color}" font-size="{size}">{esc(symbol)}</text>'
            f'<text class="mono" x="62" y="{y}" fill="{value_color}" font-size="{size}">{esc(value)}</text>'
            f"{caret}</g>"
        )
    return "\n".join(groups)


def terminal() -> None:
    specs = [
        ("cmd", "$", "whoami"),
        ("out", ">", "Cristiano Vieira"),
        ("cmd", "$", "current_role"),
        ("out", ">", "Senior Software Engineer"),
        ("cmd", "$", "specialization"),
        ("out", ">", "React Native | React | TypeScript | Node.js"),
        ("cmd", "$", "mission"),
        ("out", ">", "Building scalable digital experiences."),
        ("cmd", "$", "status"),
        ("out", ">", "Available for new opportunities"),
        ("cmd", "$", ""),
    ]
    w, h = 860, 460
    body = f"""
    {stage(w, h)}
    <circle cx="28" cy="28" r="6" fill="#F43F5E" fill-opacity="0.85"/>
    <circle cx="50" cy="28" r="6" fill="#F59E0B" fill-opacity="0.85"/>
    <circle cx="72" cy="28" r="6" fill="#34D399" fill-opacity="0.85"/>
    <text class="mono" x="430" y="33" text-anchor="middle" fill="#94A3B8" font-size="13">cristiano@developer-os — zsh</text>
    <path d="M20 52 H840" stroke="#16304A"/>
    {terminal_lines(specs, 16, 92, 32)}
    """
    save("terminal.svg", document(
        w, h,
        "Terminal — Cristiano Vieira",
        "whoami: Cristiano Vieira. current_role: Senior Software Engineer. specialization: React Native, React, TypeScript, Node.js. mission: Building scalable digital experiences. status: Available for new opportunities.",
        body,
        reveal_css(len(specs)),
    ))


def terminal_mobile() -> None:
    specs = [
        ("cmd", "$", "whoami"),
        ("out", ">", "Cristiano Vieira"),
        ("cmd", "$", "current_role"),
        ("out", ">", "Senior Software Engineer"),
        ("cmd", "$", "specialization"),
        ("out", ">", "React Native | React"),
        ("out", ">", "TypeScript | Node.js"),
        ("cmd", "$", "mission"),
        ("out", ">", "Building scalable"),
        ("out", ">", "digital experiences."),
        ("cmd", "$", "status"),
        ("out", ">", "Available for new"),
        ("out", ">", "opportunities"),
        ("cmd", "$", ""),
    ]
    w, h = 400, 620
    body = f"""
    {stage(w, h)}
    <circle cx="24" cy="26" r="5.5" fill="#F43F5E" fill-opacity="0.85"/>
    <circle cx="42" cy="26" r="5.5" fill="#F59E0B" fill-opacity="0.85"/>
    <circle cx="60" cy="26" r="5.5" fill="#34D399" fill-opacity="0.85"/>
    <text class="mono" x="200" y="31" text-anchor="middle" fill="#94A3B8" font-size="12">developer-os — zsh</text>
    <path d="M16 48 H384" stroke="#16304A"/>
    {terminal_lines(specs, 15, 84, 36)}
    """
    save("terminal-mobile.svg", document(
        w, h,
        "Terminal — Cristiano Vieira",
        "whoami: Cristiano Vieira. current_role: Senior Software Engineer. specialization: React Native, React, TypeScript, Node.js. mission: Building scalable digital experiences. status: Available for new opportunities.",
        body,
        reveal_css(len(specs)),
    ))


def digital_core() -> None:
    w = h = 320
    body = f"""
    {stage(w, h)}
    <g class="motion spin">
      <circle cx="160" cy="160" r="118" fill="none" stroke="#22D3EE" stroke-opacity="0.28" stroke-dasharray="2 7"/>
      <circle cx="160" cy="42" r="3.5" fill="#22D3EE"/>
    </g>
    <g class="motion spin-rev">
      <circle cx="160" cy="160" r="96" fill="none" stroke="#8B5CF6" stroke-opacity="0.4" stroke-dasharray="10 14"/>
      <circle cx="256" cy="160" r="3.2" fill="#C4B5FD"/>
      <circle cx="92" cy="214" r="2.4" fill="#38BDF8"/>
    </g>
    <g class="motion spin" style="animation-duration: 18s">
      <circle cx="160" cy="160" r="74" fill="none" stroke="#38BDF8" stroke-opacity="0.55"/>
      <circle cx="160" cy="86" r="4" fill="#F8FAFC"/>
    </g>
    {particles([(54, 70, "#22D3EE", 0), (260, 84, "#8B5CF6", 1), (70, 250, "#38BDF8", 2), (248, 246, "#67E8F9", 1.4)])}
    <circle cx="160" cy="160" r="52" fill="#0C1222" stroke="url(#accent)" stroke-width="1.6"/>
    <text x="160" y="176" text-anchor="middle" fill="#38BDF8" font-size="64" font-weight="700" filter="url(#soft)" opacity="0.7">C</text>
    <text x="160" y="176" text-anchor="middle" fill="url(#accent)" font-size="64" font-weight="700">C</text>
    <circle class="motion pulse" cx="160" cy="160" r="3" fill="#F8FAFC"/>
    """
    save("digital-core.svg", document(
        w, h,
        "Digital Core",
        "Signature monogram. A letter C orbited by rings and particles.",
        body,
    ))


def glass_card(x: int, y: int, width: int, height: int, title: str, items: list[str], size: int = 16) -> str:
    rows = [f'<text x="{x + 22}" y="{y + 32}" fill="#22D3EE" font-size="12" letter-spacing="1.5">{esc(title)}</text>']
    baseline = y + 64
    for item in items:
        rows.append(f'<text x="{x + 22}" y="{baseline}" fill="#F8FAFC" font-size="{size}">{esc(item)}</text>')
        baseline += size + 10
    return (
        f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="16" fill="#0C1222" stroke="#1E3A5F"/>'
        f'<rect x="{x}" y="{y}" width="{width}" height="36" rx="16" fill="url(#sheen)"/>'
        f'<rect x="{x}" y="{y + 18}" width="{width}" height="18" fill="#0C1222"/>'
        + "".join(rows)
    )


def tech_universe() -> None:
    w, h = 960, 640
    body = f"""
    {stage(w, h)}
    <g class="motion spin">
      <circle cx="480" cy="318" r="98" fill="none" stroke="#38BDF8" stroke-opacity="0.35" stroke-dasharray="3 8"/>
      <circle cx="578" cy="318" r="3.2" fill="#22D3EE"/>
    </g>
    <g class="motion spin-rev">
      <circle cx="480" cy="318" r="112" fill="none" stroke="#8B5CF6" stroke-opacity="0.28" stroke-dasharray="2 10"/>
      <circle cx="480" cy="206" r="2.8" fill="#C4B5FD"/>
    </g>
    <path d="M480 248 V192 M480 388 V466 M410 318 H374 M550 318 H586" stroke="#164E63" fill="none"/>
    {glass_card(255, 16, 450, 176, "MOBILE ENGINEERING", ["React Native", "Expo", "Android", "iOS"])}
    {glass_card(586, 214, 352, 208, "FRONTEND ENGINEERING", ["React", "Next.js", "Angular", "TypeScript"])}
    {glass_card(255, 466, 450, 150, "BACKEND & CLOUD", ["Node.js", "Firebase", "REST APIs"], 16)}
    {glass_card(22, 203, 352, 230, "TOOLS & ENGINEERING", ["Git", "GitHub", "VS Code", "Xcode", "Android Studio"])}
    <circle cx="480" cy="318" r="70" fill="#080B14" stroke="url(#accent)" stroke-width="1.5"/>
    <text x="480" y="312" text-anchor="middle" fill="#94A3B8" font-size="11" letter-spacing="1.6">SOFTWARE</text>
    <text x="480" y="332" text-anchor="middle" fill="#F8FAFC" font-size="13" letter-spacing="1.1">ENGINEERING</text>
    """
    save("tech-universe.svg", document(
        w, h,
        "My Tech Universe",
        "Software engineering across mobile, frontend, backend and cloud, and tools.",
        body,
    ))


def tech_compact() -> None:
    cards = [
        ("MOBILE ENGINEERING", ["React Native", "Expo", "Android", "iOS"]),
        ("FRONTEND ENGINEERING", ["React", "Next.js", "Angular", "TypeScript"]),
        ("BACKEND & CLOUD", ["Node.js", "Firebase", "REST APIs"]),
        ("TOOLS & ENGINEERING", ["Git", "GitHub", "VS Code", "Xcode", "Android Studio"]),
    ]
    y = 0
    blocks = []
    gap = 14
    for title, items in cards:
        height = 58 + len(items) * 28
        blocks.append(glass_card(0, y, 400, height, title, items, 18))
        y += height + gap
    save("tech-universe-compact.svg", document(
        400, y - gap,
        "My Tech Universe",
        "Software engineering across mobile, frontend, backend and cloud, and tools.",
        "\n".join(blocks),
    ))


def project_card(filename: str, index: str, category: str, name: str, summary: str) -> None:
    w, h = 880, 132
    body = f"""
    <g clip-path="url(#frame)">
      <rect width="{w}" height="{h}" fill="#080B14"/>
      <rect width="{w}" height="{h}" fill="url(#grid)" opacity="0.4"/>
      <rect width="{w}" height="64" fill="url(#sheen)"/>
      <rect width="5" height="{h}" fill="url(#accent)"/>
    </g>
    <rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="24" fill="none" stroke="#1E3A5F"/>
    <text x="32" y="48" fill="#8B5CF6" font-size="13" letter-spacing="1.6">{index}</text>
    <text x="848" y="48" text-anchor="end" fill="#22D3EE" font-size="12" letter-spacing="1.8">{esc(category)}</text>
    <text x="32" y="98" fill="#F8FAFC" font-size="34" font-weight="700" letter-spacing="0.8">{esc(name)}</text>
    """
    save(filename, document(w, h, name, summary, body))


def buttons() -> None:
    labels = [
        ("btn-portfolio.svg", "Portfolio", 156),
        ("btn-linkedin.svg", "LinkedIn", 150),
        ("btn-email.svg", "Email", 128),
        ("btn-github.svg", "GitHub", 140),
    ]
    for filename, label, width in labels:
        body = f"""
        <rect width="{width}" height="40" rx="20" fill="#0C1222" stroke="url(#accent)"/>
        <circle cx="18" cy="20" r="3" fill="#22D3EE"/>
        <text x="{width / 2 + 6}" y="25" text-anchor="middle" fill="#F8FAFC" font-size="14" letter-spacing="0.4">{label}</text>
        """
        save(filename, document(width, 40, label, label, body))


def footer(filename: str, width: int, height: int, title_size: int) -> None:
    body = f"""
    {stage(width, height)}
    <g class="motion spin">
      <circle cx="{width / 2}" cy="46" r="18" fill="none" stroke="#38BDF8" stroke-opacity="0.6"/>
      <circle cx="{width / 2 + 18}" cy="46" r="2.2" fill="#22D3EE"/>
    </g>
    <text x="{width / 2}" y="52" text-anchor="middle" fill="url(#accent)" font-size="16" font-weight="700">C</text>
    <text x="{width / 2}" y="{height - 28}" text-anchor="middle" fill="#94A3B8" font-size="{title_size}" letter-spacing="1.1">Designed &amp; Engineered by Cristiano Vieira</text>
    """
    save(filename, document(
        width, height,
        "Designed and Engineered by Cristiano Vieira",
        "Closing signature of the Developer OS profile.",
        body,
    ))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    hero()
    hero_mobile()
    terminal()
    terminal_mobile()
    digital_core()
    tech_universe()
    tech_compact()
    project_card(
        "project-jobtto.svg", "01", "MARKETPLACE", "JOBTTO",
        "Marketplace for hiring services and freelancers. Founded and engineered by Cristiano Vieira.",
    )
    project_card(
        "project-orderflow.svg", "02", "OPERATIONS", "ORDERFLOW",
        "Restaurant management for point of sale, delivery, and daily operations.",
    )
    project_card(
        "project-gauchotech.svg", "03", "STUDIO", "GAÚCHO TECH",
        "Digital studio for applications, websites, and business systems.",
    )
    project_card(
        "project-portfolio.svg", "04", "SELECTED WORK", "PORTFOLIO",
        "Personal portfolio of mobile and web work.",
    )
    buttons()
    footer("footer.svg", 880, 132, 16)
    footer("footer-mobile.svg", 400, 120, 13)
    print("static svgs written")


if __name__ == "__main__":
    main()
