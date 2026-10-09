#!/usr/bin/env python3
"""Render assets/dashboard.svg from config.json + data/stats.json (stdlib only)."""
import html
import json
import math
import pathlib
import textwrap

ROOT = pathlib.Path(__file__).resolve().parent.parent
cfg = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
st = json.loads((ROOT / "data" / "stats.json").read_text(encoding="utf-8"))

W, H = 1312, 1200
CY, TEAL = "#22d3ee", "#2dd4bf"
TXT, MUTED, WHITE = "#cfe3ee", "#8fb0c0", "#ffffff"
FONT = "'Segoe UI', 'Helvetica Neue', Arial, sans-serif"
SCRIPT = "'Segoe Script', 'Brush Script MT', 'Comic Sans MS', cursive"
HEAT = ["#12303a", "#0e5a43", "#12804f", "#22b866", "#39e07e"]

o = []


def esc(s):
    return html.escape(str(s), quote=True)


def fmt(n):
    return f"{int(n):,}"


def T(x, y, s, size=13, fill=TXT, weight=400, anchor="start", extra=""):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" '
            f'font-weight="{weight}" text-anchor="{anchor}" {extra}>{esc(s)}</text>')


def TL(x, y, s, n, lh, size=12, fill=MUTED, weight=400, anchor="start"):
    lines = textwrap.wrap(s, n) or [""]
    return "".join(T(x, y + i * lh, ln, size, fill, weight, anchor) for i, ln in enumerate(lines))


def R(x, y, w, h, rx=0, fill="none", stroke=None, sw=1, extra=""):
    s = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"{s} {extra}/>'


def lum(hexc):
    h = hexc.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return 0.299 * r + 0.587 * g + 0.114 * b


# ------------------------------------------------------------------ defs / background
o.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
         f'font-family="{FONT}" role="img" aria-label="{esc(cfg["name"])} developer dashboard">')
o.append("""<defs>
<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#04141f"/><stop offset="1" stop-color="#030e17"/></linearGradient>
<linearGradient id="hdr" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#06303a"/><stop offset="0.5" stop-color="#062033"/><stop offset="1" stop-color="#05283a"/></linearGradient>
<radialGradient id="glow" cx="0.3" cy="0.4" r="0.6"><stop offset="0" stop-color="#14b8a6" stop-opacity="0.28"/><stop offset="1" stop-color="#14b8a6" stop-opacity="0"/></radialGradient>
<linearGradient id="card" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#082234"/><stop offset="1" stop-color="#061a28"/></linearGradient>
</defs>""")
o.append(f'<rect width="{W}" height="{H}" fill="url(#bg)"/>')

# ------------------------------------------------------------------ header
o.append(f'<rect width="{W}" height="220" fill="url(#hdr)"/><rect width="{W}" height="220" fill="url(#glow)"/>')
o.append('<path d="M0 190 C200 140 420 235 700 175 S1100 115 1312 160 L1312 220 L0 220Z" fill="#14b8a6" opacity="0.12"/>')
o.append('<path d="M0 205 C250 170 480 225 760 195 S1150 150 1312 185 L1312 220 L0 220Z" fill="#22d3ee" opacity="0.10"/>')
o.append(f'<rect y="219" width="{W}" height="2" fill="{CY}" opacity="0.55"/>')

hs = cfg["header_small"]
o.append(T(46, 38, hs[0], 15, "#7fd6e6", 400, extra='font-style="italic" letter-spacing="1.5"'))
o.append(T(46, 60, hs[1], 15, "#7fd6e6", 400, extra='font-style="italic" letter-spacing="1.5"'))

first, _, last = cfg["name"].partition(" ")
o.append(T(445, 56, "Hi, I'm", 40, TXT, 400, extra='font-style="italic" font-family="Georgia, serif"'))
o.append(f'<text x="445" y="113" font-size="58" font-weight="700" fill="{WHITE}">{esc(first)} '
         f'<tspan fill="{CY}">{esc(last)}</tspan></text>')
roles = f' <tspan fill="{MUTED}" font-weight="400">  |  </tspan>'.join(
    f'<tspan fill="{CY}" font-weight="600">{esc(r)}</tspan>' for r in cfg["roles"])
