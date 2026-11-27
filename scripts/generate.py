#!/usr/bin/env python3
"""Builds every SVG on the profile and refreshes the recent-projects block.

Standard library only. Environment:
    GH_USER        GitHub login (default: Ssajaia)
    GITHUB_TOKEN   optional, raises the API rate limit
"""
import json
import math
import os
import re
import textwrap
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from xml.sax.saxutils import escape

USER = os.environ.get("GH_USER", "Ssajaia")
TOKEN = os.environ.get("GITHUB_TOKEN")
ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
SANS = "'Avenir Next','Segoe UI','Helvetica Neue',Arial,sans-serif"

# Cyanotype blueprint (dark) and drafting paper (light).
THEMES = {
    "dark": dict(bg="#0a2f4a", panel="#0e3b5c", line="#2d6288", text="#eaf4fb",
                 muted="#9ec0d8", accent="#ffd166", accent2="#7dd3fc", ok="#6ee7b7"),
    "light": dict(bg="#eef3f6", panel="#ffffff", line="#b9cddb", text="#0c2b40",
                  muted="#4f6b80", accent="#0b5d8c", accent2="#b45309", ok="#0f766e"),
}

LANG_COLORS = {
    "Python": "#3572A5", "Go": "#00ADD8", "Rust": "#dea584", "C#": "#178600",
    "TypeScript": "#3178c6", "JavaScript": "#f1e05a", "Shell": "#89e051",
    "Java": "#b07219", "Kotlin": "#A97BFF", "C++": "#f34b7d", "Dart": "#00B4AB",
    "HCL": "#844FBA", "Dockerfile": "#384d54", "HTML": "#e34c26", "CSS": "#563d7c",
}


