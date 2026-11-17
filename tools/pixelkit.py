"""Shared pixel-art kit for the Qcutedev profile SVGs (make_craft.py: static art, make_stats.py: live stats).

Every texture, sprite and icon is original pixel art drawn here as ASCII grids or seeded noise;
no game textures, logos or fonts are used. Output is deterministic (fixed RNG seeds).
Fonts (SIL OFL 1.1, licenses in ../licenses/) are subset to ASCII, renamed and embedded as WOFF.
They are not stored in this repo; put these files in <fonts-dir>:
  pixel.ttf <- https://raw.githubusercontent.com/google/fonts/main/ofl/pressstart2p/PressStart2P-Regular.ttf
  body.ttf  <- https://raw.githubusercontent.com/google/fonts/main/ofl/pixelifysans/PixelifySans%5Bwght%5D.ttf
Press Start 2P has a Reserved Font Name, so the subsets are renamed (QcPixel, QcBody, QcBodyB).
"""
import base64
import io
import math
import random
import re
import string
from pathlib import Path
from xml.sax.saxutils import escape

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

# ---------------------------------------------------------------- palette
NIGHT, PANEL, PANEL2, SLOTBG = "#0A0E1A", "#0F1524", "#151D30", "#0B1120"
EDGE, EDGE2 = "#26314A", "#3A4A70"
TEXT, SOFT, MUTED, DIM = "#E6EDF7", "#B9C4D6", "#8A96AD", "#56627A"
CYAN, CYAN_L, CYAN_D = "#3EE6EE", "#B8FBFF", "#1B7F8A"
PURPLE, PURPLE_L, PURPLE_D = "#9B6BFF", "#C3A6FF", "#4B2F94"
GREEN = "#7BE35A"

# ore colour triples: highlight, body, shade
DIAMOND = ("#D6FFFC", "#4EE6E0", "#1F9C97")
AMETHYST = ("#EBDDFF", "#A57BFF", "#5B3AA8")
EMERALD = ("#C8FFD9", "#2ED16B", "#137A3A")
LAPIS = ("#B8C8FF", "#4A6FF0", "#1A2F8A")
QUARTZ = ("#FFFFFF", "#D9DEE8", "#8E97AA")
PRISMARINE = ("#C8FFF0", "#3FC9B0", "#1B6E62")


def shade(color: str, k: float) -> str:
    return "#" + "".join(f"{min(255, int(int(color[i:i + 2], 16) * k)):02X}" for i in (1, 3, 5))


# ---------------------------------------------------------------- fonts
FAMILY = {"px": "QcPixel", "tx": "QcBody", "tb": "QcBodyB"}
_SOURCES = {"px": ("pixel.ttf", None), "tx": ("body.ttf", 400), "tb": ("body.ttf", 600)}
_FONTS: dict[str, tuple[str, dict[str, float]]] = {}


def load_fonts(fonts_dir: Path) -> None:
    for key, (src, wght) in _SOURCES.items():
        alias = FAMILY[key]
        font = TTFont(fonts_dir / src)
        if wght is not None and "fvar" in font:
            font = instantiateVariableFont(font, {"wght": wght})
        opts = subset.Options()
        opts.layout_features = ["kern"]
        opts.name_IDs = [0, 13, 14]  # keep copyright + license; family names are replaced below
        sub = subset.Subsetter(opts)
        sub.populate(text=string.printable)
        sub.subset(font)
        name = font["name"]
        for nid, value in ((1, alias), (2, "Regular"), (4, alias), (6, alias), (3, alias)):
            name.setName(value, nid, 3, 1, 0x409)
        upm, cmap, hmtx = font["head"].unitsPerEm, font.getBestCmap(), font["hmtx"]
        widths = {chr(cp): hmtx[g][0] / upm for cp, g in cmap.items()}
        font.flavor = "woff"
        buf = io.BytesIO()
        font.save(buf)
        _FONTS[key] = (base64.b64encode(buf.getvalue()).decode(), widths)


def tw(s: str, size: float, f: str = "tx") -> float:
    """Text advance width in px (kerning ignored)."""
    widths = _FONTS[f][1]
    return sum(widths.get(c, .6) for c in s) * size


BASE_CSS = """.blink { animation: blink 1s steps(1) infinite; }
    @keyframes blink { 50% { opacity: 0; } }
    .fa { animation: fa .4s steps(1) infinite; }
    .fb { animation: fb .4s steps(1) infinite; }
    @keyframes fa { 0% { opacity: 1; } 50% { opacity: 0; } }
    @keyframes fb { 0% { opacity: 0; } 50% { opacity: 1; } }
    @keyframes show { from { opacity: 0; } to { opacity: 1; } }"""
REDUCED = "@media (prefers-reduced-motion: reduce) { * { animation: none !important; } .fb, .moving { display: none; } }"