o.append(f'<text x="445" y="143" font-size="12.5" letter-spacing="0.6">{roles}</text>')
o.append(T(445, 175, cfg["tagline"][0], 14.5, TXT))
o.append(T(445, 198, cfg["tagline"][1], 14.5, TXT))

# laptop + books + mug + plant (left)
o.append(R(92, 86, 160, 100, 7, "#0a1d2c", "#27506a", 2))
for i, (w_, c) in enumerate([(70, "#38bdf8"), (45, "#f472b6"), (90, "#34d399"), (60, "#fbbf24"),
                             (80, "#38bdf8"), (35, "#a78bfa"), (65, "#34d399"), (50, "#f472b6")]):
    o.append(R(104 + (i % 2) * 14, 96 + i * 10, w_, 4, 2, c, extra='opacity="0.8"'))
o.append('<path d="M70 190 L274 190 L262 200 L82 200Z" fill="#1b3446"/>')
for i, (t, c) in enumerate([("Data Analytics", "#0f3a52"), ("PostgreSQL", "#0c3550"), ("FastAPI", "#103a50"), ("Python", "#0f3d57")]):
    y = 168 - i * 20
    o.append(R(272, y, 120, 19, 3, c, "#2a6c8c", 1))
    o.append(T(282, y + 13.5, t, 11.5, "#8fd3ea"))
o.append(R(400, 150, 38, 40, 5, "#0b2230", "#2a6c8c", 1.5))
o.append('<path d="M438 160 q16 3 0 20" stroke="#2a6c8c" stroke-width="3" fill="none"/>')
o.append('<ellipse cx="40" cy="150" rx="14" ry="30" fill="#0f766e" opacity="0.9" transform="rotate(-20 40 150)"/>'
         '<ellipse cx="62" cy="145" rx="12" ry="28" fill="#14b8a6" opacity="0.8" transform="rotate(18 62 145)"/>'
         '<rect x="38" y="172" width="34" height="30" rx="4" fill="#12394a"/>')

# charts + database (right)
o.append(R(1012, 34, 132, 84, 8, "#0a2a40", "#2a6c8c", 1.5, 'opacity="0.95"'))
for i, hgt in enumerate([18, 30, 24, 40, 33, 50]):
    o.append(R(1026 + i * 18, 106 - hgt, 11, hgt, 2, "#38bdf8", extra='opacity="0.9"'))
o.append('<circle cx="1182" cy="64" r="24" fill="#22b8dc"/>'
         '<path d="M1182 64 L1182 40 A24 24 0 0 1 1206 64Z" fill="#0b2a3c"/>')
o.append(R(1046, 128, 132, 84, 8, "#0a2a40", "#2a6c8c", 1.5, 'opacity="0.95"'))
o.append('<polyline points="1056,198 1080,176 1102,186 1128,156 1150,164 1168,142" fill="none" stroke="#2dd4bf" stroke-width="3"/>')
for i, hgt in enumerate([10, 16, 13, 22, 19, 27, 23]):
    o.append(R(1056 + i * 16, 204 - hgt, 9, hgt, 2, "#22d3ee", extra='opacity="0.4"'))
o.append('<ellipse cx="980" cy="192" rx="28" ry="8" fill="#22d3ee"/>'
         '<rect x="952" y="152" width="56" height="40" fill="#0e7490"/>'
         '<ellipse cx="980" cy="172" rx="28" ry="8" fill="none" stroke="#67e8f9" opacity="0.6"/>'
         '<ellipse cx="980" cy="152" rx="28" ry="8" fill="#67e8f9"/>'
         '<rect x="952" y="132" width="56" height="20" fill="#0891b2"/>'
         '<ellipse cx="980" cy="132" rx="28" ry="8" fill="#67e8f9"/>')
mot = cfg["header_motto"]
for i, wd in enumerate(mot):
    o.append(T(1214 + i * 3, 96 + i * 22, wd, 20, WHITE if i % 2 else CY, 400,
               extra=f'font-style="italic" font-family="{SCRIPT}" transform="rotate(-12 1214 96)"'))
o.append(f'<path d="M1214 178 q28 -8 56 -20" stroke="{TEAL}" stroke-width="2" fill="none"/>')

