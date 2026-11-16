"""Generate the 'Cyberpunk Terminal' SVG assets for the GitHub profile README.

usage: python make_punk.py <fonts-dir> <out-assets-dir>
Embeds ASCII subsets of Press Start 2P and JetBrains Mono (SIL OFL 1.1) as WOFF data URIs.
Subsets are renamed (QcPixel / QcMono) because Press Start 2P has a Reserved Font Name.
"""
import base64
import io
import string
import sys
from pathlib import Path
from xml.sax.saxutils import escape

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

FONTS, OUT = Path(sys.argv[1]), Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- palette
BG, PANEL, BAR, LINE = "#0B0A12", "#110F1C", "#1A1730", "#2A2645"
TEXT, DIM = "#E8E6F5", "#7C7899"
PINK, CYAN, YELLOW, PURPLE, GREEN = "#FF2E88", "#00F0FF", "#F9F002", "#A970FF", "#39FF14"
SKIN, HOODIE, ARM, PANTS, WHITE = "#F1C27D", "#7A3CFF", "#5A2BC0", "#2E3A8C", "#F5F5FF"


# ---------------------------------------------------------------- fonts
def build_font(src: str, alias: str, wght: int | None = None) -> str:
    font = TTFont(FONTS / src)
    if wght is not None and "fvar" in font:
        font = instantiateVariableFont(font, {"wght": wght})
    opts = subset.Options()
    opts.layout_features = ["kern"]
    opts.name_IDs = [0, 13, 14]  # keep copyright + license; family names are replaced below
    sub = subset.Subsetter(opts)
    sub.populate(text=string.printable)
    sub.subset(font)
    name = font["name"]
    for nid, value in ((1, alias), (2, "Regular"), (4, alias), (6, alias.replace(" ", "")), (3, alias)):
        name.setName(value, nid, 3, 1, 0x409)
    font.flavor = "woff"
    buf = io.BytesIO()
    font.save(buf)
    return base64.b64encode(buf.getvalue()).decode()


PX_B64 = build_font("pixel.ttf", "QcPixel")
MONO_B64 = build_font("mono.ttf", "QcMono", 400)
MONOB_B64 = build_font("mono.ttf", "QcMonoBold", 700)

FONT_CSS = {
    "px": f"@font-face {{ font-family: 'QcPixel'; src: url(data:font/woff;base64,{PX_B64}) format('woff'); }}",
    "mono": f"@font-face {{ font-family: 'QcMono'; src: url(data:font/woff;base64,{MONO_B64}) format('woff'); }}",
    "monob": f"@font-face {{ font-family: 'QcMonoB'; src: url(data:font/woff;base64,{MONOB_B64}) format('woff'); }}",
}
BASE_CSS = """.px { font-family: 'QcPixel', 'Courier New', monospace; }
    .mono { font-family: 'QcMono', Consolas, 'DejaVu Sans Mono', monospace; }
    .monob { font-family: 'QcMonoB', Consolas, 'DejaVu Sans Mono', monospace; font-weight: 700; }
    .blink { animation: blink 1s steps(1) infinite; }
    @keyframes blink { 50% { opacity: 0; } }"""
REDUCED = ("@media (prefers-reduced-motion: reduce) { * { animation: none !important; } "
           ".typecover, .typecursor, .fb { display: none; } }")