def svg(w: float, h: float, label: str, body: str, css: str = "") -> str:
    used = [k for k in FAMILY if re.search(rf'class="(?:[^"]* )?{k}(?: [^"]*)?"', body)]
    faces = "\n    ".join(f"@font-face {{ font-family: '{FAMILY[k]}'; src: url(data:font/woff;base64,{_FONTS[k][0]}) format('woff'); }}"
                           for k in used)
    classes = " ".join(f".{k} {{ font-family: '{FAMILY[k]}', 'Courier New', monospace; }}" for k in used)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:g} {h:g}" width="{w:g}" height="{h:g}" role="img" aria-label="{escape(label)}">
  <style>
    {faces}
    {classes}
    {BASE_CSS}
    {css}
    {REDUCED}
  </style>
{body}
</svg>
"""


# ---------------------------------------------------------------- text
Tok = tuple[str, str, str]  # text, colour, font class


def text(x: float, y: float, s: str, size: float, color: str, f: str = "tx", anchor: str = "start",
         attrs: str = "", shadow: str | None = None, off: float | None = None) -> str:
    assert s.isascii(), s  # fonts are ASCII subsets
    a = "" if anchor == "start" else f' text-anchor="{anchor}"'
    t = escape(s)
    out = ""
    if shadow:
        o = off if off is not None else max(1.0, size / 8)
        out += (f'<text x="{x + o:g}" y="{y + o:g}"{a} class="{f}" font-size="{size:g}" fill="{shadow}" '
                f'xml:space="preserve"{attrs}>{t}</text>')
    return out + f'<text x="{x:g}" y="{y:g}"{a} class="{f}" font-size="{size:g}" fill="{color}" xml:space="preserve"{attrs}>{t}</text>'


def rich(x: float, y: float, toks: list[Tok], size: float, anchor: str = "start", attrs: str = "") -> str:
    assert all(s.isascii() for s, _, _ in toks), toks
    a = "" if anchor == "start" else f' text-anchor="{anchor}"'
    spans ="".join(f'<tspan class="{f}" fill="{c}">{escape(s)}</tspan>' for s, c, f in toks)
    return f'<text x="{x:g}" y="{y:g}"{a} font-size="{size:g}" xml:space="preserve"{attrs}>{spans}</text>'


def rich_w(toks: list[Tok], size: float) -> float:
    return sum(tw(s, size, f) for s, _, f in toks)


def wrap(toks: list[Tok], size: float, maxw: float) -> list[list[Tok]]:
    """Greedy word wrap that keeps each word's colour and font."""
    words = [(part, c, f) for s, c, f in toks for part in re.findall(r"\S+\s*|\s+", s)]
    lines: list[list[Tok]] = []
    cur: list[Tok] = []
    curw = 0.0
    for part, c, f in words:
        if cur and curw + tw(part.rstrip(), size, f) > maxw:
            lines.append(cur)
            cur, curw = [], 0.0
            if not part.strip():
                continue
        cur.append((part, c, f))
        curw += tw(part, size, f)
    if cur:
        lines.append(cur)
    out = []
    for ln in lines:
        merged: list[Tok] = []
        for s, c, f in ln:
            if merged and merged[-1][1:] == (c, f):
                merged[-1] = (merged[-1][0] + s, c, f)
            else:
                merged.append((s, c, f))
        s, c, f = merged[-1]
        merged[-1] = (s.rstrip(), c, f)
        out.append(merged)
    return out


# ---------------------------------------------------------------- shapes
def nrect(x: float, y: float, w: float, h: float, n: float) -> str:
    """Path for a rectangle with square (pixel) notched corners."""
    return (f"M{x + n:g} {y:g}H{x + w - n:g}V{y + n:g}H{x + w:g}V{y + h - n:g}H{x + w - n:g}V{y + h:g}"
            f"H{x + n:g}V{y + h - n:g}H{x:g}V{y + n:g}H{x + n:g}Z")


def box(x: float, y: float, w: float, h: float, fill: str, edge: str | None = None, t: float = 2, n: float = 4,
        extra: str = "") -> str:
    out = ""
    if edge:
        out += f'<path d="{nrect(x, y, w, h, n)}" fill="{edge}"/>'
        x, y, w, h = x + t, y + t, w - 2 * t, h - 2 * t
    return out + f'<path d="{nrect(x, y, w, h, n)}" fill="{fill}"{extra}/>'


def brackets(x: float, y: float, w: float, h: float, ln: float, t: float, color: str, op: float = 1) -> str:
    """HUD corner brackets."""
    out = []
    for cx, cy, sx, sy in ((x, y, 1, 1), (x + w, y, -1, 1), (x, y + h, 1, -1), (x + w, y + h, -1, -1)):
        hx = cx if sx > 0 else cx - ln
        vy = cy if sy > 0 else cy - ln
        out.append(f'<rect x="{hx:g}" y="{cy if sy > 0 else cy - t:g}" width="{ln:g}" height="{t:g}"/>'
                   f'<rect x="{cx if sx > 0 else cx - t:g}" y="{vy:g}" width="{t:g}" height="{ln:g}"/>')
    return f'<g fill="{color}" fill-opacity="{op:g}">{"".join(out)}</g>'