# ------------------------------------------------------------------ About Me
o.append(f'<circle cx="42" cy="249" r="7" fill="{TEAL}"/><path d="M28 272 q14 -26 28 0Z" fill="{TEAL}"/>')
o.append(T(70, 260, "About Me", 20, WHITE, 600))
o.append(TL(30, 287, cfg["about"], 52, 19.5, 13.5, TXT))
fy = 416
for label, val in cfg["facts"]:
    lines = textwrap.wrap(f"{label} {val}", 50)
    o.append(f'<circle cx="40" cy="{fy - 5}" r="9" fill="none" stroke="{TEAL}" stroke-width="2"/>'
             f'<circle cx="40" cy="{fy - 5}" r="3.5" fill="{TEAL}"/>')
    first_rest = lines[0][len(label):].strip() if lines[0].startswith(label) else lines[0]
    o.append(f'<text x="58" y="{fy}" font-size="12.5" fill="{TXT}"><tspan fill="{TEAL}" font-weight="600">{esc(label)} </tspan>{esc(first_rest)}</text>')
    for k, ln in enumerate(lines[1:], 1):
        o.append(T(58, fy + k * 16, ln, 12.5, TXT))
    fy += 30 + (len(lines) - 1) * 16

# ------------------------------------------------------------------ Tech stack
o.append(f'<path d="M482 246 l18 18 M500 246 l-18 18" stroke="{TEAL}" stroke-width="4" stroke-linecap="round"/>')
o.append(T(512, 260, "Tech Stack", 20, TEAL, 600))
GX, GW = 478, 528
y = 270
for g in cfg["tech_stack"]:
    px = GX + 18
    cx, row, placed = px, 0, []
    for name, color in g["items"]:
        pw = int(46 + len(name) * 7.0)
        if cx + pw > GX + GW - 14 and cx > px:
            row, cx = row + 1, px
        placed.append((name, color, cx, row, pw))
        cx += pw + 9
    gh = (row + 1) * 34 + 22
    o.append(R(GX, y, GW, gh, 12, "#071e2b", "#12303f"))
    o.append(T(GX + 18, y + 17, g["title"], 11.5, TEAL, 700))
    for name, color, x_, r_, pw in placed:
        py = y + 25 + r_ * 34
        o.append(R(x_, py, pw, 26, 13, "#0c2b3b", "#1a4357"))
        o.append(f'<circle cx="{x_ + 15}" cy="{py + 13}" r="9" fill="{color}" stroke="#2a6c8c" stroke-width="0.8"/>')
        o.append(T(x_ + 15, py + 17, name[0].upper(), 10, "#0b1620" if lum(color) > 150 else WHITE, 700, "middle"))
        o.append(T(x_ + 30, py + 17.5, name, 12.5, TXT))
    y += gh + 8

# ------------------------------------------------------------------ right column
o.append('<rect x="1030" y="240" width="1" height="370" fill="#12303f"/>')
yy = 262
for key, c in (("education", "#2dd4bf"), ("focus", "#22d3ee"), ("interests", "#2dd4bf")):
    blk = cfg[key]
    o.append(f'<circle cx="1062" cy="{yy - 5}" r="10" fill="none" stroke="{c}" stroke-width="2.5"/>'
             f'<circle cx="1062" cy="{yy - 5}" r="3.5" fill="{c}"/>')
    o.append(T(1084, yy, blk["title"], 15, WHITE, 600))
    ly = yy + 23
    for ln in blk["lines"]:
        for w_ in textwrap.wrap(ln, 31):
            o.append(T(1084, ly, w_, 11.5, CY if ln.startswith("(") else MUTED))
            ly += 17
    yy = ly + 22
for i, ln in enumerate(cfg["side_quote"]):
    o.append(T(1094 + i * 10, max(yy, 520) + 8 + i * 22, ln if i == 0 else ln, 17, TEAL, 400,
               extra=f'font-style="italic" font-family="{SCRIPT}" transform="rotate(-8 1094 {max(yy, 520) + 8})"'))

