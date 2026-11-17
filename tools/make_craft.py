"""Generate the static 'Blockcraft' SVGs for the GitHub profile README (Minecraft-style x cyber, pixel art).

usage: python make_craft.py <fonts-dir> <out-assets-dir>      (needs: pip install fonttools)
Every asset has a desktop version (<name>.svg, 1000 px wide) and a mobile version (<name>-m.svg, 480 px wide);
README.md swaps them with <picture><source media="(max-width: 640px)">. Fonts and art notes: see pixelkit.py.
The live stats panel is drawn separately by make_stats.py in the daily workflow.
"""
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pixelkit as pk  # noqa: E402
from pixelkit import (AMETHYST, BEACON, BEACON_PAL, BED, BED_PAL, BOOK, BOOK_PAL, BUG_LEGS_A, BUG_PAL,  # noqa: E402
                      BUG_TOP, CHIP, CHIP_PAL, CUP, CUP_PAL, CYAN, CYAN_D, CYAN_L, DEEP_BASE,
                      DIAMOND, DIM, DIRT_BASE, EDGE, EDGE2, EMERALD, EYE, EYE_PAL, FLOWER_A, FLOWER_B, GEM,
                      GREEN, LAPIS, LAPTOP, LAPTOP_PAL, MAP, MAP_PAL, MUTED, NIGHT, OBS_BASE, PANEL, PANEL2,
                      PICK, PIN, PIN_PAL, PLANT_PAL, POTION, POTION_PAL, PRISMARINE, PURPLE, PURPLE_D,
                      PURPLE_L, QUARTZ, SLOTBG, SOFT, STONE_BASE, TEXT, TORCH_A, TORCH_B, TORCH_PAL, TUFT,
                      arm, box, brackets, crack_stages, dev, gem_pal, held_pickaxe, panel, rich, rich_w,
                      sprite, svg, tex_deepslate, tex_dirt, tex_grass_side, tex_obsidian, tex_ore, tex_pattern,
                      tex_stone, text, tw, wrap)

pk.load_fonts(Path(sys.argv[1]))
OUT = Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)
USER = "Qcutedev"


# ---------------------------------------------------------------- hero: night overworld game cover
def skyline(x0: float, x1: float, base: float, hmin: int, hmax: int, step: int, color: str, rng: random.Random) -> str:
    out, x, hgt = [], x0, rng.randint(hmin, hmax)
    while x < x1:
        wcol = step * rng.randint(1, 3)
        hgt = max(hmin, min(hmax, hgt + rng.choice([-step, 0, step])))
        out.append(f'<rect x="{x:g}" y="{base - hgt:g}" width="{wcol:g}" height="{hgt:g}"/>')
        x += wcol
    return f'<g fill="{color}">{"".join(out)}</g>'


def city(x0: int, x1: int, base: int, hmax: int, rng: random.Random) -> str:
    """Far-off block towers with lit windows: the 'future' half of the world."""
    out, x = [], x0
    while x < x1:
        cw = rng.choice([24, 32, 40, 48])
        ch = rng.randrange(40, hmax, 8)
        top = base - ch
        out.append(f'<rect x="{x}" y="{top}" width="{cw}" height="{ch}" fill="#0E172C"/>'
                   f'<rect x="{x}" y="{top}" width="{cw}" height="4" fill="#1A2746"/>')
        if ch > hmax * .7:
            out.append(f'<rect x="{x + cw // 2 - 1}" y="{top - 14}" width="2" height="14" fill="#1A2746"/>'
                       f'<rect class="tw" style="animation-delay:-{rng.uniform(0, 3):.1f}s" x="{x + cw // 2 - 2}" '
                       f'y="{top - 18}" width="4" height="4" fill="{PURPLE}"/>')
        for wx in range(x + 4, x + cw - 4, 8):
            for wy in range(top + 10, base - 6, 10):
                if rng.random() < .22:
                    col = CYAN if rng.random() < .65 else PURPLE
                    cls = f' class="tw" style="animation-delay:-{rng.uniform(0, 4):.1f}s"' if rng.random() < .12 else ""
                    out.append(f'<rect{cls} x="{wx}" y="{wy}" width="4" height="4" fill="{col}" fill-opacity=".6"/>')
        x += cw + rng.choice([0, 8])
    return "".join(out)


def stars(w: float, ymax: float, n: int, rng: random.Random) -> str:
    out = []
    for i in range(n):
        x, y = rng.randrange(8, int(w) - 8), rng.randrange(8, int(ymax))
        s = rng.choice([2, 2, 2, 3])
        col = rng.choice([TEXT, CYAN_L, PURPLE_L])
        cls = f' class="tw" style="animation-delay:-{rng.uniform(0, 4):.1f}s"' if i % 4 == 0 else ""
        out.append(f'<rect{cls} x="{x}" y="{y}" width="{s}" height="{s}" fill="{col}" fill-opacity="{rng.uniform(.35, .85):.2f}"/>')
    return "".join(out)


def moon(x: float, y: float, s: float) -> str:
    rows = ["..WWWW..", ".WWWWWW.", "WWcWWWWW", "WWWWWcWW", "WWWWWWWW", "WcWWWWWW", ".WWWWcW.", "..WWWW.."]
    return (f'<rect x="{x - s * .5:g}" y="{y - s * .5:g}" width="{s * 2:g}" height="{s * 2:g}" fill="{CYAN}" fill-opacity=".035"/>'
            f'<rect x="{x - s * .25:g}" y="{y - s * .25:g}" width="{s * 1.5:g}" height="{s * 1.5:g}" fill="{CYAN}" fill-opacity=".05"/>'
            + sprite(rows, {"W": "#DCEBFF", "c": "#AFC3E3"}, s / 8, x, y))


def title_text(x: float, y: float, size: float, anchor: str) -> str:
    s, st = "QCUTEDEV", size / 16
    out = "".join(text(x + k * st, y + k * st, s, size, col, "px", anchor)
                  for col, k in (("#120C2A", 4), ("#1E1442", 3), ("#2C1C63", 2), (PURPLE_D, 1)))
    out += text(x, y, s, size, CYAN, "px", anchor, ' filter="url(#glow)" opacity=".4"')
    out += text(x, y, s, size, "url(#tgrad)", "px", anchor,
                f' stroke="{NIGHT}" stroke-width="{size / 32:g}" paint-order="stroke"')
    return out


