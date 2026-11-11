#!/usr/bin/env python3
"""読み物としての評価（reader/*/judge_*.md）を集計する。

- 審査員 × 書き手 × 条件（before / v4）ごとの各項目の平均
- 課題内の順位から、同じ書き手の v4 が before より上位に置かれた割合（勝率）

usage: reader_scores.py <dir>...
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

KEYS = ["interest", "readability", "immersion", "exhilaration", "insight", "dynamics",
        "voice", "no_ai_smell", "memorability", "sustain", "architecture", "repetition",
        "overall", "read_more", "dropoff"]

avg = defaultdict(lambda: defaultdict(list))   # (judge, writer, cond) -> key -> [..]
wins = defaultdict(lambda: [0, 0])             # (judge, writer) -> [v4が上, 対戦数]
ranks = defaultdict(list)                      # (judge, writer, cond) -> [順位]

for d in map(Path, sys.argv[1:]):
    idmap = {}
    for line in (d / ".map.txt").read_text().splitlines():
        if line.strip():
            sid, name = line.split()
            cond, writer, task = name.split("_")
            idmap[sid] = (writer, cond, task)
    for jf in sorted(d.glob("judge_*.md")):
        judge = jf.stem.replace("judge_", "")
        blocks = re.findall(r"```json\s*(\{.*?\})\s*```", jf.read_text(), re.S)
        if not blocks:
            print(f"{d.name}\t{judge}\t(no json)", file=sys.stderr)
            continue
        data = json.loads(blocks[-1])
        for sid, sc in data.get("scores", {}).items():
            writer, cond, _ = idmap[sid]
            for k in KEYS:
                if k in sc:
                    avg[(judge, writer, cond)][k].append(float(sc[k]))
        for order in data.get("rankings", {}).values():
            pos = {sid: i + 1 for i, sid in enumerate(order)}
            for sid, r in pos.items():
                writer, cond, _ = idmap[sid]
                ranks[(judge, writer, cond)].append(r)
            for writer in ("gpt", "opus"):
                b = [s for s in pos if idmap[s][:2] == (writer, "before")]
                a = [s for s in pos if idmap[s][:2] in ((writer, "v4"), (writer, "after"))]
                if a and b:
                    wins[(judge, writer)][0] += pos[a[0]] < pos[b[0]]
                    wins[(judge, writer)][1] += 1

print("judge\twriter\tcond\tn\t" + "\t".join(KEYS) + "\tmean_rank")
for (judge, writer, cond), d in sorted(avg.items()):
    n = len(d["overall"])
    vals = "\t".join(f"{sum(d[k]) / len(d[k]):.1f}" if d[k] else "-" for k in KEYS)
    r = ranks[(judge, writer, cond)]
    print(f"{judge}\t{writer}\t{cond}\t{n}\t{vals}\t{sum(r) / len(r):.2f}" if r else f"{judge}\t{writer}\t{cond}\t{n}\t{vals}\t-")
print()
print("judge\twriter\tv4がbeforeより上位\t")
for (judge, writer), (w, n) in sorted(wins.items()):
    print(f"{judge}\t{writer}\t{w}/{n}")
