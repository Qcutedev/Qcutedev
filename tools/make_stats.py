"""Draw the live 'Player Stats' HUD from real GitHub data (run daily by .github/workflows/snake.yml).

usage: GITHUB_TOKEN=... python make_stats.py <fonts-dir> <out-dir> [login]      (needs: pip install fonttools)
Writes stats.svg (1000 px wide) and stats-m.svg (480 px wide). Every number comes from the GitHub GraphQL API:
public non-fork repos owned by <login> (count, stars, language bytes), followers, and the public contribution
calendar of the last year (total and streaks). Advancements are fixed thresholds checked against those numbers.
Any API error exits non-zero and writes nothing, so the workflow keeps the previously published files.
"""
import datetime as dt
import json
import os
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pixelkit as pk  # noqa: E402
from pixelkit import (CAT_ICONS, CYAN, DIAMOND, DIM, EDGE2, GEM, GREEN, MUTED, PURPLE, SLOTBG,  # noqa: E402
                      TEXT, box, gem_pal, panel, sprite, svg, text, tw)

QUERY = """query($login: String!) { user(login: $login) { login followers { totalCount }
  repositories(first: 100, ownerAffiliations: OWNER, privacy: PUBLIC, isFork: false) { totalCount
    nodes { stargazerCount languages(first: 10, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name } } } } }
  contributionsCollection { contributionCalendar { totalContributions weeks { contributionDays { contributionCount } } } } } }"""
LANG_COLORS = [CYAN, PURPLE, GREEN, "#6C8BD8", "#B9C4D6", "#56627A"]
LOCKED = ("#9AA3B5", "#5D6679", "#353C4B")


def fetch(login: str, token: str) -> dict:
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {token}", "User-Agent": "profile-stats-hud", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)
    user = (data.get("data") or {}).get("user")
    if data.get("errors") or not user:
        raise SystemExit(f"GitHub API error: {data.get('errors')}")
    return user


def summarize(u: dict) -> dict:
    nodes = u["repositories"]["nodes"]
    langs: dict[str, int] = {}
    for n in nodes:
        for e in n["languages"]["edges"]:
            langs[e["node"]["name"]] = langs.get(e["node"]["name"], 0) + e["size"]
    cal = u["contributionsCollection"]["contributionCalendar"]
    counts = [d["contributionCount"] for wk in cal["weeks"] for d in wk["contributionDays"]]
    longest = run = 0
    for c in counts:
        run = run + 1 if c > 0 else 0
        longest = max(longest, run)
    current, i = 0, len(counts) - 1
    if i >= 0 and counts[i] == 0:  # today may not have activity yet
        i -= 1
    while i >= 0 and counts[i] > 0:
        current, i = current + 1, i - 1
    total_bytes = sum(langs.values()) or 1
    top = sorted(langs.items(), key=lambda kv: -kv[1])
    shown = [(name, size / total_bytes) for name, size in top[:5]]
    rest = sum(size for _, size in top[5:]) / total_bytes
    if rest > 0:
        shown.append(("other", rest))
    return {"login": u["login"], "repos": u["repositories"]["totalCount"],
            "stars": sum(n["stargazerCount"] for n in nodes), "followers": u["followers"]["totalCount"],
            "contrib": cal["totalContributions"], "current": current, "longest": longest,
            "langs": shown, "lang_count": len(langs)}


def advancements(s: dict) -> list[tuple[str, str, bool]]:
    return [("Hello, World", "publish a public repo", s["repos"] >= 1),
            ("Polyglot", "use 4+ languages", s["lang_count"] >= 4),
            ("Grinder", "100+ contributions in a year", s["contrib"] >= 100),
            ("On Fire", "7-day contribution streak", s["longest"] >= 7),
            ("Stargazer", "earn a star on a repo", s["stars"] >= 1)]


def tiles(s: dict) -> list[tuple[str, int, str, str, str]]:
    return [("CONTRIBUTIONS", s["contrib"], "last 12 months", "spark", CYAN),
            ("CURRENT STREAK", s["current"], "days", "check", GREEN),
            ("LONGEST STREAK", s["longest"], "days", "check", GREEN),
            ("PUBLIC REPOS", s["repos"], "non-fork", "code", CYAN),
            ("STARS EARNED", s["stars"], "on public repos", "spark", PURPLE),
            ("FOLLOWERS", s["followers"], "on GitHub", "phone", PURPLE)]


def tile(x: float, y: float, w: float, h: float, label: str, value: int, sub: str, icon: str, color: str, vsize: float) -> str:
    return (box(x, y, w, h, SLOTBG, EDGE2, 2, 3)
            + text(x + 12, y + 22, label, 7, MUTED, "px")
            + sprite(CAT_ICONS[icon], {"C": color}, 2, x + w - 24, y + 11)
            + text(x + 12, y + 30 + vsize, f"{value:,}", vsize, TEXT, "px")
            + text(x + 12, y + h - 12, sub, 13, DIM))