def hotbar(w: float, h: float, s: float, bottom: float) -> str:
    n = 9
    hx, hy = (w - n * s) / 2, h - s - bottom
    out = [f'<rect x="{hx:g}" y="{hy - 10:g}" width="{n * s:g}" height="6" fill="{NIGHT}"/>',
           f'<rect x="{hx + 1:g}" y="{hy - 9:g}" width="{(n * s - 2) * .72:g}" height="4" fill="{CYAN}"/>',
           "".join(f'<rect x="{hx + i * s:g}" y="{hy - 9:g}" width="1" height="4" fill="{NIGHT}" fill-opacity=".7"/>'
                   for i in range(1, n)),
           f'<rect x="{hx - 2:g}" y="{hy - 2:g}" width="{n * s + 4:g}" height="{s + 4:g}" fill="{NIGHT}" fill-opacity=".8"/>']
    items = [(PICK, gem_pal(DIAMOND), ""), (LAPTOP, LAPTOP_PAL, ""), (CUP, CUP_PAL, "64"), (BOOK, BOOK_PAL, ""),
             (TORCH_A, TORCH_PAL, "torch"), (GEM, gem_pal(DIAMOND), "3"), (GEM, gem_pal(AMETHYST), "12"),
             (CHIP, CHIP_PAL, ""), (BUG_TOP + BUG_LEGS_A, BUG_PAL, "99")]
    for i, (rows, pal, count) in enumerate(items):
        sx = hx + i * s
        out.append(f'<rect x="{sx + 1:g}" y="{hy + 1:g}" width="{s - 2:g}" height="{s - 2:g}" fill="{SLOTBG}" '
                   f'fill-opacity=".6" stroke="{EDGE2}" stroke-width="2"/>')
        ipx = round((s - 14) / max(len(rows[0]), len(rows)) * 4) / 4
        iw, ih = len(rows[0]) * ipx, len(rows) * ipx
        ix, iy = sx + (s - iw) / 2, hy + (s - ih) / 2
        if count == "torch":
            out.append(f'<g class="fa">{sprite(TORCH_A, pal, ipx, ix, iy)}</g><g class="fb">{sprite(TORCH_B, pal, ipx, ix, iy)}</g>')
        else:
            out.append(sprite(rows, pal, ipx, ix, iy))
            if count:
                out.append(text(sx + s - 3, hy + s - 3, count, 8, TEXT, "px", "end", shadow=NIGHT))
    out.append(f'<rect x="{hx - 1:g}" y="{hy - 1:g}" width="{s + 2:g}" height="{s + 2:g}" fill="none" stroke="{CYAN}" stroke-width="3"/>')
    return "".join(out)


