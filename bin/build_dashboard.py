#!/usr/bin/env python3
"""Render _data/analytics.json into a self-contained dashboard.html.

    python3 bin/fetch_analytics.py && python3 bin/build_dashboard.py

Everything is pre-rendered here rather than drawn by client-side JavaScript,
so the output is a static snapshot that works anywhere it is opened.
Both the input and the output are gitignored - they are regenerated, not kept.
"""

import datetime
import html
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "_data" / "analytics.json"
OUT = ROOT / "dashboard.html"

# Cities that are datacenter regions rather than places people read from.
DATACENTRE = {"Council Bluffs", "Ashburn", "The Dalles", "Boardman", "Columbus", "Moncks Corner", "Dublin", "Mountain View"}
DAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
e = html.escape


def bar_rows(items, label_key, value_key, extra=None, limit=10):
    rows, top = [], max((i[value_key] for i in items[:limit]), default=1) or 1
    for i in items[:limit]:
        pct = i[value_key] / top * 100
        note = f'<span class="note">{e(str(extra(i)))}</span>' if extra else ""
        rows.append(
            f'<div class="row"><span class="lbl">{e(str(i[label_key]))}</span>'
            f'<span class="track"><span class="fill" style="width:{pct:.1f}%"></span></span>'
            f'<span class="val">{i[value_key]:,}</span>{note}</div>'
        )
    return "\n".join(rows)


def area_chart(daily, w=1000, h=200):
    if not daily:
        return "<p class='note'>No data.</p>"
    vals = [d["views"] for d in daily]
    peak = max(vals) or 1
    step = w / max(len(vals) - 1, 1)
    pts = [(i * step, h - (v / peak) * (h - 20)) for i, v in enumerate(vals)]
    line = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    area = f"M0,{h} L" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + f" L{w},{h} Z"

    marks, labels = [], []
    for d in sorted(daily, key=lambda x: -x["views"])[:3]:
        i = daily.index(d)
        x, y = i * step, h - (d["views"] / peak) * (h - 20)
        marks.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" class="pk"><title>{e(d["date"])}: {d["views"]} views</title></circle>')
        anchor = "end" if x > w * 0.85 else "start"
        dx = -8 if anchor == "end" else 8
        labels.append(
            f'<text x="{x + dx:.1f}" y="{max(y - 10, 14):.1f}" text-anchor="{anchor}" class="pklbl">'
            f'{e(d["date"][5:])} · {d["views"]}</text>'
        )

    first, last = daily[0]["date"], daily[-1]["date"]
    return f"""<svg viewBox="0 0 {w} {h + 26}" class="chart" role="img" aria-label="Daily page views">
  <path d="{area}" class="area"/><polyline points="{line}" class="line"/>
  {''.join(marks)}{''.join(labels)}
  <text x="0" y="{h + 20}" class="ax">{e(first)}</text>
  <text x="{w}" y="{h + 20}" text-anchor="end" class="ax">{e(last)}</text>
</svg>"""


def spark(daily, w=260, h=40):
    vals = [d["views"] for d in daily][-90:]
    if not vals:
        return ""
    peak = max(vals) or 1
    step = w / max(len(vals) - 1, 1)
    pts = " ".join(f"{i * step:.1f},{h - (v / peak) * h:.1f}" for i, v in enumerate(vals))
    return f'<svg viewBox="0 0 {w} {h}" class="spark"><polyline points="{pts}"/></svg>'


def heatmap(cells):
    grid = {(c["day"], c["hour"]): c["views"] for c in cells}
    peak = max(grid.values(), default=1) or 1
    out = ['<div class="hm">']
    out.append('<div class="hm-row hm-head"><span class="hm-day"></span>')
    for hh in range(24):
        out.append(f'<span class="hm-h">{hh if hh % 6 == 0 else ""}</span>')
    out.append("</div>")
    for d in range(7):
        out.append(f'<div class="hm-row"><span class="hm-day">{DAYS[d]}</span>')
        for hh in range(24):
            v = grid.get((d, hh), 0)
            out.append(
                f'<span class="hm-c" style="--i:{v / peak:.3f}" title="{DAYS[d]} {hh:02d}:00 — {v} views"></span>'
            )
        out.append("</div>")
    out.append("</div>")
    return "".join(out)