def panel(w: float, h: float, title: str, right: str = "", bar: float = 44, tsize: float = 11) -> str:
    """Dark game-console panel: notched border, title bar, cyan/purple accent line."""
    n = 6
    top = (f"M{2 + n} 2H{w - 2 - n}V{2 + n}H{w - 2}V{bar}H2V{2 + n}H{2 + n}Z")
    out = (box(0, 0, w, h, PANEL, EDGE, 2, n)
           + f'<path d="{top}" fill="{PANEL2}"/>'
           + f'<rect x="2" y="{bar}" width="{w - 4:g}" height="2" fill="{EDGE}"/>'
           + f'<rect x="{2 + n}" y="2" width="132" height="2" fill="{CYAN}"/>'
           + f'<rect x="{2 + n + 132}" y="2" width="44" height="2" fill="{PURPLE}"/>'
           + f'<rect x="20" y="{bar / 2 - 4:g}" width="8" height="8" fill="{CYAN}"/>'
           + text(38, bar / 2 + tsize / 2, title, tsize, TEXT, "px"))
    if right:
        out += text(w - 20, bar / 2 + 5, right, 14, MUTED, "tx", "end")
    return out


# ---------------------------------------------------------------- pixel sprites
def sprite(rows: list[str], palette: dict[str, str], px: float, x0: float = 0, y0: float = 0) -> str:
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
            out.append(f'<rect x="{x0 + start * px:g}" y="{y0 + r * px:g}" width="{(c - start) * px:g}" '
                       f'height="{px:g}" fill="{palette[ch]}"/>')
    return "".join(out)


def gem_pal(ore: tuple[str, str, str]) -> dict[str, str]:
    hi, mid, lo = ore
    return {"K": shade(lo, .3), "H": hi, "M": mid, "L": lo, "b": "#7A5A32"}


DEV_PAL = {"H": "#3B2A20", "K": CYAN, "s": "#E0AC7E", "S": "#C68E62", "W": "#FFFFFF", "E": "#2B4BC9",
           "m": "#9C5B45", "P": "#7A3CFF", "D": "#5A2BC0", "w": "#F0F0FF", "C": GREEN,
           "J": "#2E3A8C", "j": "#232C6B", "G": "#4A4A4A", "g": "#363636"}
DEV_HEAD = [
    "....HHHHHHHH....",
    "...KHHHHHHHHK...",
    "...KHsssssHHK...",
    "...KssssssssK...",
    "....sWEssEWs....",
    "....ssssssss....",
    "....sssmmsss....",
    "....ssssssss....",
]
DEV_BODY = [
    "DDDDPPPPPPPP....",
    "DDDDPPwPPwPP....",
    "DDDDPPwPPwPP....",
    "DDDDPPPPPPPP....",
    "DDDDPPPPCCPP....",
    "DDDDPPPPCCPP....",
    "DDDDPPDDDDPP....",
    "DDDDPDDDDDDP....",
    "ssssPPPPPPPP....",
    "ssssPPPPPPPP....",
    "ssssPPPPPPPP....",
    "SSSSPPPPPPPP....",
]
DEV_LEGS = ["....JJJJjjjj...."] * 10 + ["....GGGGgggg...."] * 2
ARM = ["DDDD"] * 8 + ["ssss"] * 3 + ["SSSS"]


def dev(px: float, x0: float, y0: float, right_arm: str = "") -> str:
    """Front-facing dev (16x32 px grid). `right_arm` is drawn in a group pivoting at the right shoulder."""
    body = sprite(DEV_HEAD + DEV_BODY + DEV_LEGS, DEV_PAL, px, x0, y0)
    return f'{body}<g transform="translate({x0 + 14 * px:g} {y0 + 8 * px:g})">{right_arm}</g>'


def arm(px: float, cls: str, tool: str = "") -> str:
    return f'<g class="{cls}">{sprite(ARM, DEV_PAL, px, -2 * px, 0)}{tool}</g>'


def held_pickaxe(px: float) -> str:
    """Pickaxe in arm-local space: handle continues the arm, head across the tip."""
    y0 = 10 * px
    handle = (f'<rect x="{-px:g}" y="{y0:g}" width="{2 * px:g}" height="{9 * px:g}" fill="#5C4126"/>'
              f'<rect x="{-px:g}" y="{y0:g}" width="{px:g}" height="{9 * px:g}" fill="#7A5A32"/>')
    head_rows = ["KK.........KK", "KMK.......KMK", ".KMMMMHMMMMK.", "..KKKKKKKKK.."]
    return handle + sprite(head_rows, gem_pal(DIAMOND), px, -6.5 * px, y0 + 7 * px)


BUG_TOP = [".......g.g", "..gggg..g.", ".gGgGgggg.", "gGgGgggggk", ".gggggggg."]
BUG_LEGS_A = [".g..g..g..", "g..g..g..."]
BUG_LEGS_B = ["..g..g..g.", "...g..g..g"]
BUG_PAL = {"g": GREEN, "G": "#3E8E2A", "k": NIGHT}


def bug(px: float, x0: float, y0: float) -> str:
    ly = y0 + len(BUG_TOP) * px
    return (sprite(BUG_TOP, BUG_PAL, px, x0, y0)
            + f'<g class="fa">{sprite(BUG_LEGS_A, BUG_PAL, px, x0, ly)}</g>'
            + f'<g class="fb">{sprite(BUG_LEGS_B, BUG_PAL, px, x0, ly)}</g>')