def hero(m: bool) -> str:
    w, h = (480, 620) if m else (1000, 460)
    B, tpx = 48, 3
    gy = 480 if m else 336
    ore_x, ore_y = (5 if m else 16) * B, gy - B
    dpx = 4
    dev_x, dev_y = ore_x - 116, gy - 32 * dpx
    beacon_x = (8 if m else 19) * B
    bcx = beacon_x + 24
    rng = random.Random(7)

    defs = "".join([
        tex_pattern("grass", tex_grass_side(3), DIRT_BASE, tpx),
        tex_pattern("dirt", tex_dirt(5), DIRT_BASE, tpx),
        tex_pattern("stone", tex_stone(9), STONE_BASE, tpx),
        tex_pattern("odia", tex_ore(21, DIAMOND), STONE_BASE, tpx),
        tex_pattern("oame", tex_ore(29, AMETHYST), STONE_BASE, tpx),
    ])
    terrain = [f'<rect x="0" y="{gy}" width="{w}" height="{B}" fill="url(#grass)"/>',
               f'<rect x="0" y="{gy + B}" width="{w}" height="{B}" fill="url(#dirt)"/>',
               f'<rect x="0" y="{gy + 2 * B}" width="{w}" height="{h - gy - 2 * B}" fill="url(#stone)"/>']
    for bx, pat in (((0, "odia"), (9, "oame")) if m else ((1, "odia"), (4, "oame"), (15, "oame"), (18, "odia"))):
        terrain.append(f'<rect x="{bx * B}" y="{gy + 2 * B}" width="{B}" height="{h - gy - 2 * B}" fill="url(#{pat})"/>')
    terrain.append("".join(f'<rect x="{x}" y="{gy}" width="1" height="{h - gy}" fill="#000" fill-opacity=".14"/>'
                           for x in range(B, w, B)))
    plant_xs = (30, 300, 440) if m else (66, 180, 262, 420, 560)
    plants = "".join(sprite(spr, PLANT_PAL, 3, x, gy - len(spr) * 3)
                     for x, spr in zip(plant_xs, (FLOWER_A, TUFT, FLOWER_B, TUFT, FLOWER_A)))

    # background: stars, moon, hills, far city
    bg = [stars(w, gy - (160 if m else 150), 40 if m else 70, rng)]
    bg.append(moon(28, 26, 32) if m else moon(800, 52, 40))
    if m:
        bg.append(skyline(0, w, gy, 16, 48, 16, "#0C1326", rng))
        bg.append(city(150, w, gy, 104, rng))
    else:
        bg.append(skyline(0, 620, gy, 16, 64, 16, "#0C1326", rng))
        bg.append(city(600, w, gy, 140, rng))

    beam_top = gy - B
    beam = (f'<g class="beam">'
            f'<rect x="{bcx - 22}" y="0" width="44" height="{beam_top}" fill="url(#beamg)" opacity=".14"/>'
            f'<rect x="{bcx - 10}" y="0" width="20" height="{beam_top}" fill="url(#beamg)" opacity=".32"/>'
            f'<rect x="{bcx - 3}" y="0" width="6" height="{beam_top}" fill="url(#beamc)"/></g>')
    beacon = (f'<rect x="{beacon_x + 3}" y="{gy - B + 3}" width="{B - 6}" height="{B - 6}" fill="{CYAN}" fill-opacity=".2"/>'
              + sprite(BEACON, BEACON_PAL, 3, beacon_x, gy - B))

    # mining: dev swings a pickaxe at a diamond-ore block until it breaks and drops loot
    scene = [dev(dpx, dev_x, dev_y, arm(dpx, "swing", held_pickaxe(dpx)))]
    ore = (f'<g class="ore"><rect x="{ore_x}" y="{ore_y}" width="{B}" height="{B}" fill="url(#odia)"/>'
           f'<rect x="{ore_x}" y="{ore_y}" width="{B}" height="{B}" fill="{NIGHT}" fill-opacity=".28"/>')
    for i, cells in enumerate(crack_stages(41)):
        rects = "".join(f'<rect x="{ore_x + c * tpx:g}" y="{ore_y + r * tpx:g}" width="{tpx}" height="{tpx}"/>' for r, c in cells)
        ore += f'<g class="ck{i + 1}" fill="#05070D" fill-opacity=".75">{rects}</g>'
    scene.append(ore + "</g>")
    part_css = []
    prng = random.Random(5)
    for i in range(8):
        col = prng.choice([DIAMOND[1], DIAMOND[2], "#8F8F8F", "#6E6E6E"])
        dx, dy = prng.uniform(-40, 40), prng.uniform(-36, -10)
        scene.append(f'<rect class="pt{i}" x="{ore_x + 21}" y="{ore_y + 21}" width="6" height="6" fill="{col}"/>')
        part_css.append(f".pt{i} {{ animation: pt{i} 4s linear infinite; opacity: 0; }}"
                        f"@keyframes pt{i} {{ 0%, 54.9% {{ opacity: 0; transform: none; }} 55% {{ opacity: 1; transform: none; }} "
                        f"61% {{ opacity: 1; transform: translate({dx * .7:.0f}px, {dy:.0f}px); }} "
                        f"68%, 100% {{ opacity: 0; transform: translate({dx:.0f}px, {dy + 40:.0f}px); }} }}")
    # loot: every break drops the next inventory item (all skills in turn, one per 4 s loop)
    loot = [it for *_, items in SKILLS for it in items]
    loot_period = 4 * len(loot)
    for i, it in enumerate(loot):
        a, b = 100 * i / len(loot), 100 * (i + 1) / len(loot)
        part_css.append(f".dw{i} {{ animation: dw{i} {loot_period}s steps(1) infinite; opacity: 0; }}"
                        f"@keyframes dw{i} {{ 0% {{ opacity: {1 if i == 0 else 0}; }} "
                        + (f"{a:.4f}% {{ opacity: 1; }} " if i else "") + f"{b:.4f}%, 100% {{ opacity: 0; }} }}")
        scene.append(f'<g class="dw{i}">'
                     f'<g transform="translate({ore_x + 9} {ore_y + 9})"><g class="drop">{pk.tech_icon(it, 2.5, 0, 0, 30)}</g></g>'
                     f'<g class="plus">{text(dev_x + 32, dev_y - 14, "+1 " + it, 9, CYAN, "px", "middle", shadow=NIGHT)}</g></g>')

    # a creeper sneaks up behind the dev, hisses, swells and poofs into smoke (12 s loop)
    cpx = 3.5
    c_h, c_w = 26 * cpx, 8 * cpx
    c_start, c_stop = -40, dev_x - (60 if m else 64)
    white = {k: "#FFFFFF" for k in pk.CREEPER_PAL}
    legs_y = 20 * cpx
    creeper_body = (sprite(pk.CREEPER_TOP, pk.CREEPER_PAL, cpx)
                    + f'<g class="cwalk"><g class="fa">{sprite(pk.CREEPER_LEGS["A"], pk.CREEPER_PAL, cpx, 0, legs_y)}</g>'
                    f'<g class="fb">{sprite(pk.CREEPER_LEGS["B"], pk.CREEPER_PAL, cpx, 0, legs_y)}</g></g>'
                    f'<g class="cstand">{sprite(pk.CREEPER_LEGS["S"], pk.CREEPER_PAL, cpx, 0, legs_y)}</g>'
                    f'<g class="flash">{sprite(pk.CREEPER_TOP + pk.CREEPER_LEGS["S"], white, cpx)}</g>')
    creeper = (f'<g class="creeper moving"><g transform="translate(0 {gy - c_h:g})">'
               f'<rect x="-2" y="{c_h - 3:g}" width="{c_w + 4:g}" height="4" fill="#000" fill-opacity=".35"/>'
               f'<g transform="translate({c_w / 2:g} {c_h:g})"><g class="swell"><g transform="translate({-c_w / 2:g} {-c_h:g})">'
               f'{creeper_body}</g></g></g>'
               f'<g class="hiss">{text(c_w / 2, -10, "sssss...", 8, GREEN, "px", "middle", shadow=NIGHT)}</g></g></g>')
    srng = random.Random(8)
    for i in range(16):
        dx, dy = srng.uniform(-48, 48), srng.uniform(-64, 4)
        sz = srng.choice([8, 10, 12, 14])
        col = srng.choice(["#D9DEE8", "#AAB3C5", "#FFFFFF"])
        ox, oy = srng.uniform(0, c_w), srng.uniform(12, c_h - 8)
        creeper += (f'<rect class="sm{i}" x="{c_stop + ox - sz / 2:.0f}" y="{gy - oy - sz / 2:.0f}" '
                    f'width="{sz}" height="{sz}" fill="{col}"/>')
        part_css.append(f".sm{i} {{ animation: sm{i} 12s linear infinite; opacity: 0; transform-box: fill-box; transform-origin: center; }}"
                        f"@keyframes sm{i} {{ 0%, 79.9% {{ opacity: 0; transform: none; }} 80% {{ opacity: .95; transform: none; }} "
                        f"86% {{ opacity: .85; transform: translate({dx * .7:.0f}px, {dy * .7:.0f}px) scale(1.5); }} "
                        f"94%, 100% {{ opacity: 0; transform: translate({dx:.0f}px, {dy:.0f}px) scale(1.9); }} }}")

    # copy
    tag = [("student dev ", TEXT, "tx"), ("//", PURPLE_L, "tx"), (" AI enjoyer ", TEXT, "tx"), ("//", PURPLE_L, "tx"),
           (" future full-time dev", TEXT, "tx")]
    status = [("status: ", MUTED, "tx"), ("shipping ML into real apps", GREEN, "tb")]
    eyebrow = [(">", CYAN, "px"), (" whoami", MUTED, "px")]
    if m:
        cx = w / 2
        st_w = rich_w(status, 15) + 18
        copy = (rich(cx, 58, eyebrow, 9, "middle")
                + title_text(cx, 124, 44, "middle")
                + rich(cx, 168, tag[:4], 18, "middle")
                + rich(cx, 194, [("future full-time dev", TEXT, "tx")], 18, "middle")
                + f'<rect class="blink" x="{cx - st_w / 2:g}" y="221" width="9" height="9" fill="{GREEN}"/>'
                + rich(cx - st_w / 2 + 18, 231, status, 15))
        splash_at, splash_size = (392, 52), 9
    else:
        assert 56 + rich_w(tag, 22) < 630, rich_w(tag, 22)
        copy = (rich(56, 70, eyebrow, 10)
                + title_text(52, 150, 64, "start")
                + rich(56, 200, tag, 22)
                + f'<rect class="blink" x="56" y="224" width="10" height="10" fill="{GREEN}"/>'
                + rich(76, 234, status, 17))
        splash_at, splash_size = (690, 84), 13
    splash = (f'<g transform="translate({splash_at[0]} {splash_at[1]}) rotate(-14)"><g class="splash">'
              f'{text(0, 0, "Now with ML!", splash_size, GREEN, "px", "middle", shadow="#16300C")}</g></g>')

    hud = [brackets(14, 14, w - 28, h - 28, 22, 3, CYAN, .7)]
    if not m:
        hud.append(text(w - 40, 40, "OVERWORLD // NIGHT", 8, MUTED, "px", "end"))
    hud.append(hotbar(w, h, 32 if m else 38, 16 if m else 12))

    body = f"""  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#05080F"/><stop offset=".55" stop-color="#0B1328"/><stop offset=".85" stop-color="#151A3C"/><stop offset="1" stop-color="#211A4A"/></linearGradient>
    <linearGradient id="beamg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{CYAN}" stop-opacity="0"/><stop offset=".6" stop-color="{CYAN}" stop-opacity=".7"/><stop offset="1" stop-color="{CYAN}"/></linearGradient>
    <linearGradient id="beamc" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{CYAN_L}" stop-opacity="0"/><stop offset=".5" stop-color="{CYAN_L}" stop-opacity=".7"/><stop offset="1" stop-color="{CYAN_L}"/></linearGradient>
    <radialGradient id="spill" gradientUnits="userSpaceOnUse" cx="{bcx}" cy="{gy}" r="{220 if m else 280}"><stop offset="0" stop-color="{CYAN}" stop-opacity=".3"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></radialGradient>
    <linearGradient id="tgrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFFFFF"/><stop offset=".55" stop-color="#C9FCFF"/><stop offset="1" stop-color="{CYAN}"/></linearGradient>
    <filter id="glow" x="-10%" y="-40%" width="120%" height="180%"><feGaussianBlur stdDeviation="7"/></filter>
    <clipPath id="frame"><path d="{pk.nrect(0, 0, w, h, 6)}"/></clipPath>
    {defs}
  </defs>
  <g clip-path="url(#frame)">
  <rect width="{w}" height="{h}" fill="url(#sky)"/>
  {''.join(bg)}
  {beam}
  {''.join(terrain)}
  {plants}
  <rect x="0" y="{gy}" width="{w}" height="{h - gy}" fill="{NIGHT}" fill-opacity=".45"/>
  <rect x="0" y="{gy - 180}" width="{w}" height="{h - gy + 180}" fill="url(#spill)"/>
  {beacon}
  {creeper}
  {''.join(scene)}
  {copy}
  {splash}
  {''.join(hud)}
  </g>
  <path d="{pk.nrect(0, 0, w, h, 6)}{pk.nrect(2, 2, w - 4, h - 4, 6)}" fill="{EDGE}" fill-rule="evenodd"/>"""
    css = """.tw { animation: tw 3.2s steps(1) infinite; }
    @keyframes tw { 50% { opacity: .15; } }
    .beam { animation: beam 2.6s ease-in-out infinite alternate; }
    @keyframes beam { from { opacity: .8; } to { opacity: 1; } }
    .splash { animation: splash .5s ease-in-out infinite alternate; }
    @keyframes splash { from { transform: scale(1); } to { transform: scale(1.08); } }
    .creeper { animation: creep 12s linear infinite; }
    @keyframes creep { 0% { transform: translateX(%CS%px); opacity: 1; } 50%, 79.9% { transform: translateX(%CE%px); opacity: 1; }
      80%, 100% { transform: translateX(%CE%px); opacity: 0; } }
    .cwalk { animation: cwalk 12s steps(1) infinite; }
    @keyframes cwalk { 0% { opacity: 1; } 50% { opacity: 0; } }
    .cstand { animation: cstand 12s steps(1) infinite; opacity: 0; }
    @keyframes cstand { 0% { opacity: 0; } 50% { opacity: 1; } }
    .swell { animation: swell 12s linear infinite; }
    @keyframes swell { 0%, 62% { transform: scale(1); } 66% { transform: scale(1.05, 1.03); } 70% { transform: scale(1); }
      74% { transform: scale(1.08, 1.05); } 78% { transform: scale(1.12, 1.08); } 80%, 100% { transform: scale(1.16, 1.1); } }
    .flash { animation: flash 12s steps(1) infinite; opacity: 0; }
    @keyframes flash { 0% { opacity: 0; } 64% { opacity: .5; } 66% { opacity: 0; } 69% { opacity: .55; } 71% { opacity: 0; }
      74% { opacity: .6; } 76% { opacity: 0; } 77.5% { opacity: .7; } 79% { opacity: 0; } }
    .hiss { animation: hiss 12s steps(1) infinite; opacity: 0; }
    @keyframes hiss { 0% { opacity: 0; } 62% { opacity: 1; } 80% { opacity: 0; } }
    .swing { animation: swing 4s ease-in infinite; }
    @keyframes swing {
      0% { transform: rotate(-150deg); } 5% { transform: rotate(-48deg); } 10% { transform: rotate(-150deg); }
      15% { transform: rotate(-48deg); } 20% { transform: rotate(-150deg); } 25% { transform: rotate(-48deg); }
      30% { transform: rotate(-150deg); } 35% { transform: rotate(-48deg); } 40% { transform: rotate(-150deg); }
      45% { transform: rotate(-48deg); } 50% { transform: rotate(-150deg); } 55% { transform: rotate(-48deg); }
      62%, 90% { transform: rotate(-12deg); } 100% { transform: rotate(-150deg); } }
    .ore { animation: ore 4s steps(1) infinite; }
    @keyframes ore { 0% { opacity: 1; } 55% { opacity: 0; } 94% { opacity: 1; } }
    .drop { animation: drop 4s linear infinite; opacity: 0; }
    @keyframes drop {
      0%, 54.9% { opacity: 0; transform: none; }
      55% { opacity: 1; transform: none; }
      60% { opacity: 1; transform: translate(4px, -20px); }
      66% { opacity: 1; transform: translate(8px, 12px); }
      72% { opacity: 1; transform: translate(8px, 7px); }
      78% { opacity: 1; transform: translate(8px, 12px); }
      86% { opacity: 1; transform: translate(-80px, -10px) scale(.5); }
      87%, 100% { opacity: 0; transform: translate(-80px, -10px) scale(.5); } }
    .plus { animation: plus 4s linear infinite; opacity: 0; }
    @keyframes plus { 0%, 86% { opacity: 0; transform: none; } 87% { opacity: 1; transform: none; }
      97% { opacity: 1; transform: translateY(-14px); } 98%, 100% { opacity: 0; } }
    """.replace("%CS%", str(c_start)).replace("%CE%", str(c_stop)) + "\n    ".join(
        f".ck{i} {{ animation: ck{i} 4s steps(1) infinite; opacity: 0; }}"
        f"@keyframes ck{i} {{ 0% {{ opacity: 0; }} {10 * i - 5}% {{ opacity: 1; }} {10 * i + 5}% {{ opacity: 0; }} }}"
        for i in range(1, 6)) + "\n    " + "\n    ".join(part_css)
    label = ("QCUTEDEV: student dev, AI enjoyer, future full-time dev. Status: shipping ML into real apps. "
             "Splash text: Now with ML! A night-time pixel block world with a far-off neon city and a cyan light beam; "
             "a pixel dev in a purple hoodie mines a diamond ore block that drops the skills one by one (python, java, docker...) "
             "while a creeper sneaks up from behind, hisses and poofs into smoke, above a game hotbar.")
    return svg(w, h, label, body, css)