def diagnostics(d):
    """Things worth saying out loud, inferred from the shape of the data."""
    notes = []
    cities = d.get("cities", [])
    total_users = d["totals"]["users"] or 1

    if cities:
        top = cities[0]
        if top["country"] != "United States" and top["users"] > total_users * 0.1:
            notes.append(
                f"<b>{e(top['city'])}, {e(top['country'])} is the single largest source of users "
                f"({top['users']:,}).</b> For a personal academic site that pattern usually means "
                f"automated traffic rather than readers, so treat totals as an upper bound."
            )
    dc = [c for c in cities if c["city"] in DATACENTRE]
    if dc:
        n = sum(c["users"] for c in dc)
        names = ", ".join(c["city"] for c in dc[:3])
        notes.append(
            f"<b>{n:,} users come from datacentre locations</b> ({e(names)}) — Google and AWS regions, "
            f"almost certainly crawlers rather than people."
        )

    pages = [p for p in d.get("top_pages", []) if p["views"] >= 20]
    if pages:
        best = max(pages, key=lambda p: p["avg_seconds"] / max(p["views"], 1))
        worst = min(pages, key=lambda p: p["avg_seconds"] / max(p["views"], 1))
        notes.append(
            f"<b>{e(best['title'])}</b> holds attention longest at "
            f"{best['avg_seconds'] / best['views']:.0f}s per view, against "
            f"{e(worst['title'])} at {worst['avg_seconds'] / max(worst['views'], 1):.0f}s."
        )

    nr = {x["kind"]: x for x in d.get("new_vs_returning", [])}
    if "returning" in nr and nr["returning"]["users"]:
        r = nr["returning"]
        notes.append(
            f"<b>{r['users']:,} returning visitors</b> account for {r['sessions']:,} sessions — "
            f"about {r['sessions'] / r['users']:.1f} visits each. You have regulars."
        )

    reads = {k: v for k, v in d.get("events", {}).items() if k.startswith("read_")}
    if not reads:
        notes.append(
            "<b>No blog read-depth events yet.</b> That tracking is newly installed; GA takes a day "
            "or two to surface new event names, and the pages need traffic."
        )
    return notes


def main():
    if not DATA.exists():
        raise SystemExit("No _data/analytics.json. Run bin/fetch_analytics.py first.")
    d = json.loads(DATA.read_text())
    t = d["totals"]
    pages = d.get("top_pages", [])
    eng = sorted(
        [p for p in pages if p["views"] >= 20],
        key=lambda p: -(p["avg_seconds"] / max(p["views"], 1)),
    )
    nr = {x["kind"]: x for x in d.get("new_vs_returning", [])}
    new_u = nr.get("new", {}).get("users", 0)
    ret_u = nr.get("returning", {}).get("users", 0)
    split = (ret_u / (new_u + ret_u) * 100) if (new_u + ret_u) else 0
    cities = d.get("cities", [])
    generated = d.get("generated_utc") or datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    notes_html = "".join(f"<li>{n}</li>" for n in diagnostics(d))

    OUT.write_text(TEMPLATE.format(
        window=e(d.get("window", "")),
        generated=e(generated),
        views=f"{t['views']:,}",
        users=f"{t['users']:,}",
        sessions=f"{t['sessions']:,}",
        spark=spark(d.get("daily", [])),
        chart=area_chart(d.get("daily", [])),
        notes=notes_html,
        pages=bar_rows(pages, "title", "views",
                       extra=lambda p: f"{p['avg_seconds'] / max(p['views'], 1):.0f}s", limit=10),
        engagement="\n".join(
            f'<div class="row"><span class="lbl">{e(p["title"])}</span>'
            f'<span class="track"><span class="fill alt" style="width:'
            f'{(p["avg_seconds"] / max(p["views"], 1)) / max((eng[0]["avg_seconds"] / max(eng[0]["views"], 1)), 1) * 100:.1f}%">'
            f'</span></span><span class="val">{p["avg_seconds"] / max(p["views"], 1):.0f}s</span>'
            f'<span class="note">{p["views"]:,} views</span></div>'
            for p in eng[:10]
        ),
        countries=bar_rows(d.get("countries", []), "country", "users", limit=8),
        cities="".join(
            f'<li><span>{e(c["city"])}<em>{e(c["country"])}</em></span><b>{c["users"]:,}</b></li>'
            for c in cities[:14]
        ),
        city_count=len(cities),
        new_users=f"{new_u:,}",
        ret_users=f"{ret_u:,}",
        ret_pct=f"{split:.0f}",
        ret_sessions=f"{nr.get('returning', {}).get('sessions', 0):,}",
        heat=heatmap(d.get("heatmap", [])),
    ))
    print(f"wrote {OUT.relative_to(pathlib.Path.cwd())}  ({OUT.stat().st_size // 1024} KB)")