def crack_stages(seed: int, n: int = 5) -> list[list[tuple[int, int]]]:
    rng = random.Random(seed)
    paths = []
    for k in range(5):
        ang = k * 2 * math.pi / 5 + rng.uniform(-.4, .4)
        r, c, path = 7.5, 7.5, []
        for _ in range(10):
            ang += rng.uniform(-.6, .6)
            r += math.sin(ang)
            c += math.cos(ang)
            cell = (int(r), int(c))
            if 0 <= cell[0] < 16 and 0 <= cell[1] < 16 and cell not in path:
                path.append(cell)
        paths.append(path)
    stages = []
    for s in range(1, n + 1):
        cells = []
        for p in paths:
            cells += p[:math.ceil(len(p) * s / n)]
        stages.append(sorted(set(cells)))
    return stages


# items
GEM = ["..KKKKKK..", ".KHMMHMMK.", "KHMMMMMMMK", "KLMMMMMMLK", ".KLMMMMLK.", "..KLMMLK..", "...KLLK...", "....KK...."]
PICK = [
    "...KKKKK....",
    "..KHMMMMK...",
    "...KKKKMMK..",
    "......KbMMK.",
    ".....KbK.KMK",
    "....KbK..KMK",
    "...KbK....KK",
    "..KbK.......",
    ".KbK........",
    "KbK.........",
    "KK..........",
]
CUP = ["KKKKKKK..", "KbbbbbKKK", "KWWWWWK.K", "KWWWWWK.K", "KWWWWWKKK", ".KWWWK...", "..KKK...."]
CUP_PAL = {"K": "#2A1608", "b": "#6B3E1E", "W": "#F2F2F2"}
LAPTOP = [
    ".KKKKKKKKKK.",
    ".KSSSSSSSSK.",
    ".KSGGGSSSSK.",
    ".KSSSCCCSSK.",
    ".KSGGSSSSSK.",
    ".KSSSSSSSSK.",
    ".KKKKKKKKKK.",
    "KMMMMMMMMMMK",
    "KKKKKKKKKKKK",
]
LAPTOP_PAL = {"K": "#222222", "S": "#16202E", "G": GREEN, "C": CYAN, "M": "#A0A0A0"}
BOOK = ["KKKKKKKKK.", "KRRRRRRRKW", "KRYYYYYRKW", "KRRRRRRRKW", "KRRYYYRRKW",
        "KRRRRRRRKW", "KRRRRRRRKW", "KKKKKKKKKW", ".WWWWWWWWW"]
BOOK_PAL = {"K": "#1E1440", "R": "#5B3AA8", "Y": CYAN, "W": "#D9DEE8"}
TORCH_A = ["...YY...", "..YOOY..", "..YOOY..", "...HH...", "...HH...", "...HH...", "...HH...", "...HH..."]
TORCH_B = ["..Y.Y...", "..YOOY..", ".YOOOY..", "...HH...", "...HH...", "...HH...", "...HH...", "...HH..."]
TORCH_PAL = {"Y": CYAN_L, "O": CYAN, "H": "#7A5A32"}
CHIP = ["..P.P.P...", ".KKKKKKK..", "PKGGGGGKP.", ".KG.A.GK..", "PKGAAAGKP.",
        ".KG.A.GK..", "PKGGGGGKP.", ".KKKKKKK..", "..P.P.P..."]