# ---------------------------------------------------------------- about: player terminal (chat console)
ME = [("<", MUTED, "tx"), ("qcutedev", CYAN, "tb"), ("> ", MUTED, "tx")]
MESSAGES = [
    [("hi! I'm a ", SOFT, "tx"), ("Student Developer", TEXT, "tb")],
    [("I love ", SOFT, "tx"), ("AI", TEXT, "tb"), (", ", SOFT, "tx"), ("Machine Learning", TEXT, "tb"),
     (" & ", SOFT, "tx"), ("Computer Vision", TEXT, "tb")],
    [("learned in class: ", SOFT, "tx"), ("Java, Python, C", TEXT, "tb")],
    [("I build with: ", SOFT, "tx"), ("Python, Dart, TypeScript", TEXT, "tb")],
    [("now: ", SOFT, "tx"), ("turning ML models into real apps", CYAN, "tb")],
    [("goal: ", SOFT, "tx"), ("Full-time Software Developer", GREEN, "tb")],
]
ADVANCEMENT = [("qcutedev has made the advancement ", SOFT, "tx"), ("[Ship ML to a real app]", GREEN, "tb")]
QUEST = "/quest accept full-time-dev"


def toast(x: float, y: float, tw_: float, th: float) -> str:
    s = th - 20
    return (f'<g class="toast"><g transform="translate({x:g} {y:g})">'
            + box(0, 0, tw_, th, SLOTBG, CYAN_D, 2, 4)
            + box(10, 10, s, s, PANEL2, EDGE2, 2, 2)
            + sprite(PICK, gem_pal(DIAMOND), (s - 10) / 12, 15, 15)
            + text(s + 22, th / 2 - 4, "Advancement Made!", 9, GREEN, "px")
            + text(s + 22, th / 2 + 18, "Ship ML to a real app", 16, TEXT)
            + "</g></g>")