def svg(w: int, h: int, label: str, body: str, fonts: list[str], css: str = "") -> str:
    font_css = "\n    ".join(FONT_CSS[f] for f in fonts)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{escape(label)}">
  <style>
    {font_css}
    {BASE_CSS}
    {css}
    {REDUCED}
  </style>
{body}
</svg>
"""


# ---------------------------------------------------------------- pixel sprites
def sprite(rows: list[str], palette: dict[str, str], px: int, x0: float = 0, y0: float = 0) -> str:
    """Render ASCII pixel art as rects, merging horizontal runs of the same colour."""
    out = []
    for r, row in enumerate(rows):
        c = 0
        while c < len(row):
            ch = row[c]
            if ch == ".":
                c += 1
                continue
            start = c
            while c < len(row) and row[c] == ch:
                c += 1
            out.append(f'<rect x="{x0 + start * px}" y="{y0 + r * px}" width="{(c - start) * px}" height="{px}" fill="{palette[ch]}"/>')
    return "".join(out)


DEV_TOP = [
    "......mm......",
    ".....mmmm.....",
    ".....mmmm.....",
    "....ssssss....",
    "....ssssss....",
    "....sscccc....",
    "....ssssss....",
    ".....ssss.....",
    "....hhhhhh..c.",
    "...hhhhhhhh.c.",
    "...hhhhhdddsc.",
    "...hhhhhh.llll",
    "...hhhhhh.....",
    "....pppppp....",
]
DEV_LEGS_A = ["....pp..pp....", "...pp....pp...", "..www....www.."]
DEV_LEGS_B = [".....pppp.....", ".....pppp.....", ".....wwww....."]
DEV_PAL = {"m": PINK, "s": SKIN, "c": CYAN, "h": HOODIE, "d": ARM, "l": "#C9C9D9", "p": PANTS, "w": WHITE}

BUG_TOP = [".......g.g", "..gggg..g.", ".gGgGgggg.", "gGgGgggggk", ".gggggggg."]
BUG_LEGS_A = [".g..g..g..", "g..g..g..."]
BUG_LEGS_B = ["..g..g..g.", "...g..g..g"]
BUG_PAL = {"g": GREEN, "G": "#1FA80A", "k": BG}

HEART = [".pp.pp.", "ppppppp", "ppppppp", ".ppppp.", "..ppp..", "...p..."]

MUG = [
    ".wwwwwwww...",
    ".wwwwwwwwww.",
    ".wppppppw.w.",
    ".wppppppw.w.",
    ".wwwwwwwwww.",
    ".wwwwwwww...",
    "..wwwwww....",
]
STEAM_A = ["...v..v.....", "..v..v......", "...v..v....."]
STEAM_B = ["..v..v......", "...v..v.....", "..v..v......"]


def dev_frames(px: int, x0: float, y0: float) -> str:
    top = sprite(DEV_TOP, DEV_PAL, px, x0, y0)
    legs_y = y0 + len(DEV_TOP) * px
    a = sprite(DEV_LEGS_A, DEV_PAL, px, x0, legs_y)
    b = sprite(DEV_LEGS_B, DEV_PAL, px, x0, legs_y)
    return f'{top}<g class="fa">{a}</g><g class="fb">{b}</g>'


def bug_frames(px: int, x0: float, y0: float) -> str:
    top = sprite(BUG_TOP, BUG_PAL, px, x0, y0)
    legs_y = y0 + len(BUG_TOP) * px
    a = sprite(BUG_LEGS_A, BUG_PAL, px, x0, legs_y)
    b = sprite(BUG_LEGS_B, BUG_PAL, px, x0, legs_y)
    return f'{top}<g class="fa">{a}</g><g class="fb">{b}</g>'


FRAME_CSS = """.fa { animation: fa .36s steps(1) infinite; }
    .fb { animation: fb .36s steps(1) infinite; }
    @keyframes fa { 0% { opacity: 1; } 50% { opacity: 0; } }
    @keyframes fb { 0% { opacity: 0; } 50% { opacity: 1; } }"""


def window(w: int, h: int, title: str, accent: str = LINE) -> str:
    """Terminal window chrome: panel, title bar, three dots, centred title."""
    return f"""  <clipPath id="win"><rect width="{w}" height="{h}" rx="12"/></clipPath>
  <g clip-path="url(#win)">
    <rect width="{w}" height="{h}" fill="{PANEL}"/>
    <rect width="{w}" height="34" fill="{BAR}"/>
  </g>
  <rect x=".75" y=".75" width="{w - 1.5}" height="{h - 1.5}" rx="11.5" fill="none" stroke="{accent}" stroke-width="1.5"/>
  <circle cx="22" cy="17" r="5.5" fill="{PINK}"/><circle cx="40" cy="17" r="5.5" fill="{YELLOW}"/><circle cx="58" cy="17" r="5.5" fill="{CYAN}"/>
  <text x="{w / 2}" y="22" text-anchor="middle" class="mono" font-size="13" fill="{DIM}">{escape(title)}</text>"""


# ---------------------------------------------------------------- banner
def banner() -> str:
    w, h = 1000, 340
    cw = 12  # JetBrains Mono advance at 20px
    horizon = 244
    # synthwave floor
    floor = []
    for xb in range(-1500, 2501, 125):
        floor.append(f'<line x1="500" y1="{horizon}" x2="{xb}" y2="{h}"/>')
    for k in range(1, 8):
        y = horizon + (h - horizon) * (k / 7) ** 2
        floor.append(f'<line x1="0" y1="{y:.1f}" x2="{w}" y2="{y:.1f}"/>')
    # player panel bars
    bars, bx, seg = [], 772, 17
    for row, (label, color, fill, y) in enumerate(
            [("HP", PINK, 10, 140), ("MP", CYAN, 7, 166), ("COFFEE", YELLOW, 10, 192)]):
        bars.append(f'<text x="680" y="{y + 9}" class="px" font-size="9" fill="{color}">{label}</text>')
        for i in range(10):
            on = i < fill
            delay = 2.4 + row * .25 + i * .06
            cls = ' class="seg"' if on else ""
            style = f' style="animation-delay:{delay:.2f}s"' if on else ""
            bars.append(f'<rect{cls}{style} x="{bx + i * seg}" y="{y}" width="14" height="11" '
                        f'fill="{color if on else LINE}"/>')
    dev_px, bug_px = 4, 4
    dev_h = (len(DEV_TOP) + len(DEV_LEGS_A)) * dev_px
    feet = 330
    body = f"""  <defs>
    <pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000" fill-opacity=".28"/></pattern>
    <linearGradient id="fade" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="{BG}" stop-opacity="1"/><stop offset=".55" stop-color="{BG}" stop-opacity="0"/>
    </linearGradient>
    <clipPath id="floorclip"><rect x="0" y="{horizon}" width="{w}" height="{h - horizon}"/></clipPath>
  </defs>
{window(w, h, "qcutedev@github: ~", PURPLE)}
  <g clip-path="url(#floorclip)" stroke="{PURPLE}" stroke-opacity=".55" stroke-width="1.2">{''.join(floor)}</g>
  <rect x="0" y="{horizon}" width="{w}" height="{h - horizon}" fill="url(#fade)"/>
  <line x1="0" y1="{horizon}" x2="{w}" y2="{horizon}" stroke="{PINK}" stroke-width="2"/>

  <!-- terminal: whoami -->
  <text x="40" y="78" class="mono" font-size="20" fill="{TEXT}"><tspan fill="{PINK}">$</tspan> whoami</text>
  <rect class="typecover" x="{40 + 2 * cw}" y="58" width="{7 * cw}" height="28" fill="{PANEL}"/>
  <rect class="typecursor" x="{40 + 2 * cw}" y="61" width="{cw - 1}" height="22" fill="{CYAN}"/>

  <g class="out1">
    <text x="44" y="146" class="px glitch g1" font-size="48" fill="{CYAN}" fill-opacity=".85">QCUTEDEV</text>
    <text x="36" y="146" class="px glitch g2" font-size="48" fill="{PINK}" fill-opacity=".85">QCUTEDEV</text>
    <text x="40" y="146" class="px glitch gm" font-size="48" fill="{WHITE}">QCUTEDEV</text>
  </g>
  <text class="out2 mono" x="40" y="184" font-size="17" fill="{CYAN}">&gt; student dev // AI enjoyer // future full-time dev</text>
  <text class="out3 mono" x="40" y="212" font-size="17" fill="{DIM}">&gt; status: <tspan fill="{GREEN}">shipping ML into real apps</tspan><tspan class="blink" fill="{GREEN}"> _</tspan></text>

  <!-- player card -->
  <g class="out2">
    <rect x="664" y="56" width="296" height="164" rx="6" fill="{BG}" stroke="{PURPLE}" stroke-width="1.5"/>
    <text x="680" y="84" class="px" font-size="11" fill="{YELLOW}"><tspan class="blink">&gt;</tspan> PLAYER 1</text>
    <text x="680" y="112" class="mono" font-size="14" fill="{TEXT}">class: <tspan fill="{PINK}">AI_DEV</tspan>  lvl: <tspan fill="{CYAN}">student</tspan></text>
    {''.join(bars)}
  </g>

  <!-- walkers: a dev chasing a bug -->
  <g class="walk">
    <g transform="translate(0 {feet - dev_h})">
      <rect x="-14" y="-30" width="96" height="18" rx="3" fill="{BG}" stroke="{CYAN}" stroke-opacity=".7"/>
      <text x="34" y="-17" text-anchor="middle" class="mono" font-size="11" fill="{CYAN}">debugging...</text>
      {dev_frames(dev_px, 0, 0)}
    </g>
    <g class="hop" transform="translate(170 {feet - (len(BUG_TOP) + len(BUG_LEGS_A)) * bug_px})">{bug_frames(bug_px, 0, 0)}</g>
  </g>

  <rect width="{w}" height="{h}" rx="12" fill="url(#scan)" pointer-events="none"/>"""
    css = f"""{FRAME_CSS}
    .typecover {{ animation: type 1s steps(6) .5s both; }}
    .typecursor {{ animation: type 1s steps(6) .5s both, gone .01s 1.7s both; }}
    @keyframes type {{ from {{ transform: translateX(0); }} to {{ transform: translateX({6 * cw}px); }} }}
    @keyframes gone {{ to {{ opacity: 0; }} }}
    .out1 {{ animation: show .01s 1.7s both; }}
    .out2 {{ animation: show .01s 2.0s both; }}
    .out3 {{ animation: show .01s 2.3s both; }}
    @keyframes show {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
    .seg {{ animation: show .01s both; }}
    .glitch {{ transform-box: fill-box; transform-origin: center; }}
    .g1 {{ animation: g1 3.2s steps(1) 2s infinite; }}
    .g2 {{ animation: g2 3.2s steps(1) 2s infinite; }}
    .gm {{ animation: gm 3.2s steps(1) 2s infinite; }}
    @keyframes g1 {{ 0%, 86%, 100% {{ transform: translate(0, 0); }} 88% {{ transform: translate(-7px, 2px); }} 91% {{ transform: translate(5px, -2px); }} 94% {{ transform: translate(-3px, 0); }} }}
    @keyframes g2 {{ 0%, 86%, 100% {{ transform: translate(0, 0); }} 88% {{ transform: translate(7px, -2px); }} 91% {{ transform: translate(-6px, 1px); }} 94% {{ transform: translate(3px, 0); }} }}
    @keyframes gm {{ 0%, 87%, 100% {{ transform: none; opacity: 1; }} 89% {{ transform: skewX(-12deg); }} 92% {{ transform: translateX(3px); opacity: .7; }} }}
    .walk {{ animation: walk 14s linear infinite; }}
    @keyframes walk {{ from {{ transform: translateX(-300px); }} to {{ transform: translateX(1060px); }} }}
    .hop {{ animation: hop .36s steps(1) infinite; }}
    @keyframes hop {{ 50% {{ translate: 0 -3px; }} }}"""
    label = ("Terminal: whoami. QCUTEDEV. Student dev, AI enjoyer, future full-time dev. "
             "Status: shipping ML into real apps. A pixel-art developer chases a bug across a neon grid.")
    return svg(w, h, label, body, ["px", "mono"], css)


# ---------------------------------------------------------------- about.ts
def about() -> str:
    w, cw, lh, top = 1000, 11.4, 31, 76
    T, K, N, P, S, C = TEXT, PINK, CYAN, PURPLE, YELLOW, DIM

    def arr(*items):
        out = [(": [", T)]
        for i, it in enumerate(items):
            out += [(f'"{it}"', S)] + ([(", ", T)] if i < len(items) - 1 else [])
        return out + [("],", T)]

    lines = [
        (0, [("const ", K), ("qcutedev", N), (" = {", T)]),
        (2, [("role", P), (": ", T), ('"Student Developer"', S), (",", T)]),
        (2, [("loves", P)] + arr("AI", "Machine Learning", "Computer Vision")),
        (2, [("learnedInClass", P)] + arr("Java", "Python", "C")),
        (2, [("buildsWith", P)] + arr("Python", "Dart", "TypeScript")),
        (2, [("currently", P), (": ", T), ('"turning ML models into real apps"', S), (",", T)]),
        (2, [("goal", P), (": ", T), ('"Full-time Software Developer"', S), (", ", T), ("// loading...", C)]),
        (0, [("};", T)]),
    ]
    h = top + lh * (len(lines) - 1) + 34
    rows = []
    for i, (indent, toks) in enumerate(lines):
        y = top + i * lh
        rows.append(f'<text x="40" y="{y}" text-anchor="end" class="mono" font-size="19" fill="{LINE}">{i + 1}</text>')
        spans = "".join(f'<tspan fill="{c}">{escape(t)}</tspan>' for t, c in toks)
        rows.append(f'<text x="{60 + indent * cw}" y="{y}" class="mono" font-size="19" xml:space="preserve">{spans}</text>')
        length = indent + sum(len(t) for t, _ in toks)
        assert 60 + length * cw < 800, (i, 60 + length * cw)
    last = lines[-1]
    cursor_x = 60 + (last[0] + sum(len(t) for t, _ in last[1])) * cw + 6
    # coffee mug with steam, bottom right
    mx, my, mpx = 862, h - 120, 7
    mug = sprite(MUG, {"w": WHITE, "p": PINK}, mpx, mx, my + 3 * mpx)
    steam_a = sprite(STEAM_A, {"v": DIM}, mpx, mx, my - 2 * mpx)
    steam_b = sprite(STEAM_B, {"v": DIM}, mpx, mx, my - 2 * mpx)
    body = f"""{window(w, h, "about.ts", PINK)}
  {''.join(rows)}
  <rect class="blink" x="{cursor_x}" y="{top + (len(lines) - 1) * lh - 18}" width="11" height="22" fill="{CYAN}"/>
  <g class="fa">{steam_a}</g><g class="fb">{steam_b}</g>{mug}"""
    css = FRAME_CSS.replace(".36s", "1.2s")
    label = ("about.ts: role Student Developer; loves AI, Machine Learning, Computer Vision; "
             "learned in class Java, Python, C; builds with Python, Dart, TypeScript; "
             "currently turning ML models into real apps; goal Full-time Software Developer.")
    return svg(w, h, label, body, ["mono"], css)


# ---------------------------------------------------------------- skills (ls)
SKILLS = [
    ("languages/", CYAN, "python  dart  typescript  javascript  java  c"),
    ("ai-ml/", PINK, "scikit-learn  pytorch  xgboost  pandas  numpy"),
    ("backend/", YELLOW, "fastapi  flask  sqlalchemy  postgresql  postgis  prisma"),
    ("mobile-web/", PURPLE, "flutter  next.js  react  tailwindcss"),
    ("tooling/", GREEN, "docker  github-actions  git  uv  render"),
    ("testing/", CYAN, "pytest  vitest  playwright"),
]


def skills() -> str:
    w, cw, lh, top = 1000, 11.4, 38, 118
    h = top + lh * (len(SKILLS) - 1) + 40
    rows = [f'<text x="32" y="74" class="mono" font-size="19" fill="{TEXT}"><tspan fill="{PINK}">$</tspan> ls ~/skills</text>']
    for i, (d, color, items) in enumerate(SKILLS):
        y = top + i * lh
        assert 260 + len(items) * cw < w - 32, d
        rows.append(f'<text x="32" y="{y}" class="monob" font-size="19" fill="{color}">{escape(d)}</text>')
        rows.append(f'<text x="260" y="{y}" class="mono" font-size="19" fill="{TEXT}" xml:space="preserve">{escape(items)}</text>')
    label = "ls ~/skills. " + ". ".join(f"{d.rstrip('/')}: {', '.join(i.split())}" for d, _, i in SKILLS)
    return svg(w, h, label, window(w, h, "zsh: ~/skills", CYAN) + "\n  " + "".join(rows), ["mono", "monob"])


# ---------------------------------------------------------------- prompt strips
def strip(cmd: str, label: str, extra: str = "", w: int = 1000, h: int = 56) -> str:
    body = f"""  <rect x=".75" y=".75" width="{w - 1.5}" height="{h - 1.5}" rx="10" fill="{PANEL}" stroke="{LINE}" stroke-width="1.5"/>
  <text x="28" y="{h / 2 + 7}" class="mono" font-size="19" fill="{TEXT}"><tspan fill="{PINK}">$</tspan> {escape(cmd)}</text>
  <rect class="blink" x="{28 + (len(cmd) + 2) * 11.4 + 4}" y="{h / 2 - 10}" width="11" height="21" fill="{CYAN}"/>
{extra}"""
    return svg(w, h, label, body, ["mono"])


def footer() -> str:
    w, h = 1000, 96
    heart = sprite(HEART, {"p": PINK}, 4, 596, h / 2 - 12)
    dev = dev_frames(3, 926, h - 12 - 17 * 3)
    extra = f"""  <g class="beat">{heart}</g>
  <text x="638" y="{h / 2 + 7}" class="px" font-size="14" fill="{YELLOW}">THANKS 4 VISITING</text>
  <g>{dev}</g>"""
    body_svg = strip("exit 0", "exit 0. Thanks for visiting.", extra, w, h)
    css = FRAME_CSS + """
    .beat { transform-box: fill-box; transform-origin: center; animation: beat 1.2s ease-in-out infinite; }
    @keyframes beat { 0%, 100% { transform: scale(1); } 15% { transform: scale(1.25); } 30% { transform: scale(1); } }"""
    return body_svg.replace(REDUCED, css + "\n    " + REDUCED)


# ---------------------------------------------------------------- project cards
CARDS = [
    ("rideros", "rideros-ai", "RIDEROS AI", "dart", CYAN,
     ["Rider productivity app with 3 custom ML", "models: pickup-time regression, a road-", "photo classifier, K-Means work patterns."],
     "#flutter #fastapi #postgis #pytorch"),
    ("sleepwise", "Project-Sleep", "SLEEPWISE AI", "dart", PURPLE,
     ["Android app that predicts sleep quality", "from a daily check-in, plus a sleep-cycle", "alarm and sleep sounds."],
     "#flutter #fastapi #scikit-learn"),
    ("marketplace", "web-shopping", "THAI MARKETPLACE", "typescript", YELLOW,
     ["Thai multi-vendor marketplace where", "customers, sellers and admins share", "one platform."],
     "#nextjs #typescript #postgresql #prisma"),
    ("mllab", "ml-deployment-lab", "ML DEPLOY LAB", "python", PINK,
     ["Model as a Service: a random-forest", "house-price model served by Flask and", "packaged in Docker."],
     "#flask #docker #scikit-learn"),
]


def card(repo: str, title: str, lang: str, accent: str, lines: list[str], tags: str) -> str:
    w, h, cw = 400, 232, 7.8  # 13px JetBrains Mono advance
    for s in lines + [tags]:
        assert 24 + len(s) * cw < w - 20, s
    assert 24 + len(title) * 15 < w - 24 - (len(lang) + 2) * 7.2 - 8, title
    desc = "".join(f'<text x="24" y="{108 + i * 21}" class="mono" font-size="13" fill="{TEXT}">{escape(s)}</text>'
                   for i, s in enumerate(lines))
    body = f"""{window(w, h, "~/" + repo, accent)}
  <text x="24" y="74" class="px" font-size="15" fill="{accent}">{escape(title)}</text>
  <text x="376" y="73" text-anchor="end" class="mono" font-size="12" fill="{DIM}">[{lang}]</text>
  {desc}
  <line x1="24" y1="186" x2="376" y2="186" stroke="{LINE}" stroke-dasharray="4 4"/>
  <text x="24" y="211" class="mono" font-size="13" fill="{accent}">{escape(tags)}</text>"""
    return svg(w, h, f"{title.title()}: {' '.join(lines)}", body, ["px", "mono"])


files = {
    "banner.svg": banner(),
    "about.svg": about(),
    "skills.svg": skills(),
    "projects.svg": strip("ls ~/projects", "ls ~/projects"),
    "snake-title.svg": strip("./snake --eat ~/contributions", "./snake --eat ~/contributions"),
    "footer.svg": footer(),
}
for slug, repo, title, lang, accent, lines, tags in CARDS:
    files[f"card-{slug}.svg"] = card(repo, title, lang, accent, lines, tags)
for name, content in files.items():
    (OUT / name).write_text(content, encoding="utf-8")
    print(f"{name:24} {len(content.encode()) / 1024:6.1f} KB")