# ------------------------------------------------------------------ Featured projects
o.append('<rect x="30" y="632" width="1252" height="1" fill="#12303f"/>')
o.append(f'<path d="M32 652 h12 l3 4 h18 v20 h-33Z" fill="{TEAL}"/>')
o.append(T(70, 668, "Featured Projects", 20, WHITE, 600))
o.append(T(1282, 668, "View all projects →", 13, CY, 400, "end"))


def mock(kind, x, y):
    s = [R(x, y, 100, 122, 9, "#08192a", "#2a6c8c", 1.5)]
    if kind == "phone":
        s += [R(x + 20, y + 4, 60, 8, 4, "#020a12"), R(x + 12, y + 24, 56, 18, 8, "#1e3a5f"),
              R(x + 32, y + 50, 56, 18, 8, "#2563eb"), R(x + 12, y + 76, 44, 18, 8, "#1e3a5f"),
              R(x + 14, y + 104, 72, 10, 5, "#0e2a3f")]
    elif kind == "shop":
        s += [R(x + 6, y + 8, 88, 10, 3, "#0e2a3f"), R(x + 6, y + 24, 88, 24, 4, "#16a34a", extra='opacity="0.7"'),
              R(x + 8, y + 58, 38, 28, 4, "#334155"), R(x + 54, y + 58, 38, 28, 4, "#dc2626", extra='opacity="0.8"'),
              R(x + 8, y + 92, 38, 22, 4, "#475569"), R(x + 54, y + 92, 38, 22, 4, "#2563eb", extra='opacity="0.8"')]
    else:
        s += [R(x + 6, y + 8, 88, 8, 3, "#0e2a3f"), R(x + 6, y + 24, 42, 8, 3, "#22d3ee", extra='opacity="0.6"'),
              R(x + 6, y + 40, 88, 30, 5, "#134e4a"), R(x + 6, y + 78, 40, 36, 5, "#0e2a3f"),
              R(x + 52, y + 78, 42, 36, 5, "#0e2a3f"),
              T(x + 10, y + 58, "Made Simple", 9, WHITE, 600)]
    return "".join(s)


CW, CX0, CY0, CH = 410, 30, 680, 196
for i, p in enumerate(cfg["projects"]):
    cx0 = CX0 + i * (CW + 11)
    o.append(R(cx0, CY0, CW, CH, 6, "url(#card)", "#0f766e", 1.2))
    o.append(R(cx0 + 18, CY0 + 18, 44, 44, 10, p["color"]))
    o.append(T(cx0 + 40, CY0 + 48, p["name"][0].upper(), 22, WHITE, 700, "middle"))
    o.append(T(cx0 + 74, CY0 + 46, p["name"], 15, WHITE, 600))
    nm_w = len(p["name"]) * 9.8
    done = p["status"].lower().startswith("comp")
    sc = "#34d399" if done else "#38bdf8"
    bw = int(len(p["status"]) * 6.4 + 20)
    o.append(R(cx0 + 74 + nm_w + 8, CY0 + 31, bw, 20, 10, "none", sc, 1))
    o.append(T(cx0 + 74 + nm_w + 8 + bw / 2, CY0 + 45, p["status"], 10.5, sc, 400, "middle"))
    o.append(TL(cx0 + 18, CY0 + 84, p["description"], 38, 15, 11.5, TXT))
    tx = cx0 + 18
    for tag, tc in p["tags"]:
        tw = int(len(tag) * 6.3 + 18)
        o.append(R(tx, CY0 + 148, tw, 20, 10, "#0b2a3b", tc, 0.8))
        o.append(T(tx + tw / 2, CY0 + 162, tag, 10.5, tc, 400, "middle"))
        tx += tw + 6
    o.append(f'<circle cx="{cx0 + 26}" cy="{CY0 + 180}" r="8" fill="none" stroke="{TXT}" stroke-width="1.6"/>'
             f'<circle cx="{cx0 + 26}" cy="{CY0 + 180}" r="3" fill="{TXT}"/>')
    o.append(T(cx0 + 42, CY0 + 184, "View Repository →", 12, TXT))
    o.append(mock(p.get("mock", "browser"), cx0 + CW - 118, CY0 + 18))