TEMPLATE = """<title>Site Traffic</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=Public+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root{{
  --paper:#faf8f4; --card:#fffefb; --ink:#1a1a1e; --muted:#6f6a63; --rule:#e7e1d8;
  --accent:#1f6f68; --accent-soft:rgba(31,111,104,.12); --warn:#b65f33;
}}
@media (prefers-color-scheme:dark){{ :root:not([data-theme="light"]){{
  --paper:#141416; --card:#1b1b1f; --ink:#ece8e2; --muted:#9a948c; --rule:#2c2c31;
  --accent:#5bbdb1; --accent-soft:rgba(91,189,177,.16); --warn:#e09064;
}} }}
:root[data-theme="dark"]{{
  --paper:#141416; --card:#1b1b1f; --ink:#ece8e2; --muted:#9a948c; --rule:#2c2c31;
  --accent:#5bbdb1; --accent-soft:rgba(91,189,177,.16); --warn:#e09064;
}}
*{{box-sizing:border-box}}
body{{background:var(--paper);color:var(--ink);margin:0;font-family:"Public Sans",system-ui,sans-serif;
 line-height:1.5;padding:clamp(1.25rem,4vw,3rem) clamp(1rem,4vw,2rem) 5rem}}
.wrap{{max-width:62rem;margin:0 auto;display:flex;flex-direction:column;gap:2.5rem}}
h1{{font-family:Fraunces,Georgia,serif;font-weight:600;font-size:clamp(2rem,5vw,2.9rem);
 margin:0;letter-spacing:-.015em;line-height:1.05}}
h2{{font-family:Fraunces,Georgia,serif;font-weight:500;font-size:1.35rem;margin:0 0 .9rem}}
.sub{{color:var(--muted);margin:.3rem 0 0}}
.mono{{font-family:"IBM Plex Mono",ui-monospace,monospace;font-variant-numeric:tabular-nums}}
.stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(9rem,1fr));gap:1rem;align-items:end}}
.stat{{background:var(--card);border:1px solid var(--rule);border-radius:6px;padding:1rem 1.1rem}}
.stat .n{{font-family:"IBM Plex Mono",monospace;font-size:2rem;line-height:1;color:var(--accent)}}
.stat .k{{color:var(--muted);font-size:.8rem;text-transform:uppercase;letter-spacing:.08em;margin-top:.4rem}}
.spark{{width:100%;height:40px}} .spark polyline{{fill:none;stroke:var(--accent);stroke-width:1.5}}
.card{{background:var(--card);border:1px solid var(--rule);border-radius:6px;padding:1.2rem 1.3rem}}
.chart{{width:100%;height:auto}}
.area{{fill:var(--accent-soft)}} .line{{fill:none;stroke:var(--accent);stroke-width:1.6}}
.pk{{fill:var(--warn)}} .pklbl{{font-size:11px;fill:var(--muted);font-family:"IBM Plex Mono",monospace}}
.ax{{font-size:11px;fill:var(--muted);font-family:"IBM Plex Mono",monospace}}
.row{{display:grid;grid-template-columns:1fr 7rem 3.2rem 4rem;gap:.6rem;align-items:center;
 padding:.3rem 0;font-size:.9rem}}
.lbl{{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
.track{{background:var(--accent-soft);border-radius:3px;height:.65rem}}
.fill{{display:block;height:100%;background:var(--accent);border-radius:3px}}
.fill.alt{{background:var(--warn)}}
.val{{text-align:right;font-family:"IBM Plex Mono",monospace;font-size:.85rem}}
.note{{color:var(--muted);font-size:.78rem;text-align:right}}
.grid2{{display:grid;grid-template-columns:repeat(auto-fit,minmax(18rem,1fr));gap:1.5rem}}
ul.places{{list-style:none;padding:0;margin:0;font-size:.9rem}}
ul.places li{{display:flex;justify-content:space-between;gap:1rem;padding:.3rem 0;border-bottom:1px solid var(--rule)}}
ul.places li:last-child{{border-bottom:none}}
ul.places em{{color:var(--muted);font-style:normal;font-size:.78rem;margin-left:.45rem}}
ul.places b{{font-family:"IBM Plex Mono",monospace;font-weight:500}}
.diag{{list-style:none;padding:0;margin:0;display:flex;flex-direction:column;gap:.7rem}}
.diag li{{border-left:3px solid var(--warn);padding:.1rem 0 .1rem .8rem;font-size:.93rem}}
.split{{display:flex;height:1.8rem;border-radius:4px;overflow:hidden;margin-bottom:.6rem}}
.split span{{display:flex;align-items:center;justify-content:center;font-size:.8rem;color:var(--paper)}}
.hm{{display:flex;flex-direction:column;gap:3px;overflow-x:auto}}
.hm-row{{display:grid;grid-template-columns:2.4rem repeat(24,1fr);gap:3px;align-items:center}}
.hm-day{{font-size:.75rem;color:var(--muted)}}
.hm-h{{font-size:.65rem;color:var(--muted);text-align:center;font-family:"IBM Plex Mono",monospace}}
.hm-c{{aspect-ratio:1;border-radius:2px;background:color-mix(in srgb,var(--accent) calc(var(--i)*100%),var(--accent-soft))}}
footer{{color:var(--muted);font-size:.82rem;border-top:1px solid var(--rule);padding-top:1rem}}
</style>
<div class="wrap">
  <header>
    <h1>Site traffic</h1>
    <p class="sub">merylye.github.io · {window} · generated {generated}</p>
  </header>

  <section class="stats">
    <div class="stat"><div class="n">{views}</div><div class="k">page views</div></div>
    <div class="stat"><div class="n">{users}</div><div class="k">users</div></div>
    <div class="stat"><div class="n">{sessions}</div><div class="k">sessions</div></div>
    <div class="stat"><div class="k" style="margin:0 0 .4rem">last 90 days</div>{spark}</div>
  </section>

  <section class="card">
    <h2>Worth knowing</h2>
    <ul class="diag">{notes}</ul>
  </section>

  <section class="card">
    <h2>Daily views</h2>
    {chart}
  </section>

  <div class="grid2">
    <section class="card"><h2>Most visited</h2>{pages}</section>
    <section class="card"><h2>Holds attention</h2>{engagement}</section>
  </div>

  <div class="grid2">
    <section class="card"><h2>Countries</h2>{countries}</section>
    <section class="card">
      <h2>Cities</h2>
      <ul class="places">{cities}</ul>
      <p class="note" style="text-align:left;margin-top:.7rem">{city_count} cities in total</p>
    </section>
  </div>

  <section class="card">
    <h2>New vs returning</h2>
    <div class="split">
      <span style="width:{ret_pct}%;background:var(--accent)">{ret_pct}% returning</span>
      <span style="flex:1;background:var(--muted)">new</span>
    </div>
    <p class="sub" style="margin:0">{ret_users} returning visitors across {ret_sessions} sessions · {new_users} new</p>
  </section>

  <section class="card">
    <h2>When people visit</h2>
    <p class="sub" style="margin:0 0 .9rem">Page views by weekday and hour, in each visitor's local time.</p>
    {heat}
  </section>

  <footer>Aggregated from Google Analytics. Regenerate with <span class="mono">/traffic</span>.</footer>
</div>
"""

if __name__ == "__main__":
    main()