def about(m: bool) -> str:
    w = 480 if m else 1000
    size, pitch, gap = (16, 24, 12) if m else (18, 26, 12)
    tx0 = 52 if m else 56
    maxw = w - tx0 - 20
    head = sprite(pk.DEV_HEAD, pk.DEV_PAL, 2, -8, 0)
    rows, y = [], (146 if m else 100)
    rows.append(f'<rect x="{tx0 - 26}" y="{y - 11}" width="8" height="8" fill="{GREEN}"/>'
                + text(tx0, y, "qcutedev joined the game", size - 2, GREEN))
    y += 46
    for msg in MESSAGES + [None]:
        toks = ME + msg if msg else ADVANCEMENT
        lines = wrap(toks, size, maxw)
        assert m or len(lines) == 1, toks
        icon = (f'<g transform="translate({tx0 - 26} {y - 15})">{head}</g>' if msg else
                f'<g transform="translate({tx0 - 28} {y - 14})">{sprite(GEM, gem_pal(EMERALD), 1.6)}</g>')
        texts = "".join(rich(tx0, y + k * pitch, ln, size) for k, ln in enumerate(lines))
        rows.append(icon + texts)
        y += (len(lines) - 1) * pitch + (pitch + gap)
    iy = y + 4
    h = iy + 40 + 18
    rows.append(box(16, iy, w - 32, 40, SLOTBG, EDGE2, 2, 4)
                + text(30, iy + 27, ">", 12, CYAN, "px")
                + text(tx0, iy + 27, QUEST, size - 1, TEXT)
                + f'<rect class="blink" x="{tx0 + tw(QUEST, size - 1) + 6:g}" y="{iy + 11}" width="9" height="19" fill="{CYAN}"/>')
    if m:
        toast_svg = toast(16, 56, w - 32, 62)
        frame = panel(w, h, "PLAYER TERMINAL", "", 40, 10)
    else:
        toast_svg = toast(w - 24 - 340, 62, 340, 62)
        frame = panel(w, h, "PLAYER TERMINAL", "qcutedev@overworld:~")
    body = f"""  {frame}
  {''.join(rows)}
  {toast_svg}"""
    css = """.toast { animation: toast .5s ease-out 3.6s both; }
    @keyframes toast { from { opacity: 0; transform: translateY(-12px); } to { opacity: 1; transform: none; } }"""
    label = ("Player terminal chat log. qcutedev joined the game. hi! I'm a Student Developer. "
             "I love AI, Machine Learning and Computer Vision. Learned in class: Java, Python, C. "
             "I build with: Python, Dart, TypeScript. Now: turning ML models into real apps. "
             "Goal: Full-time Software Developer. Advancement made: Ship ML to a real app. "
             "Command: /quest accept full-time-dev.")
    return svg(w, h, label, body, css)


# ---------------------------------------------------------------- inventory (skills)
SKILLS = [
    ("languages", DIAMOND, "code", ["python", "dart", "typescript", "javascript", "java", "c"]),
    ("ai-ml", AMETHYST, "spark", ["scikit-learn", "pytorch", "xgboost", "pandas", "numpy"]),
    ("backend", EMERALD, "db", ["fastapi", "flask", "sqlalchemy", "postgresql", "postgis", "prisma"]),
    ("mobile-web", LAPIS, "phone", ["flutter", "next.js", "react", "tailwindcss"]),
    ("tooling", QUARTZ, "gear", ["docker", "github-actions", "git", "uv", "render"]),
    ("testing", PRISMARINE, "check", ["pytest", "vitest", "playwright"]),
]