def wrap(w, h, title, body):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(title)}">
<title>{escape(title)}</title>
<style>
text{{font-family:{SANS}}}
.m{{font-family:{MONO}}}
@keyframes flow{{to{{stroke-dashoffset:-24}}}}
@keyframes pulse{{0%,100%{{opacity:.2}}50%{{opacity:1}}}}
@keyframes blink{{0%,49%{{opacity:1}}50%,100%{{opacity:0}}}}
@keyframes type{{from{{transform:scaleX(1)}}to{{transform:scaleX(0)}}}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}.cover{{display:none}}}}
</style>
{body}
</svg>
"""


def rnd(seed):
    x = math.sin(seed * 12.9898) * 43758.5453
    return x - math.floor(x)


# --------------------------------------------------------------- hero
def hero(t):
    W, H = 900, 250
    cmd = "terraform apply -auto-approve   # nah, I'd win"
    cw = 9.6
    tw = len(cmd) * cw
    x0 = 82
    p = [
        f'<defs><pattern id="g" width="30" height="30" patternUnits="userSpaceOnUse">'
        f'<path d="M30 0H0V30" fill="none" stroke="{t["line"]}" stroke-width=".6" opacity=".7"/></pattern></defs>',
        f'<rect width="{W}" height="{H}" rx="14" fill="{t["bg"]}"/>',
        f'<rect width="{W}" height="{H}" rx="14" fill="url(#g)"/>',
        f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="14" fill="none" stroke="{t["line"]}"/>',
        f'<text x="40" y="96" font-size="48" font-weight="800" fill="{t["text"]}">Saba Sajaia</text>',
        f'<text x="40" y="132" font-size="19" fill="{t["accent"]}">Junior DevOps Engineer at EPAM Systems</text>',
        f'<rect x="40" y="158" width="{tw+70:.0f}" height="42" rx="8" fill="{t["panel"]}" stroke="{t["line"]}"/>',
        f'<text class="m" x="56" y="185" font-size="16" fill="{t["ok"]}">$</text>',
        f'<text class="m" x="{x0}" y="185" font-size="16" fill="{t["text"]}">{escape(cmd)}</text>',
        f'<rect class="cover" x="{x0}" y="168" width="{tw:.0f}" height="24" fill="{t["panel"]}" '
        f'style="transform-origin:{x0+tw:.0f}px 180px;animation:type 3.4s steps({len(cmd)}) .8s forwards"/>',
        f'<rect x="{x0+tw+3:.0f}" y="169" width="9" height="22" fill="{t["accent"]}" '
        f'style="animation:blink 1s step-end infinite"/>',
    ]
    nodes = {"AWS": (640, 70), "VPC": (760, 48), "K8s": (842, 112),
             "IAM": (722, 130), "CI": (664, 196), "TF": (800, 200)}
    edges = [("AWS", "VPC"), ("VPC", "K8s"), ("AWS", "IAM"), ("IAM", "K8s"),
             ("IAM", "CI"), ("IAM", "TF"), ("CI", "TF"), ("K8s", "TF")]
    for a, b in edges:
        (x1, y1), (x2, y2) = nodes[a], nodes[b]
        p.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{t["accent2"]}" '
                 f'stroke-opacity=".7" stroke-width="1.5" stroke-dasharray="4 8" '
                 f'style="animation:flow 1.4s linear infinite"/>')
    for i, (name, (x, y)) in enumerate(nodes.items()):
        p.append(f'<circle cx="{x}" cy="{y}" r="26" fill="none" stroke="{t["accent"]}" '
                 f'style="animation:pulse 3.2s ease-in-out {i*0.55:.2f}s infinite"/>')
        p.append(f'<circle cx="{x}" cy="{y}" r="18" fill="{t["panel"]}" stroke="{t["accent2"]}" stroke-width="1.5"/>')
        p.append(f'<text class="m" x="{x}" y="{y+4}" text-anchor="middle" font-size="11" fill="{t["text"]}">{name}</text>')
    return wrap(W, H, "Saba Sajaia, Junior DevOps Engineer at EPAM Systems", "\n".join(p))


# -------------------------------------------------------------- stack
STACK = [
    ("write", ["Python", "Go", "Rust", "C#", "TypeScript"]),
    ("ship", ["GitHub Actions", "GitLab CI", "Jenkins", "Ansible", "Bash"]),
    ("provision", ["Terraform", "AWS", "Docker", "Kubernetes", "Git"]),
    ("run", ["Linux (Fedora)", "PostgreSQL", "DynamoDB", "MongoDB", "MS SQL Server"]),
]


def stack(t):
    W, H = 900, 300
    p = [
        f'<rect width="{W}" height="{H}" rx="14" fill="{t["bg"]}"/>',
        f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="14" fill="none" stroke="{t["line"]}"/>',
        f'<line x1="30" y1="54" x2="870" y2="54" stroke="{t["accent2"]}" stroke-opacity=".7" '
        f'stroke-width="1.5" stroke-dasharray="4 8" style="animation:flow 1.6s linear infinite"/>',
    ]
    for b in (0, 1.7, 3.4):
        p.append(f'<circle r="4.5" cy="0" fill="{t["accent"]}"><animateMotion dur="5.1s" begin="{b}s" '
                 f'repeatCount="indefinite" path="M30 54 H870"/></circle>')
    for i, (head, items) in enumerate(STACK):
        x0 = 30 + i * 220
        p.append(f'<text x="{x0}" y="36" font-size="17" font-weight="700" fill="{t["accent"]}">{head}</text>')
        for j, item in enumerate(items):
            y = 76 + j * 44
            p.append(f'<rect x="{x0}" y="{y}" width="200" height="34" rx="8" fill="{t["panel"]}" stroke="{t["line"]}"/>')
            p.append(f'<circle cx="{x0+16}" cy="{y+17}" r="4" fill="{t["ok"]}" '
                     f'style="animation:pulse 3s ease-in-out {(i*5+j)*0.2:.1f}s infinite"/>')
            p.append(f'<text x="{x0+30}" y="{y+22}" font-size="14" fill="{t["text"]}">{escape(item)}</text>')
    return wrap(W, H, "Tech stack: write, ship, provision, run", "\n".join(p))


# ------------------------------------------------------------- cards
def ago(iso):
    s = int((datetime.now(timezone.utc) - datetime.fromisoformat(iso.replace("Z", "+00:00"))).total_seconds())
    for size, unit in ((31536000, "y"), (2592000, "mo"), (86400, "d"), (3600, "h")):
        if s >= size:
            return f"{s // size}{unit} ago"
    return "just now"


def card(repo, t):
    W, H = 440, 124
    lang = repo.get("language") or "no language"
    color = LANG_COLORS.get(repo.get("language") or "", t["muted"])
    desc = repo.get("description") or "No description yet. Mystery box."
    lines = textwrap.wrap(desc, 50)
    if len(lines) > 2:
        lines = [lines[0], lines[1][:47].rstrip() + "…"]
    name = repo["name"] if len(repo["name"]) <= 28 else repo["name"][:27] + "…"
    p = [
        f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="12" fill="{t["panel"]}" stroke="{t["line"]}"/>',
        f'<rect x="12" y="16" width="3" height="{H-32}" rx="1.5" fill="{color}"/>',
        f'<text x="28" y="35" font-size="18" font-weight="700" fill="{t["accent"]}">{escape(name)}</text>',
        f'<text class="m" x="{W-20}" y="34" text-anchor="end" font-size="13" fill="{t["muted"]}">★ {repo.get("stargazers_count", 0)}</text>',
    ]
    for k, line in enumerate(lines):
        p.append(f'<text x="28" y="{62 + k*20}" font-size="13" fill="{t["text"]}">{escape(line)}</text>')
    p += [
        f'<circle cx="32" cy="{H-20}" r="5" fill="{color}"/>',
        f'<text class="m" x="44" y="{H-16}" font-size="12" fill="{t["muted"]}">{escape(lang)}</text>',
        f'<text class="m" x="{W-20}" y="{H-16}" text-anchor="end" font-size="12" fill="{t["muted"]}">pushed {ago(repo["pushed_at"])}</text>',
    ]
    return wrap(W, H, f"Repository {repo['name']}", "\n".join(p))


def recent_repos():
    url = f"https://api.github.com/users/{USER}/repos?per_page=100&sort=pushed&type=owner"
    headers = {"User-Agent": "profile-readme-builder", "Accept": "application/vnd.github+json"}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as r:
            repos = json.load(r)
    except Exception as err:  # keep the previous cards if the API is unavailable
        print("repo fetch failed:", err)
        return []
    keep = [r for r in repos if not r["fork"] and not r["archived"] and r["name"].lower() != USER.lower()]
    return keep[:4]


def picture(src, alt, width):
    return (f'<picture><source media="(prefers-color-scheme: dark)" srcset="assets/{src}-dark.svg">'
            f'<source media="(prefers-color-scheme: light)" srcset="assets/{src}-light.svg">'
            f'<img alt="{escape(alt, {chr(34): "&quot;"})}" src="assets/{src}-dark.svg" width="{width}"></picture>')


def update_projects(repos):
    for old in ASSETS.glob("project-*.svg"):
        old.unlink()
    cells = []
    for i, repo in enumerate(repos):
        for name, t in THEMES.items():
            (ASSETS / f"project-{i}-{name}.svg").write_text(card(repo, t), encoding="utf-8")
        cells.append(f'<a href="{repo["html_url"]}">{picture(f"project-{i}", repo["name"], "49%")}</a>')
    block = '<p align="center">\n' + "\n".join(cells) + "\n</p>"
    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    new = re.sub(r"(<!-- PROJECTS:START -->).*?(<!-- PROJECTS:END -->)",
                 lambda m: f"{m.group(1)}\n{block}\n{m.group(2)}", text, flags=re.S)
    readme.write_text(new, encoding="utf-8")


# ------------------------------------------------------------- scene
def scene():
    now = datetime.now(timezone(timedelta(hours=4)))  # Tbilisi, no DST
    h = now.hour + now.minute / 60
    phase = "night" if (h < 5 or h >= 21) else "dawn" if h < 8 else "day" if h < 17 else "dusk"
    sky = {"night": ("#050816", "#17204a"), "dawn": ("#3b3a7a", "#f6b26b"),
           "day": ("#3d9be0", "#cfeeff"), "dusk": ("#3a2a66", "#f2874b")}[phase]
    ridge = {"night": ("#0d1430", "#070a1a"), "dawn": ("#51457f", "#2b2550"),
             "day": ("#7396c0", "#4d6f99"), "dusk": ("#5f4380", "#30224a")}[phase]
    city = {"night": "#0a0f24", "dawn": "#2a2350", "day": "#3b5a82", "dusk": "#241a3d"}[phase]
    caption = {"night": "Night shift. The servers sleep. I allegedly do too.",
               "dawn": "Sunrise over the Caucasus. Coffee is deploying.",
               "day": "Daytime. Pipelines are green. Allegedly.",
               "dusk": "Golden hour. Strong deploy-freeze energy."}[phase]
    ink = "#0f2a4a" if phase == "day" else "#eef3ff"
    W, H = 900, 220
    p = [
        f'<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{sky[0]}"/><stop offset="1" stop-color="{sky[1]}"/></linearGradient>'
        f'<clipPath id="r"><rect width="{W}" height="{H}" rx="14"/></clipPath></defs>',
        '<g clip-path="url(#r)">',
        f'<rect width="{W}" height="{H}" fill="url(#sky)"/>',
    ]
    if phase != "day":
        for i in range(44 if phase == "night" else 14):
            p.append(f'<circle cx="{rnd(i)*880+10:.0f}" cy="{rnd(i+100)*110+8:.0f}" r="{0.8+rnd(i+200)*1.2:.1f}" '
                     f'fill="#fff" style="animation:pulse {2+rnd(i+300)*3:.1f}s ease-in-out {rnd(i+400)*3:.1f}s infinite"/>')
    if 6 <= h < 20:
        pr = (h - 6) / 14
        sx, sy = 70 + pr * 760, 175 - math.sin(math.pi * pr) * 55
        col = "#ffd54a" if phase == "day" else "#ff9a3c"
        p += [f'<circle cx="{sx:.0f}" cy="{sy:.0f}" r="38" fill="{col}" opacity=".25"/>',
              f'<circle cx="{sx:.0f}" cy="{sy:.0f}" r="22" fill="{col}"/>']
    else:
        q = min(max(((h - 20) % 24) / 10, 0), 1)
        mx, my = 70 + q * 760, 175 - math.sin(math.pi * q) * 55
        p += [f'<mask id="mm"><rect x="{mx-30:.0f}" y="{my-30:.0f}" width="60" height="60" fill="#fff"/>'
              f'<circle cx="{mx+8:.0f}" cy="{my-4:.0f}" r="16" fill="#000"/></mask>',
              f'<circle cx="{mx:.0f}" cy="{my:.0f}" r="34" fill="#f4f1de" opacity=".08"/>',
              f'<circle cx="{mx:.0f}" cy="{my:.0f}" r="18" fill="#f4f1de" mask="url(#mm)"/>']
    p += [
        f'<path d="M0 190 L90 130 L160 165 L260 100 L350 160 L450 120 L560 170 L680 105 L780 150 L860 125 L900 150 V220 H0Z" fill="{ridge[0]}"/>',
        f'<path d="M0 205 L120 165 L220 195 L340 150 L470 200 L600 160 L730 200 L830 170 L900 195 V220 H0Z" fill="{ridge[1]}"/>',
    ]
    x, i = 540, 0
    while x < 870:
        bw, bh = 16 + int(rnd(i + 300) * 14), 14 + int(rnd(i + 400) * 26)
        by = 218 - bh
        p.append(f'<rect x="{x}" y="{by}" width="{bw}" height="{bh}" fill="{city}"/>')
        if phase != "day":
            for wy in range(by + 4, 214, 8):
                for wx in (x + 3, x + bw - 6):
                    if rnd(wx * 7 + wy) > 0.45:
                        p.append(f'<rect x="{wx}" y="{wy}" width="3" height="3" fill="#ffd479" '
                                 f'style="animation:pulse {3+rnd(wx+wy)*4:.1f}s ease-in-out {rnd(wy)*3:.1f}s infinite"/>')
        x += bw + 3
        i += 1
    p += [
        f'<text x="36" y="50" font-size="14" fill="{ink}" opacity=".85">Tbilisi, Georgia (UTC+4)</text>',
        f'<text x="36" y="82" font-size="21" font-weight="700" fill="{ink}">{escape(caption)}</text>',
        '</g>',
        f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="14" fill="none" stroke="{ink}" stroke-opacity=".25"/>',
    ]
    return wrap(W, H, f"Tbilisi sky, currently {phase}", "\n".join(p))


def main():
    ASSETS.mkdir(exist_ok=True)
    for name, t in THEMES.items():
        (ASSETS / f"hero-{name}.svg").write_text(hero(t), encoding="utf-8")
        (ASSETS / f"stack-{name}.svg").write_text(stack(t), encoding="utf-8")
    (ASSETS / "tbilisi.svg").write_text(scene(), encoding="utf-8")
    repos = recent_repos()
    if repos:
        update_projects(repos)
    print(f"done: {len(repos)} project cards")


if __name__ == "__main__":
    main()
