#!/usr/bin/env python3
"""Generate an animated contribution/streak SVG from data/contributions.json.

Run ``fetch_contributions.py`` first so this SVG and the contribution heatmap
always reflect the same GitHub data.
"""
import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(HERE, "..", "data", "contributions.json")
OUT = sys.argv[2] if len(sys.argv) > 2 else "streak.svg"

with open(DATA_PATH, encoding="utf-8") as source:
    data = json.load(source)

contribs = data["days"]
total = data["total_contributions"]
current = data["current_streak"]["length"]
longest = data["longest_streak"]["length"]

# ---- layout ----
CELL, GAP, RAD, LEFT, TOP = 13, 3, 2.5, 34, 24
COLORS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
GRAY = "#7d8590"
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

n = len(contribs)
NW = (n + 6) // 7
W = LEFT + NW * (CELL + GAP) + 6
H = TOP + 7 * (CELL + GAP) + 48
REVEAL, DUR = 3.6, 0.55
maxorder = (NW - 1) + 6 * 0.55

max_count = max(day["count"] for day in contribs) or 1

def level(count):
    if not count:
        return 0
    return min(4, max(1, (count * 4 + max_count - 1) // max_count))

rects, labels = [], []
start_date = datetime.date.fromisoformat(contribs[0]["date"])
last_month = None
for week in range(NW):
    date = start_date + datetime.timedelta(days=week * 7)
    if date.month != last_month:
        last_month = date.month
        labels.append(f'<text class="lbl" x="{LEFT + week * (CELL + GAP)}" y="{TOP - 8}">{MONTHS[date.month - 1]}</text>')
for name, row in [("Mon", 1), ("Wed", 3), ("Fri", 5)]:
    labels.append(f'<text class="lbl" x="2" y="{TOP + row * (CELL + GAP) + CELL - 2}">{name}</text>')

for index, contribution in enumerate(contribs):
    week, row = divmod(index, 7)
    intensity = level(contribution["count"])
    x = LEFT + week * (CELL + GAP)
    y = TOP + row * (CELL + GAP)
    delay = round((week + row * 0.55) / maxorder * REVEAL, 3)
    group = "c g" if intensity else "c e"
    rects.append(
        f'<rect class="{group}" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="{RAD}" '
        f'fill="{COLORS[intensity]}" style="animation-delay:{delay}s"><title>{contribution["date"]}: {contribution["count"]} contributions</title></rect>'
    )

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif">
<style>
  text.lbl {{ fill:{GRAY}; font-size:13px; font-weight:600; }}
  text.total {{ fill:#e6edf3; font-size:15px; font-weight:700; }}
  text.stat {{ fill:{GRAY}; font-size:13px; }} text.stat tspan {{ fill:#f2cc60; font-weight:700; }}
  .c {{ transform-box:fill-box; transform-origin:center; opacity:0; animation:pop {DUR}s ease-out both; }}
  .g {{ animation:pop {DUR}s ease-out both, flash {DUR + 0.15}s ease-out both; }}
  @keyframes pop {{ 0%{{opacity:0;transform:scale(.2)}} 60%{{opacity:1;transform:scale(1.1)}} 100%{{opacity:1;transform:scale(1)}} }}
  @keyframes flash {{ 0%{{filter:brightness(2.4)}} 45%{{filter:brightness(2.4)}} 100%{{filter:brightness(1)}} }}
  @media (prefers-reduced-motion: reduce) {{ .c {{ opacity:1 !important; animation:none !important; }} }}
</style>
<rect width="{W}" height="{H}" fill="none"/>
{''.join(labels)}
{''.join(rects)}
<text class="total" x="{LEFT}" y="{H - 26}">{total:,} contributions in the last year</text>
<text class="stat" x="{LEFT}" y="{H - 7}">current streak <tspan>{current} days</tspan> · longest streak <tspan>{longest} days</tspan></text>
</svg>'''

with open(OUT, "w", encoding="utf-8") as output:
    output.write(svg)
print(f"Wrote {OUT}: {n} days, {total:,} contributions, current streak {current}, longest streak {longest}")