def skills(m: bool) -> str:
    total = sum(len(i) for *_, i in SKILLS)
    chips, rows = [], []
    if m:
        w, fs, ch = 480, 14, 30
        ore_px = 1.625
        y = 58
        for i, (cat, ore, icon, items) in enumerate(SKILLS):
            rows.append(box(16, y, 30, 30, SLOTBG, EDGE2, 2, 2)
                        + f'<rect x="18" y="{y + 2}" width="26" height="26" fill="url(#ico{i})"/>'
                        + text(58, y + 20, cat.upper(), 9, TEXT, "px")
                        + text(w - 16, y + 20, f"{len(items)} items", 13, MUTED, "tx", "end"))
            y += 40
            x = 16
            for it in items:
                cw = 36 + tw(it, fs) + 10
                if x + cw > w - 16:
                    x, y = 16, y + ch + 6
                rows.append(box(x, y, cw, ch, SLOTBG, EDGE2, 2, 2)
                            + pk.tech_icon(it, 2, x + 6, y, ch)
                            + text(x + 36, y + 20, it, fs, TEXT))
                chips.append(f'<rect x="{x + 2:g}" y="{y + 2}" width="{cw - 4:g}" height="{ch - 4}"/>')
                x += cw + 6
            y += ch + 20
        h = y + 2
        frame = panel(w, h, "INVENTORY", f"{total} items", 40, 10)
    else:
        w, fs, top, rh = 1000, 15, 66, 46
        ore_px = 2
        for i, (cat, ore, icon, items) in enumerate(SKILLS):
            y = top + i * rh
            rows.append(box(24, y, 36, 36, SLOTBG, EDGE2, 2, 2)
                        + f'<rect x="26" y="{y + 2}" width="32" height="32" fill="url(#ico{i})"/>'
                        + text(74, y + 23, cat.upper(), 10, TEXT, "px"))
            x = 224
            for it in items:
                cw = 40 + tw(it, fs) + 12
                rows.append(box(x, y + 2, cw, 32, SLOTBG, EDGE2, 2, 2)
                            + pk.tech_icon(it, 2, x + 8, y + 2, 32)
                            + text(x + 40, y + 23, it, fs, TEXT))
                chips.append(f'<rect x="{x + 2:g}" y="{y + 4}" width="{cw - 4:g}" height="28"/>')
                x += cw + 8
            assert x < w - 16, (cat, x)
        h = top + len(SKILLS) * rh + 10
        frame = panel(w, h, "INVENTORY", f"{len(SKILLS)} categories / {total} items")
    defs = "".join(tex_pattern(f"ico{i}", tex_ore(60 + i, ore, tex_deepslate), DEEP_BASE, ore_px)
                   for i, (_, ore, _, _) in enumerate(SKILLS))
    body = f"""  <defs>{defs}<clipPath id="chips">{''.join(chips)}</clipPath>
    <linearGradient id="glint" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{PURPLE}" stop-opacity="0"/><stop offset=".5" stop-color="{PURPLE}" stop-opacity=".28"/><stop offset="1" stop-color="{PURPLE}" stop-opacity="0"/></linearGradient></defs>
  {frame}
  {''.join(rows)}
  <g clip-path="url(#chips)"><rect class="glint" x="0" y="0" width="180" height="{h}" fill="url(#glint)" transform="skewX(-20)"/></g>"""
    css = f""".glint {{ animation: glint 4s linear infinite; }}
    @keyframes glint {{ from {{ translate: -200px 0; }} to {{ translate: {w + 200}px 0; }} }}"""
    label = "Inventory of skills. " + ". ".join(f"{c}: {', '.join(i)}" for c, _, _, i in SKILLS)
    return svg(w, h, label, body, css)


# ---------------------------------------------------------------- section headers
HEADERS = {
    "projects": ("PROJECTS", [("/tp @s ~/projects", MUTED)], "4 BUILDS", "pick"),
    "snake-title": ("WORLD MAP", [("contributions explored over the last year", SOFT),
                                  ("/gamerule snakeEatsCommits true", MUTED)], "UPDATED DAILY", "map"),
}


def header(kind: str, m: bool) -> str:
    title, subs, right, icon = HEADERS[kind]
    w = 480 if m else 1000
    if m:
        lines = [[(s, c, "tx")] for s, c in subs]
    else:
        joined = []
        for k, (s, c) in enumerate(subs):
            joined += [(s, c, "tx")] + ([("   ", DIM, "tx")] if k < len(subs) - 1 else [])
        lines = [joined]
    fs, tsize, slot_s, rsize = (14, 12, 36, 8) if m else (15, 14, 44, 9)
    title_y = 22 + tsize
    h = title_y + len(lines) * (fs + 8) + 16
    ix, iy = 16, (h - slot_s) / 2
    if icon == "pick":
        art_svg = sprite(PICK, gem_pal(DIAMOND), (slot_s - 12) / 12, ix + 6, iy + 7)
    else:
        art_svg = sprite(MAP, MAP_PAL, (slot_s - 10) / 16, ix + 5, iy + 6)
    tx0 = ix + slot_s + 16
    for ln in lines:
        assert tx0 + rich_w(ln, fs) < w - 16, ln
    dot_x = w - 20 - tw(right, rsize, "px") - 14
    body = (box(0, 0, w, h, PANEL, EDGE, 2, 6)
            + f'<rect x="8" y="2" width="120" height="2" fill="{CYAN}"/><rect x="128" y="2" width="36" height="2" fill="{PURPLE}"/>'
            + box(ix, iy, slot_s, slot_s, SLOTBG, EDGE2, 2, 2) + art_svg
            + text(tx0, title_y, title, tsize, TEXT, "px")
            + "".join(rich(tx0, title_y + (k + 1) * (fs + 8), ln, fs) for k, ln in enumerate(lines))
            + f'<rect class="blink" x="{dot_x:g}" y="{title_y - rsize}" width="8" height="8" fill="{GREEN if icon == "map" else CYAN}"/>'
            + text(w - 20, title_y, right, rsize, CYAN, "px", "end"))
    label = f"{title.title()}: " + " ".join(s for s, _ in subs)
    return svg(w, h, label, body)


# ---------------------------------------------------------------- project build cards
CARDS = [
    ("rideros", "rideros-ai", "RIDEROS AI", "dart", "map",
     "Rider productivity app with 3 custom ML models: pickup-time regression, a road-photo classifier, K-Means work patterns.",
     ["#flutter", "#fastapi", "#postgis", "#pytorch"]),
    ("sleepwise", "Project-Sleep", "SLEEPWISE AI", "dart", "bed",
     "Android app that predicts sleep quality from a daily check-in, plus a sleep-cycle alarm and sleep sounds.",
     ["#flutter", "#fastapi", "#scikit-learn"]),
    ("marketplace", "web-shopping", "THAI MARKETPLACE", "typescript", "emerald",
     "Thai multi-vendor marketplace where customers, sellers and admins trade on one platform.",
     ["#nextjs", "#typescript", "#postgresql", "#prisma"]),
    ("mllab", "ml-deployment-lab", "ML DEPLOY LAB", "python", "potion",
     "Model as a Service: a random-forest house-price model served by Flask and packaged in Docker.",
     ["#flask", "#docker", "#scikit-learn"]),
]