# ------------------------------------------------------------------ Workflow
o.append('<rect x="30" y="885" width="1252" height="1" fill="#12303f"/>')
for i, hgt in enumerate([12, 20, 28]):
    o.append(R(34 + i * 9, 918 - hgt, 6, hgt, 2, TEAL))
o.append(T(70, 916, "Data Analytics Workflow", 17, WHITE, 600))
STEP_COL = ["#14b8a6", "#22c55e", "#a3b81a", "#2563eb", "#d99a1e"]


def step_icon(i, cx, cy):
    c = WHITE
    if i == 0:
        return f'<path d="M{cx} {cy-12} l3 9 9 3 -9 3 -3 9 -3 -9 -9 -3 9 -3Z" fill="{c}"/>'
    if i == 1:
        return (f'<circle cx="{cx-3}" cy="{cy-3}" r="8" fill="none" stroke="{c}" stroke-width="2.5"/>'
                f'<path d="M{cx+3} {cy+3} l8 8" stroke="{c}" stroke-width="3" stroke-linecap="round"/>')
    if i == 2:
        return (f'<ellipse cx="{cx}" cy="{cy-9}" rx="10" ry="4" fill="{c}"/><rect x="{cx-10}" y="{cy-9}" width="20" height="18" fill="{c}" opacity="0.7"/>'
                f'<ellipse cx="{cx}" cy="{cy+9}" rx="10" ry="4" fill="{c}"/>')
    if i == 3:
        return "".join(R(cx - 11 + k * 8, cy + 10 - h_, 6, h_, 1.5, c) for k, h_ in enumerate([10, 18, 26]))
    return (f'<circle cx="{cx}" cy="{cy-3}" r="9" fill="{c}"/><rect x="{cx-4}" y="{cy+6}" width="8" height="6" rx="2" fill="{c}"/>')


for i, (title, desc) in enumerate(cfg["workflow"]):
    x0 = 34 + i * 137
    cx, cy = x0 + 45, 948
    o.append(f'<circle cx="{cx}" cy="{cy}" r="27" fill="{STEP_COL[i]}" opacity="0.28"/>'
             f'<circle cx="{cx}" cy="{cy}" r="27" fill="none" stroke="{STEP_COL[i]}" stroke-width="2"/>')
    o.append(step_icon(i, cx, cy))
    if i < 4:
        ax = cx + 52
        o.append(f'<path d="M{ax} {cy} h32 m-6 -5 l6 5 -6 5" stroke="#4b6a7a" stroke-width="1.8" fill="none"/>')
    o.append(T(x0, 998, f"{i + 1:02d}", 13, STEP_COL[i], 700))
    tl = textwrap.wrap(title, 15)
    for k, t_ in enumerate(tl):
        o.append(T(x0, 1017 + k * 15, t_, 12, WHITE, 600))
    o.append(TL(x0, 1048, desc, 24, 14, 10.5, MUTED))

# ------------------------------------------------------------------ GitHub stats
o.append('<rect x="730" y="905" width="1" height="160" fill="#12303f"/>')
for i, hgt in enumerate([8, 14, 20]):
    o.append(R(748 + i * 8, 918 - hgt, 5, hgt, 1.5, TEAL))
o.append(T(773, 916, "GitHub Stats", 17, WHITE, 600))
cards = [
    ("Commits (3 months)", st["commits_3mo"], "Last 90 days", WHITE),
    ("Total Issues", st["issues"], "Issues you opened", WHITE),
    ("Contributions (1 yr)", st["contributions_1y"], "Last 12 months", WHITE),
    ("Current Streak", f'{st["current_streak"]} days', f'Longest: {st["longest_streak"]} days', "#fb923c"),
]
for i, (lab, val, sub, vc) in enumerate(cards):
    x = 745 + i * 137.3
    o.append(R(round(x, 1), 930, 128, 78, 8, "#07202f", "#154256", 1.2))
    o.append(R(round(x, 1) + 1, 940, 3, 58, 1.5, TEAL))
    o.append(T(round(x, 1) + 14, 950, lab, 9, TEAL, 600))
    o.append(T(round(x, 1) + 14, 982, val if isinstance(val, str) else fmt(val), 25, vc, 700))
    o.append(T(round(x, 1) + 14, 998, sub, 9.5, MUTED))