CHIP_PAL = {"P": PURPLE_L, "K": "#2A2A3A", "G": "#1F9C97", "A": CYAN}
MAP = [
    "KKKKKKKKKKKKKKKK",
    "KTTTTTTTTTTTTTTK",
    "KTGGTTTTBBBTTTTK",
    "KTGGGTTTBBBBTTTK",
    "KTTGTTRTTBBTTTTK",
    "KTTTTTRTTTTTTGGK",
    "KTTRRRTTTTTTGGGK",
    "KTTRTTTTTTTTTTTK",
    "KTTRTTTGGTTTTTTK",
    "KTTRRRRRRRRTTTTK",
    "KTBBTTTGGTTRTTTK",
    "KTBBBTTTTTTRTTTK",
    "KTTBTTTTTTTRTTTK",
    "KTTTTTTTTTTTTTTK",
    "KKKKKKKKKKKKKKKK",
]
MAP_PAL = {"K": "#4A3A22", "T": "#E8D9A8", "G": "#6DB83A", "B": "#4F8DE8", "R": PURPLE}
PIN = [".KKK.", "KRRRK", "KRWRK", "KRRRK", ".KRK.", "..K.."]
PIN_PAL = {"K": "#08303A", "R": CYAN, "W": "#FFFFFF"}
BED = [
    "PP..............",
    "PPWWWW..........",
    "PPWWWWRRRRRRRRRR",
    "PPWWWWRRRRRRRRRR",
    "PPRRRRRRRRRRRRRR",
    "PPDDDDDDDDDDDDDD",
    "PPPPPPPPPPPPPPPP",
    "PP............PP",
    "PP............PP",
]
BED_PAL = {"P": "#8F6A3A", "W": "#F2F2F2", "R": "#7A4FE0", "D": "#4B2F94"}
POTION = [
    "......KKKK......",
    "......KCCK......",
    "......KCCK......",
    ".......KK.......",
    "......KGGK......",
    "......KGGK......",
    ".....KGGGGK.....",
    "....KGGGGGGK....",
    "...KPPPPPPPPK...",
    "...KPWPPPPPPK...",
    "...KPWPPPPPPK...",
    "...KPPPPPPPPK...",
    "...KPPPPPPPPK...",
    "....KPPPPPPK....",
    ".....KKKKKK.....",
]
POTION_PAL = {"K": "#2A2A3A", "C": "#8F6A3A", "G": "#CFE8FF", "P": CYAN, "W": CYAN_L}
BEACON = [
    "KKKKKKKKKKKKKKKK",
    "KggggggggggggggK",
    "Kg............gK",
    "Kg..cccccccc..gK",
    "Kg.cCCCCCCCCc.gK",
    "Kg.cCWWWWWWCc.gK",
    "Kg.cCWWWWWWCc.gK",
    "Kg.cCWWWWWWCc.gK",
    "Kg.cCWWWWWWCc.gK",
    "Kg.cCCCCCCCCc.gK",
    "Kg..cccccccc..gK",
    "Kg............gK",
    "KOOOOOOOOOOOOOOK",
    "KOoOoOoOoOoOoOoK",
    "KOOOOOOOOOOOOOOK",
    "KKKKKKKKKKKKKKKK",
]
BEACON_PAL = {"K": "#12333A", "g": "#9FEFF2", "c": CYAN_D, "C": CYAN, "W": CYAN_L, "O": "#1C1430", "o": "#3E2D6B"}
EYE = [".gggg.", "gGccGg", "gcKKcg", "gcKKcg", "gGccGg", ".gggg."]
EYE_PAL = {"g": "#1E4B46", "G": "#2E7C6E", "c": CYAN, "K": "#062A2E"}
FLOWER_A = [".P.P.", "PPCPP", ".PPP.", "..G..", ".GG..", "..G.."]
FLOWER_B = ["..C..", ".CWC.", "..C..", "..G..", "..GG.", "..G.."]
TUFT = ["G...G.G", ".G.GG..", "GGG.GGG"]
PLANT_PAL = {"P": PURPLE_L, "C": CYAN, "W": "#FFFFFF", "G": "#3E8E2A"}

# 7x7 category icons for the inventory
CAT_ICONS = {
    "code": [".C...C.", "C.....C", "C.....C", "C.....C", "C.....C", "C.....C", ".C...C."],
    "spark": ["...C...", "...C...", "..CCC..", "CCCCCCC", "..CCC..", "...C...", "...C..."],
    "db": [".CCCCC.", "C.....C", "CCCCCCC", "C.....C", "CCCCCCC", "C.....C", ".CCCCC."],
    "phone": [".CCCCC.", ".C...C.", ".C...C.", ".C...C.", ".CCCCC.", ".CC.CC.", ".CCCCC."],
    "gear": ["..C.C..", ".CCCCC.", "CC...CC", ".C...C.", "CC...CC", ".CCCCC.", "..C.C.."],
    "check": ["......C", ".....CC", "C...CC.", "CC.CC..", ".CCC...", "..C....", "......."],
}


# ---------------------------------------------------------------- block textures (16x16, seeded noise)
Grid = list[list[str | None]]  # None = base colour
STONE_BASE, DIRT_BASE, DEEP_BASE, OBS_BASE = "#7F7F7F", "#866043", "#3A3D45", "#150F26"


def noise(rng: random.Random, picks: list[tuple[str, float]]) -> Grid:
    grid: Grid = []
    for _ in range(16):
        row = []
        for _ in range(16):
            r, acc, val = rng.random(), 0.0, None
            for color, p in picks:
                acc += p
                if r < acc:
                    val = color
                    break
            row.append(val)
        grid.append(row)
    return grid


def tex_stone(seed: int) -> Grid:
    return noise(random.Random(seed), [("#6E6E6E", .2), ("#8F8F8F", .14), ("#747474", .08), ("#999999", .03)])


def tex_dirt(seed: int) -> Grid:
    return noise(random.Random(seed), [("#6F4E36", .2), ("#976C4A", .14), ("#5E4230", .05), ("#B48660", .03)])


def tex_deepslate(seed: int) -> Grid:
    return noise(random.Random(seed), [("#2E3138", .24), ("#474B55", .14), ("#25272D", .06), ("#545966", .03)])


def tex_obsidian(seed: int) -> Grid:
    return noise(random.Random(seed), [("#0C0818", .24), ("#24193F", .14), ("#36265F", .05), ("#4B3585", .015)])


def tex_grass_side(seed: int) -> Grid:
    rng = random.Random(seed)
    grid = tex_dirt(seed + 1)
    greens = ["#5DA130", "#6DB83A", "#4E8C28", "#7CC546"]
    depth = [rng.choice([3, 3, 4, 4, 5, 2]) for _ in range(16)]
    for c in range(16):
        for r in range(depth[c]):
            grid[r][c] = rng.choice(greens)
    return grid