def art(kind: str, x: float, y: float, s: float) -> tuple[str, str]:
    """Card artwork: deepslate backdrop, cyan floor light, animated item icon."""
    p = s * .6 / 16
    out = (box(x, y, s, s, SLOTBG, EDGE2, 2, 4)
           + f'<path d="{pk.nrect(x + 2, y + 2, s - 4, s - 4, 4)}" fill="url(#deep)" opacity=".55"/>'
           + "".join(f'<rect x="{x + s / 2 - s * f / 2:g}" y="{y + s - 26 + k * 5:g}" width="{s * f:g}" height="5" '
                     f'fill="{CYAN}" fill-opacity="{o}"/>' for k, (f, o) in enumerate(((.5, .1), (.7, .12), (.85, .08))))
           + brackets(x + 8, y + 8, s - 16, s - 16, 8, 2, CYAN, .5))
    rows = {"map": MAP, "bed": BED, "emerald": GEM, "potion": POTION}[kind]
    q = p * 1.6 if kind == "emerald" else p
    iw, ih = len(rows[0]) * q, len(rows) * q
    ix, iy = x + (s - iw) / 2, y + (s - ih) / 2 - s * .05
    if kind == "map":
        return (out + sprite(MAP, MAP_PAL, q, ix, iy) + f'<g class="pin">{sprite(PIN, PIN_PAL, q, ix + 9 * q, iy + 2 * q)}</g>',
                ".pin { animation: pin .8s ease-in-out infinite alternate; } @keyframes pin { to { translate: 0 -5px; } }")
    if kind == "bed":
        zs = "".join(f'<g class="z z{i}">{text(ix + 10 * q + i * 2.4 * q, iy - q - i * 2.6 * q, "z", round(q * 1.6 + i * q * .6), CYAN_L, "px")}</g>'
                     for i in range(3))
        return (out + sprite(BED, BED_PAL, q, ix, iy) + zs,
                ".z { animation: zz 2.4s linear infinite; opacity: 0; } .z1 { animation-delay: .8s; } .z2 { animation-delay: 1.6s; }"
                "@keyframes zz { 0% { opacity: 0; } 15% { opacity: 1; } 80% { opacity: 1; translate: 4px -6px; } 100% { opacity: 0; translate: 6px -8px; } }")
    if kind == "emerald":
        sx, sy, u = ix + iw - q, iy - q, q * .7
        spark = (f'<g class="spark"><rect x="{sx - u / 2:g}" y="{sy - 2 * u:g}" width="{u:g}" height="{u * 4:g}" fill="#FFF"/>'
                 f'<rect x="{sx - 2 * u:g}" y="{sy - u / 2:g}" width="{u * 4:g}" height="{u:g}" fill="#FFF"/></g>')
        return (out + sprite(GEM, gem_pal(EMERALD), q, ix, iy) + spark,
                ".spark { animation: spark 1.6s steps(1) infinite; } @keyframes spark { 50% { opacity: 0; } }")
    bubbles = "".join(f'<rect class="bb b{i}" x="{ix + 6.5 * q + i * 2 * q:g}" y="{iy + 11 * q:g}" width="{q * .8:g}" '
                      f'height="{q * .8:g}" fill="{CYAN_L}"/>' for i in range(2))
    return (out + sprite(POTION, POTION_PAL, q, ix, iy) + bubbles,
            ".bb { animation: bb 1.4s linear infinite; } .b1 { animation-delay: .7s; }"
            "@keyframes bb { 0% { opacity: 0; } 20% { opacity: 1; } 100% { opacity: 0; translate: 0 -14px; } }")


def tag_chips(x0: float, y: float, tags: list[str], fs: float, maxx: float, ch: float = 24) -> tuple[str, float]:
    out, x = [], x0
    for t in tags:
        cw = tw(t, fs) + 20
        if x + cw > maxx:
            x, y = x0, y + ch + 8
        out.append(box(x, y, cw, ch, "#140F28", PURPLE_D, 2, 2) + text(x + 10, y + ch / 2 + fs / 2 - 2, t, fs, PURPLE_L))
        x += cw + 8
    return "".join(out), y + ch


def button(x: float, y: float, w: float, h: float, label: str, size: float) -> str:
    return (box(x, y, w, h, SLOTBG, CYAN_D, 2, 2)
            + text(x + w / 2, y + h / 2 + size / 2, label, size, CYAN, "px", "middle"))


def card(i: int, m: bool) -> str:
    slug, repo, title, lang, kind, desc, tags = CARDS[i]
    url = f"github.com/{USER}/{repo}"
    eyebrow = [(f"BUILD 0{i + 1}", CYAN, "px"), ("  //  ", DIM, "px"), (lang.upper(), MUTED, "px")]
    btn = "VIEW REPO >"
    if m:
        w, s, tx0 = 480, 104, 136
        assert tx0 + tw(title, 13, "px") < w - 16 and tx0 + tw(url, 13) < w - 16, title
        dl = wrap([(desc, SOFT, "tx")], 16, w - 32)
        y = 150
        desc_svg = "".join(rich(16, y + k * 23, ln, 16) for k, ln in enumerate(dl))
        tags_svg, ty = tag_chips(16, y + (len(dl) - 1) * 23 + 18, tags, 13, w - 16)
        by = ty + 14
        h = by + 36 + 16
        art_svg, art_css = art(kind, 16, 16, s)
        head = rich(tx0, 38, eyebrow, 8) + text(tx0, 66, title, 13, TEXT, "px") + text(tx0, 92, url, 13, MUTED)
        btn_svg = button(16, by, w - 32, 36, btn, 9)
    else:
        w, h, s, tx0 = 1000, 200, 160, 204
        dl = wrap([(desc, SOFT, "tx")], 16, w - tx0 - 28)
        assert len(dl) <= 2, dl
        desc_svg = "".join(rich(tx0, 126 + k * 22, ln, 16) for k, ln in enumerate(dl))
        bw = tw(btn, 9, "px") + 32
        tags_svg, _ = tag_chips(tx0, 160, tags, 13, w - 28 - bw - 16)
        art_svg, art_css = art(kind, 20, 20, s)
        head = rich(tx0, 42, eyebrow, 9) + text(tx0, 74, title, 20, TEXT, "px") + text(tx0, 98, url, 14, MUTED)
        btn_svg = button(w - 20 - bw, 158, bw, 28, btn, 9)
    body = f"""  <defs>{tex_pattern("deep", tex_deepslate(44), DEEP_BASE, 2.5)}{tex_pattern("panelstone", tex_deepslate(45), DEEP_BASE, 3)}</defs>
  {box(0, 0, w, h, PANEL, EDGE, 2, 6)}
  <path d="{pk.nrect(2, 2, w - 4, h - 4, 6)}" fill="url(#panelstone)" opacity=".07"/>
  <rect x="8" y="2" width="120" height="2" fill="{CYAN}"/><rect x="128" y="2" width="36" height="2" fill="{PURPLE}"/>
  {art_svg}
  {head}
  {desc_svg}
  {tags_svg}
  {btn_svg}"""
    label = f"Project {title.title()} ({lang}), {url}: {desc} Tags: {' '.join(tags)}."
    return svg(w, h, label, body, art_css)


