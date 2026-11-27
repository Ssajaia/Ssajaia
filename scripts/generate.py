#!/usr/bin/env python3
"""Builds the hero and stack SVG assets used by the profile README.

Run it by hand to refresh those assets, then commit the result:
    python scripts/generate.py

Standard library only.
"""
import math
import textwrap
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"
SANS = "'Avenir Next','Segoe UI','Helvetica Neue',Arial,sans-serif"

# Colours follow GitHub's dark theme.
THEMES = {
    "dark": dict(bg="#161b22", panel="#21262d", line="#30363d", text="#e6edf3",
                 muted="#8b949e", accent="#ffd166", accent2="#58a6ff", ok="#56d364"),
}

LANG_COLORS = {
    "Python": "#3572A5", "Go": "#00ADD8", "Rust": "#dea584", "C#": "#178600",
    "TypeScript": "#3178c6", "JavaScript": "#f1e05a", "Shell": "#89e051",
    "Java": "#b07219", "Kotlin": "#A97BFF", "C++": "#f34b7d", "Dart": "#00B4AB",
    "HCL": "#844FBA", "Dockerfile": "#384d54", "HTML": "#e34c26", "CSS": "#563d7c",
}


def wrap(w, h, title, body, css=""):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(title)}">
<title>{escape(title)}</title>
<style>
text{{font-family:{SANS}}}
.m{{font-family:{MONO}}}
@keyframes flow{{to{{stroke-dashoffset:-24}}}}
@keyframes pulse{{0%,100%{{opacity:.2}}50%{{opacity:1}}}}
@keyframes blink{{0%,49%{{opacity:1}}50%,100%{{opacity:0}}}}
@keyframes type{{from{{transform:scaleX(1)}}to{{transform:scaleX(0)}}}}
{css}
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
    cmd = "terraform apply -auto-approve   # nah, I'd Apply"
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
    nodes = {"AWS": (636, 62), "GCP": (748, 44), "AZ": (846, 92), "K8s": (722, 124),
             "CI": (664, 196), "TF": (790, 200), "ANS": (850, 158)}
    edges = [("AWS", "GCP"), ("GCP", "AZ"), ("AWS", "K8s"), ("GCP", "K8s"), ("AZ", "K8s"),
             ("K8s", "CI"), ("K8s", "TF"), ("CI", "TF"), ("TF", "ANS"), ("AZ", "ANS")]
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
    ("write", ["Python", "Go", "Rust", "C#","C++","C","Assembly", "TypeScript","Javascript"]),
    ("ship", ["GitHub Actions", "GitLab CI", "Jenkins", "Bash", "Git"]),
    ("provision", ["Terraform", "Ansible", "Docker", "Kubernetes"]),
    ("cloud", ["AWS", "Azure", "GCP"]),
    ("run", ["PostgreSQL", "DynamoDB", "MongoDB", "MS SQL Server"]),
    ("OS", ["Arch","OpenBSD","FreeBSD","Fedora","Mint","Windows","MacOS"]), 
]


def stack(t):
    # Keep every current category and item inside the viewBox.
    W, H = 1080, 482
    p = [
        f'<rect width="{W}" height="{H}" rx="14" fill="{t["bg"]}"/>',
        f'<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="14" fill="none" stroke="{t["line"]}"/>',
        f'<line x1="20" y1="54" x2="1060" y2="54" stroke="{t["accent2"]}" stroke-opacity=".7" '
        f'stroke-width="1.5" stroke-dasharray="4 8" style="animation:flow 1.6s linear infinite"/>',
    ]
    for b in (0, 1.7, 3.4):
        p.append(f'<circle r="4.5" cy="0" fill="{t["accent"]}"><animateMotion dur="5.1s" begin="{b}s" '
                 f'repeatCount="indefinite" path="M20 54 H1060"/></circle>')
    for i, (head, items) in enumerate(STACK):
        x0 = 20 + i * 175
        p.append(f'<text x="{x0}" y="36" font-size="17" font-weight="700" fill="{t["accent"]}">{head}</text>')
        for j, item in enumerate(items):
            y = 76 + j * 44
            p.append(f'<rect x="{x0}" y="{y}" width="160" height="34" rx="8" fill="{t["panel"]}" stroke="{t["line"]}"/>')
            p.append(f'<circle cx="{x0+16}" cy="{y+17}" r="4" fill="{t["ok"]}" '
                     f'style="animation:pulse 3s ease-in-out {(i*5+j)*0.2:.1f}s infinite"/>')
            p.append(f'<text x="{x0+30}" y="{y+22}" font-size="14" fill="{t["text"]}">{escape(item)}</text>')
    return wrap(W, H, "Tech stack: write, ship, provision, cloud, run, and operating systems", "\n".join(p))


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


def main():
    ASSETS.mkdir(exist_ok=True)
    t = THEMES["dark"]
    (ASSETS / "hero-dark.svg").write_text(hero(t), encoding="utf-8")
    (ASSETS / "stack-dark.svg").write_text(stack(t), encoding="utf-8")
    print("done: dark hero and stack assets")


if __name__ == "__main__":
    main()