def tex_ore(seed: int, ore: tuple[str, str, str], base_fn=tex_stone) -> Grid:
    rng = random.Random(seed)
    grid = base_fn(seed + 7)
    hi, mid, lo = ore
    spots = [(2, 2), (9, 1), (5, 8), (11, 9), (2, 12), (8, 13)]
    for (r0, c0) in rng.sample(spots, 4):
        shape = rng.choice([[(0, 0), (0, 1), (1, 0), (1, 1), (1, 2)],
                            [(0, 1), (1, 0), (1, 1), (1, 2), (2, 1)],
                            [(0, 0), (0, 1), (1, 1), (1, 2), (2, 2)]])
        for i, (dr, dc) in enumerate(shape):
            grid[r0 + dr][c0 + dc] = hi if i == 0 else (lo if i == len(shape) - 1 else mid)
    return grid


# ---------------------------------------------------------------- fan-art mob: a walking creeper (front view, 8x26)
CREEPER_PAL = {"a": "#5DBB46", "b": "#4CA53A", "c": "#3E8E2A", "d": "#7ED957", "e": "#2A5E1C", "K": "#0B0B0B"}
_FACE = ["........", "........", ".KK..KK.", ".KK..KK.", "...KK...", "..KKKK..", "..KKKK..", "..K..K.."]


def _creeper() -> tuple[list[str], dict[str, list[str]]]:
    rng = random.Random(404)
    top = []
    for r in range(20):  # head 0-7, body 8-19
        row = [rng.choice("aabbbcd") for _ in range(8)]
        if r < 8:
            row = [("K" if _FACE[r][c] == "K" else ch) for c, ch in enumerate(row)]
        if r >= 8:
            row[7] = "e" if rng.random() < .6 else "c"
        top.append("".join(row))

    def leg() -> list[str]:
        return ["".join(rng.choice("bcc") for _ in range(4)) for _ in range(5)] + ["eeee"]

    left, right = leg(), leg()
    # a lifted leg: one row shorter, foot raised by 1 px
    left_s, right_s = ["...."] + left[:4] + ["eeee"], ["...."] + right[:4] + ["eeee"]
    legs = {"S": [a + b for a, b in zip(left, right)],
            "A": [a + b for a, b in zip(left_s, right)],
            "B": [a + b for a, b in zip(left, right_s)]}
    return top, legs


CREEPER_TOP, CREEPER_LEGS = _creeper()


# ---------------------------------------------------------------- tech icons: 12x12 pixel renditions
# (logos and names are trademarks of their owners; drawn here only to label the skills)
MINI = {
    "T": ["###", ".#.", ".#.", ".#.", ".#."], "S": ["###", "#..", "###", "..#", "###"],
    "J": ["..#", "..#", "..#", "#.#", "###"], "C": ["####", "#...", "#...", "#...", "####"],
    "X": ["#.#", "#.#", ".#.", "#.#", "#.#"], "G": ["###", "#..", "#.#", "#.#", "###"],
    "N": ["#..#", "##.#", "#.##", "#..#", "#..#"], "R": ["###.", "#..#", "###.", "#.#.", "#..#"],
    "u": ["...", "#.#", "#.#", "#.#", "###"], "v": ["...", "#.#", "#.#", "#.#", ".#."],
}
SHAPES = {
    "square": [".##########."] + ["############"] * 10 + [".##########."],
    "circle": ["...######...", "..########..", ".##########."] + ["############"] * 6
              + [".##########.", "..########..", "...######..."],
    "hex": ["....####....", "..########.."] + ["############"] * 8 + ["..########..", "....####...."],
}


def letter_icon(shape: str, bg: str, fg: str, glyphs: str, col0: int, row0: int) -> tuple[list[str], dict[str, str]]:
    grid = [list(r.replace("#", "b")) for r in SHAPES[shape]]
    col = col0
    for g in glyphs:
        for r, line in enumerate(MINI[g]):
            for c, ch in enumerate(line):
                if ch == "#":
                    grid[row0 + r][col + c] = "f"
        col += len(MINI[g][0]) + 1
    return ["".join(r) for r in grid], {"b": bg, "f": fg}