# ---------------------------------------------------------------- footer: portal ending
def footer(m: bool) -> str:
    w = 480 if m else 1000
    fb, cols, rows = 30, (14 if m else 26), 7
    fw, fh = cols * fb, rows * fb
    fx, fy = (w - fw) / 2, 16
    h = fy + fh + 16
    ix, iy, iw, ih = fx + fb, fy + fb, fw - 2 * fb, fh - 2 * fb
    rng = random.Random(99)
    ring = f'<path d="M{fx:g} {fy}h{fw}v{fh}h-{fw}zM{ix:g} {iy}v{ih}h{iw}v-{ih}z" fill="url(#obs)" fill-rule="evenodd"/>'
    cells, eyes = [], []
    for c in range(cols):
        for r in range(rows):
            if 0 < c < cols - 1 and 0 < r < rows - 1:
                continue
            bx, by = fx + c * fb, fy + r * fb
            cells.append(f'<rect x="{bx + .5:g}" y="{by + .5:g}" width="{fb - 1}" height="{fb - 1}"/>')
            if r in (0, rows - 1) and c % 3 == 2 and c < cols - 2:
                eyes.append(f'<g class="eye" style="animation-delay:-{rng.uniform(0, 2.4):.1f}s">'
                            f'{sprite(EYE, EYE_PAL, 3, bx + 6, by + 6)}</g>')
    layers = []
    specs = (36, 18, 10) if m else (70, 40, 18)
    palettes = (["#2B6F7A", PURPLE_D], [CYAN, PURPLE], [CYAN_L, GREEN, PURPLE_L])
    for li, (n, pal, dur) in enumerate(zip(specs, palettes, (60, 36, 20))):
        sz = (2, 3, 4)[li]
        dots = []
        for _ in range(n):
            x0, y0 = rng.uniform(0, iw), rng.uniform(0, ih - sz)
            col, op = rng.choice(pal), rng.uniform(.4, .95)
            for off in (0, iw):
                dots.append(f'<rect x="{ix + x0 + off:.1f}" y="{iy + y0:.1f}" width="{sz}" height="{sz}" fill="{col}" fill-opacity="{op:.2f}"/>')
        layers.append(f'<g class="drift" style="animation-duration:{dur}s">{"".join(dots)}</g>')
    cx, cy = w / 2, iy + ih / 2
    if m:
        msg = (text(cx, cy - 10, "Thanks 4 visiting!", 16, TEXT, "px", "middle", shadow=PURPLE_D)
               + text(cx, cy + 18, "Saving world... done.", 15, SOFT, "tx", "middle")
               + text(cx, cy + 38, "See you next session.", 15, SOFT, "tx", "middle"))
        pw, ph, py = 320, 86, cy - 38
    else:
        msg = (text(cx, cy - 4, "Thanks 4 visiting!", 22, TEXT, "px", "middle", shadow=PURPLE_D)
               + text(cx, cy + 28, "Saving world... done. See you next session.", 18, SOFT, "tx", "middle"))
        pw, ph, py = 560, 84, cy - 42
    body = f"""  <defs>
    {tex_pattern("obs", tex_obsidian(12), OBS_BASE, 1.875, (fx, fy))}
    <linearGradient id="void" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#062A30" stop-opacity=".55"/><stop offset=".5" stop-color="#03060C" stop-opacity="0"/><stop offset="1" stop-color="#2A1A5C" stop-opacity=".55"/></linearGradient>
    <clipPath id="portal"><rect x="{ix:g}" y="{iy}" width="{iw}" height="{ih}"/></clipPath>
  </defs>
  {box(0, 0, w, h, NIGHT, EDGE, 2, 6)}
  <rect x="{ix:g}" y="{iy}" width="{iw}" height="{ih}" fill="#03060C"/>
  <rect x="{ix:g}" y="{iy}" width="{iw}" height="{ih}" fill="url(#void)"/>
  <g clip-path="url(#portal)">{''.join(layers)}</g>
  {ring}
  <g fill="none" stroke="#000" stroke-opacity=".45">{''.join(cells)}</g>
  {''.join(eyes)}
  <path d="{pk.nrect(cx - pw / 2, py, pw, ph, 4)}" fill="{NIGHT}" fill-opacity=".72"/>
  {msg}"""
    css = f""".drift {{ animation: drift linear infinite; }}
    @keyframes drift {{ from {{ transform: none; }} to {{ transform: translateX(-{iw}px); }} }}
    .eye {{ animation: eye 2.4s ease-in-out infinite alternate; }}
    @keyframes eye {{ from {{ opacity: .55; }} to {{ opacity: 1; }} }}"""
    label = "Thanks 4 visiting! Saving world... done. See you next session. A pixel portal frame with a drifting starfield."
    return svg(w, h, label, body, css)


files = {}
for mobile, suf in ((False, ""), (True, "-m")):
    files[f"banner{suf}.svg"] = hero(mobile)
    files[f"about{suf}.svg"] = about(mobile)
    files[f"skills{suf}.svg"] = skills(mobile)
    files[f"projects{suf}.svg"] = header("projects", mobile)
    for idx, c in enumerate(CARDS):
        files[f"card-{c[0]}{suf}.svg"] = card(idx, mobile)
    files[f"snake-title{suf}.svg"] = header("snake-title", mobile)
    files[f"footer{suf}.svg"] = footer(mobile)
for name, content in files.items():
    (OUT / name).write_text(content, encoding="utf-8")
    print(f"{name:26} {len(content.encode()) / 1024:6.1f} KB")