# languages panel
o.append(R(745, 1018, 240, 90, 8, "#07202f", "#154256", 1.2))
o.append(T(758, 1034, "Most Used Languages", 11, WHITE, 600))
langs = st["languages"] or [{"name": "No data", "percent": 100, "color": "#334155"}]
dcx, dcy, dr = 792, 1074, 24
circ = 2 * math.pi * dr
off = 0.0
tot = sum(l["percent"] for l in langs) or 1
o.append(f'<g transform="rotate(-90 {dcx} {dcy})">')
for l in langs:
    seg = l["percent"] / tot * circ
    o.append(f'<circle cx="{dcx}" cy="{dcy}" r="{dr}" fill="none" stroke="{l["color"]}" stroke-width="12" '
             f'stroke-dasharray="{seg:.2f} {circ - seg:.2f}" stroke-dashoffset="{-off:.2f}"/>')
    off += seg
o.append('</g>')
for i, l in enumerate(langs[:6]):
    yy = 1048 + i * 10.6
    o.append(f'<circle cx="852" cy="{yy - 3}" r="3" fill="{l["color"]}"/>')
    o.append(T(860, yy, l["name"], 9.5, TXT))
    o.append(T(972, yy, f'{l["percent"]:.1f}%', 9.5, TXT, 400, "end"))

# heatmap panel
o.append(R(997, 1018, 288, 90, 8, "#07202f", "#154256", 1.2))
o.append(T(1010, 1034, "Contribution Activity", 11, WHITE, 600))
o.append(T(1274, 1034, "last 20 weeks", 9, MUTED, 400, "end"))
for r_, lab in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
    o.append(T(1010, 1045 + r_ * 8.6 + 6, lab, 8, MUTED))
for wi, wk in enumerate(st["heatmap"][-20:]):
    for di, lv in enumerate(wk):
        o.append(R(1038 + wi * 11.8, 1042 + di * 8.6, 9, 7, 1.5, HEAT[max(0, min(4, lv))]))

# ------------------------------------------------------------------ Footer
o.append('<rect x="0" y="1125" width="1312" height="75" fill="#04121c"/><rect x="0" y="1124" width="1312" height="1" fill="#12303f"/>')
o.append(f'<path d="M34 1166 L56 1138 L66 1152 L72 1146 L90 1166Z" fill="{TEAL}" opacity="0.85"/>')
o.append(T(96, 1148, "My Journey", 16, WHITE, 600))
o.append(TL(96, 1168, cfg["journey"], 78, 15, 11.5, MUTED))
for i, ln in enumerate(cfg["footer_quote"]):
    o.append(T(560 + i * 12, 1145 + i * 18, ln, 14, TEAL, 400,
               extra=f'font-style="italic" font-family="{SCRIPT}" transform="rotate(-6 560 1145)"'))
o.append(f'<path d="M760 1138 l8 -8 8 8 -8 4Z" fill="{TEAL}"/>')
o.append(T(788, 1146, "Let's Connect", 15, WHITE, 600))
c = cfg["contact"]
items = [("GitHub", c["github"], "#e6edf3"), ("LinkedIn", c["linkedin_text"], "#0a66c2"), ("Email", c["email"], "#38bdf8")]
for i, (lab, sub, ic) in enumerate(items):
    x = 770 + i * 180
    o.append(R(x, 1160, 26, 26, 6 if i else 13, ic))
    glyph = {"GitHub": "", "LinkedIn": "in", "Email": "@"}[lab]
    if glyph:
        o.append(T(x + 13, 1179, glyph, 14, WHITE, 700, "middle"))
    else:
        o.append('<circle cx="%d" cy="1173" r="8" fill="#0d1117"/>' % (x + 13))
    o.append(T(x + 36, 1171, lab, 12, WHITE, 600))
    o.append(T(x + 36, 1185, sub, 11, MUTED))
o.append(T(1284, 1146, f'Auto-updated {st["updated"]}', 9.5, MUTED, 400, "end"))

o.append("</svg>")
out = ROOT / "assets" / "dashboard.svg"
out.write_text("\n".join(o), encoding="utf-8")
print(f"wrote {out} ({out.stat().st_size // 1024} KB)")