def lang_block(x: float, y: float, w: float, langs: list[tuple[str, float]], col_w: float, fs: float) -> tuple[str, float]:
    out = [text(x, y + 14, "TOP LANGUAGES", 8, MUTED, "px")]
    bx, by, bw = x, y + 28, w
    cur = bx
    for k, (name, share) in enumerate(langs):
        sw = max(2.0, (bw - 2 * (len(langs) - 1)) * share)
        out.append(f'<rect x="{cur:.1f}" y="{by}" width="{sw:.1f}" height="14" fill="{LANG_COLORS[k]}"/>')
        cur += sw + 2
    out.append(f'<rect x="{bx}" y="{by + 10}" width="{bw}" height="4" fill="#000" fill-opacity=".25"/>')
    ly = by + 46
    for k, (name, share) in enumerate(langs):
        cx, cy = x + (k % 2) * col_w, ly + (k // 2) * 26
        out.append(f'<rect x="{cx}" y="{cy - 10}" width="10" height="10" fill="{LANG_COLORS[k]}"/>'
                   + text(cx + 18, cy, name, fs, TEXT) + text(cx + col_w - 24, cy, f"{share * 100:.1f}%", fs, MUTED, "tx", "end"))
    return "".join(out), ly + ((len(langs) + 1) // 2 - 1) * 26 + 8


def adv_rows(x: float, y: float, w: float, advs: list[tuple[str, str, bool]], m: bool) -> tuple[str, float]:
    done = sum(a[2] for a in advs)
    out = [text(x, y + 14, "ADVANCEMENTS", 8, MUTED, "px"), text(x + w, y + 14, f"{done}/{len(advs)}", 8, CYAN, "px", "end")]
    yy = y + 40
    for name, req, ok in advs:
        pal = gem_pal(DIAMOND if ok else LOCKED)
        state = ("UNLOCKED", GREEN) if ok else ("LOCKED", DIM)
        out.append(sprite(GEM, pal, 1.4, x, yy - 11) + text(x + 22, yy, name, 15, TEXT if ok else MUTED, "tb")
                   + text(x + w, yy, state[0], 7, state[1], "px", "end"))
        if m:
            out.append(text(x + 22, yy + 18, req, 13, DIM))
            yy += 42
        else:
            assert x + 22 + tw(name, 15, "tb") + 10 + tw(req, 13) < x + w - tw("UNLOCKED", 7, "px") - 10, name
            out.append(text(x + 22 + tw(name, 15, "tb") + 10, yy, req, 13, DIM))
            yy += 24
    return "".join(out), yy


def render(s: dict, m: bool, today: str) -> str:
    advs = advancements(s)
    ts = tiles(s)
    if m:
        w, gap = 480, 8
        tw_ = (w - 32 - 2 * gap) / 3
        cells = "".join(tile(16 + (k % 3) * (tw_ + gap), 56 + (k // 3) * (84 + gap), tw_, 84, *t, 16) for k, t in enumerate(ts))
        ly = 56 + 2 * 84 + gap + 16
        langs, lend = lang_block(32, ly + 14, w - 64, s["langs"], (w - 64) / 2 + 12, 14)
        lang_box = box(16, ly, w - 32, lend - ly + 10, SLOTBG, EDGE2, 2, 3)
        ay = lend + 22
        advs_svg, aend = adv_rows(32, ay + 14, w - 64, advs, True)
        adv_box = box(16, ay, w - 32, aend - ay - 10, SLOTBG, EDGE2, 2, 3)
        h = aend + 10
        right = f"live / {today}"
        frame = panel(w, h, "PLAYER STATS", right, 40, 10)
    else:
        w, gap = 1000, 12
        tw_ = (w - 48 - 5 * gap) / 6
        cells = "".join(tile(24 + k * (tw_ + gap), 64, tw_, 94, *t, 22) for k, t in enumerate(ts))
        y0 = 176
        langs, lend = lang_block(44, y0 + 14, 440, s["langs"], 232, 15)
        advs_svg, aend = adv_rows(540, y0 + 14, 416, advs, False)
        bh = max(lend, aend) - y0 + 4
        lang_box = box(24, y0, 480, bh, SLOTBG, EDGE2, 2, 3)
        adv_box = box(520, y0, 456, bh, SLOTBG, EDGE2, 2, 3)
        h = y0 + bh + 22
        frame = panel(w, h, "PLAYER STATS", f"live data / @{s['login']} / updated {today}")
    body = f"""  {frame}
  {cells}
  {lang_box}{langs}
  {adv_box}{advs_svg}"""
    label = (f"Player stats for @{s['login']}, updated {today}: {s['contrib']} contributions in the last 12 months, "
             f"current streak {s['current']} days, longest streak {s['longest']} days, {s['repos']} public non-fork repos, "
             f"{s['stars']} stars, {s['followers']} followers. Top languages: "
             + ", ".join(f"{n} {p * 100:.1f}%" for n, p in s["langs"]) + ". Advancements: "
             + ", ".join(f"{n} ({'unlocked' if ok else 'locked'})" for n, _, ok in advs) + ".")
    return svg(w, h, label, body)


def main() -> None:
    fonts, out = Path(sys.argv[1]), Path(sys.argv[2])
    login = sys.argv[3] if len(sys.argv) > 3 else os.environ.get("GITHUB_REPOSITORY_OWNER", "Qcutedev")
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        raise SystemExit("set GITHUB_TOKEN (or GH_TOKEN)")
    s = summarize(fetch(login, token))
    pk.load_fonts(fonts)
    today = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
    out.mkdir(parents=True, exist_ok=True)
    for name, m in (("stats.svg", False), ("stats-m.svg", True)):
        content = render(s, m, today)
        (out / name).write_text(content, encoding="utf-8")
        print(f"{name:14} {len(content.encode()) / 1024:6.1f} KB")
    print(json.dumps({k: v for k, v in s.items() if k != "langs"}))


if __name__ == "__main__":
    main()