TECH: dict[str, tuple[list[str], dict[str, str]]] = {
    "python": (["...BBBBBB...", "..BwBBBBBB..", "..BBBBBBBB..", "........BB..", ".BBBBBBBBB.Y", "BBBBBBBBB.YY",
                "BB.YYYYYYYYY", "B.YYYYYYYYY.", "..YY........", "..YYYYYYYY..", "..YYYYYYwY..", "...YYYYYY..."],
               {"B": "#4B8BD4", "Y": "#FFD43B", "w": "#FFFFFF"}),
    "dart": (["....LLLL....", "...LLLLLL...", "..LLLLLLLL..", ".LLLLLLLLLD.", "LLLLLLLLLDDD", ".LLLLLLLDDDD",
              "..LLLLLDDDDD", "...LLLDDDDDD", "....LDDDDDD.", ".....DDDDD..", "......DDD...", ".......D...."],
             {"L": "#40C4FF", "D": "#0175C2"}),
    "typescript": letter_icon("square", "#3178C6", "#FFFFFF", "TS", 4, 6),
    "javascript": letter_icon("square", "#F7DF1E", "#111111", "JS", 4, 6),
    "java": (["....R..R....", "...R..R.....", "....R..R....", "...R..R.....", "............", ".BBBBBBBB...",
              ".BWWWWWWBBB.", ".BWWWWWWB.B.", ".BWWWWWWB.B.", "..BWWWWBBB..", "...BBBBB....", "BBBBBBBBBBB."],
             {"R": "#F0812D", "B": "#5382A1", "W": "#E8EEF5"}),
    "c": letter_icon("hex", "#5C6BC0", "#FFFFFF", "C", 4, 4),
    "scikit-learn": (["...OOOO.....", "..OOOOOO....", ".OOOOOOOO...", ".OOOOOOOO...", ".OOOOOOBBB..",
                      "..OOOOBBBBB.", "...OOBBBBBBB", "....BBBBBBBB", ".....BBBBBB.", "......BBBB.."],
                     {"O": "#F7931E", "B": "#29ABE2"}),
    "pytorch": (["......OO....", ".....OO.....", "....OO...O..", "...OO.......", "..OO......O.", ".OO........O",
                 ".O.........O", ".O.........O", ".OO.......OO", "..OO.....OO.", "...OOOOOOO..", "....OOOOO..."],
                {"O": "#EE4C2C"}),
    "xgboost": letter_icon("square", "#155E6B", CYAN, "XG", 3, 4),
    "pandas": ([".KK......KK.", ".KK..YY..KK.", ".KK..YY..KK.", ".KK......KK.", ".KK..KK..KK.", ".KK..KK..KK.",
                ".KK..KK..KK.", ".KK..KK..KK.", ".KK......KK.", ".KK..PP..KK.", ".KK..PP..KK."],
               {"K": "#9C8CF0", "Y": "#FFCA00", "P": "#E70488"}),
    "numpy": ([".....LL.....", "...LLLLLL...", ".LLLLLLLLLL.", ".DLLLLLLLLM.", ".DDDLLLLMMM.", ".DDDDDMMMMM.",
               ".DDDDDMMMMM.", ".DDDDDMMMMM.", ".DDDDDMMMMM.", "..DDDDMMMM..", "....DDMM...."],
              {"L": "#9FD3F0", "D": "#4D77CF", "M": "#4DABCF"}),
    "fastapi": (["...TTTTTT...", "..TTTTTTTT..", ".TTTTTTWWTT.", ".TTTTTWWTTT.", "TTTTTWWTTTTT", "TTTTWWWWWTTT",
                 "TTTTTTTWWTTT", "TTTTTTWWTTTT", ".TTTTWWTTTT.", ".TTTWTTTTTT.", "..TTTTTTTT..", "...TTTTTT..."],
                {"T": "#05A898", "W": "#FFFFFF"}),
    "flask": (["....KKKK....", ".....WW.....", ".....WW.....", ".....WW.....", "....W..W....", "...W....W...",
               "..WLLLLLLW..", ".WLLLLLLLLW.", "WLLLLLLLLLLW", "WWWWWWWWWWWW"],
              {"K": "#8F6A3A", "W": "#E6EDF7", "L": "#8FA6C0"}),
    "sqlalchemy": (["..RRRRRRRR..", ".RRRRRRRRRR.", ".rRRRRRRRRr.", ".rrrrrrrrrr.", ".RRRRRRRRRR.", ".rRRRRRRRRr.",
                    ".rrrrrrrrrr.", ".RRRRRRRRRR.", ".rRRRRRRRRr.", ".rrrrrrrrrr.", "..rrrrrrrr.."],
                   {"R": "#E0482B", "r": "#9A2414"}),
    "postgresql": (["..BBB..BBB..", ".BBBBBBBBBB.", "BBBBBBBBBBBB", "BBBwBBBBwBBB", "BBBBBBBBBBBB", ".BBBBBBBBBB.",
                    "..BBBBBBBB..", "....BBBB....", "....BBBB....", "....BB.BB...", "...BB...B..."],
                   {"B": "#5B8FC8", "w": "#FFFFFF"}),
    "postgis": (["...BBBBBB...", ".BBGGBBBBBB.", ".BGGGGBBGGB.", "BGGGGBBBGGGB", "BBGGBBBBBGGB", "BBBGBBBBBBBB",
                 "BBBBBBGGBBBB", "BBBBBGGGGBBB", ".BBBBBGGBBB.", ".BBBBBBBBBB.", "...BBBBBB..."],
                {"B": "#2F6FB0", "G": "#3FA34D"}),
    "prisma": ([".....W......", ".....WW.....", "....WKW.....", "....WKKW....", "...WKKKW....", "...WKKKKW...",
                "..WKKKKKW...", "..WKKKKKKW..", ".WKKKKKKKW..", ".WKKKKKKKKW.", "WWWWWWWWWWWW"],
               {"W": "#CBD5E0", "K": "#4A5568"}),
    "flutter": (["........LL..", ".......LLL..", "......LLL...", ".....LLL....", "....LLL.....", "...LLL..LL..",
                 "..LLL..LLL..", "...L..LLL...", ".....DDD....", "......DDD...", ".......DD..."],
                {"L": "#54C5F8", "D": "#1E73C8"}),
    "next.js": letter_icon("circle", "#E6EDF7", "#000000", "N", 4, 4),
    "react": (["....C..C....", "...C.CC.C...", "CCCCC..CCCCC", "C..C....C..C", "C.C..CC..C.C", ".C..CCCC..C.",
               ".C..CCCC..C.", "C.C..CC..C.C", "C..C....C..C", "CCCCC..CCCCC", "...C.CC.C...", "....C..C...."],
              {"C": "#61DAFB"}),
    "tailwindcss": (["....CCC.....", "..CCCCCCC..C", ".CC....CCCCC", "CC......CCC.", "............",
                     "....CCC.....", "..CCCCCCC..C", ".CC....CCCCC", "CC......CCC."], {"C": "#38BDF8"}),
    "docker": (["......CC....", "...CC.CC....", ".CC.CC.CC...", "BBBBBBBBBB.B", "BBBBBBBBBBBB", "BwBBBBBBBBB.",
                "BBBBBBBBBB..", ".BBBBBBBB...", "...BBBB....."], {"B": "#2496ED", "C": "#9BD3FF", "w": "#FFFFFF"}),
    "github-actions": (["...BBBBBB...", "..BBBBBBBB..", ".BBBWBBBBBB.", "BBBBWWBBBBBB", "BBBBWWWBBBBB", "BBBBWWWWBBBB",
                        "BBBBWWWWBBBB", "BBBBWWWBBBBB", "BBBBWWBBBBBB", ".BBBWBBBBBB.", "..BBBBBBBB..", "...BBBBBB..."],
                       {"B": "#2088FF", "W": "#FFFFFF"}),
    "git": ([".....OO.....", "....OOOO....", "...OWOOOO...", "..OOOWOOOO..", ".OOOOOWOOOO.", "OOOOOOWWWWOO",
             "OOOOOOWOOWOO", ".OOOOOWOOOO.", "..OOOWWWOO..", "...OOWWWO...", "....OOOO....", ".....OO....."],
            {"O": "#F05032", "W": "#FFFFFF"}),
    "uv": letter_icon("square", "#8F5BFF", "#FFFFFF", "uv", 3, 4),
    "render": letter_icon("square", "#E6EDF7", "#111111", "R", 4, 4),
    "pytest": (["BBBBBBBBBBBB", "BBBBBBBBBBBB", "............", "GG.YY.OO.RR.", "GG.YY.OO.RR.", "GG.YY.OO.RR.",
                "GG.YY.OO....", "GG.YY.......", "GG.........."],
               {"B": "#0A9EDC", "G": "#3FA34D", "Y": "#F9C33C", "O": "#F07E2C", "R": "#D84C3A"}),
    "vitest": (["G..........G", "GG........GG", ".GG..YY..GG.", ".GG.YY...GG.", "..GGYYYYGG..", "..GG..YYGG..",
                "...GG.YGG...", "...GGYGG....", "....GGGG....", ".....GG....."], {"G": "#8BC34A", "Y": "#FCC72B"}),
    "playwright": (["RRRRR.......", "RwRwR.......", "RRRRRGGGGG..", "RRwwRGwGwG..", ".RRRGGGGGG..", "..R.GGwwGG..",
                    "....GGGGGG..", ".....GGGG..."], {"R": "#D65348", "G": "#2EAD33", "w": "#FFFFFF"}),
}
for _name, (_rows, _pal) in TECH.items():
    assert all(len(r) == 12 for r in _rows) and len(_rows) <= 12, _name
    assert set("".join(_rows)) <= set(_pal) | {"."}, _name


def tech_icon(name: str, px: float, x: float, y: float, h: float | None = None) -> str:
    """Draw a tech icon at (x, y); with `h`, centre it vertically inside a box of that height."""
    rows, pal = TECH[name]
    if h is not None:
        y += (h - len(rows) * px) / 2
    return sprite(rows, pal, px, x, y)


def tex_pattern(pid: str, grid: Grid, base: str, px: float, origin: tuple[float, float] = (0, 0)) -> str:
    size = 16 * px
    move = f' patternTransform="translate({origin[0]:g} {origin[1]:g})"' if origin != (0, 0) else ""
    out = [f'<pattern id="{pid}" width="{size:g}" height="{size:g}" patternUnits="userSpaceOnUse"{move}>'
           f'<rect width="{size:g}" height="{size:g}" fill="{base}"/>']
    for r, row in enumerate(grid):
        c = 0
        while c < 16:
            col = row[c]
            if col is None:
                c += 1
                continue
            s = c
            while c < 16 and row[c] == col:
                c += 1
            out.append(f'<rect x="{s * px:g}" y="{r * px:g}" width="{(c - s) * px:g}" height="{px:g}" fill="{col}"/>')
    out.append("</pattern>")
    return "".join(out)
