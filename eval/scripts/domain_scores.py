#!/usr/bin/env python3
"""補助線の分類（domain_rubric.md）の結果を、審査員 × 条件 × 書き手で集計する。

usage: domain_scores.py <dir>
- classic: 手本の書き手に典型的な領域（思想・哲学／武道・稽古／古典・伝統芸能／作品／昔の職業・商習慣）の割合
- kinds: 出てきた領域の種類数
"""
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

CLASSIC = {"思想・哲学", "武道・稽古", "古典・伝統芸能", "映画・文学・漫画などの作品", "昔の職業・商習慣"}

d = Path(sys.argv[1])
idmap = dict(l.split() for l in (d / ".map.txt").read_text().splitlines() if l.strip())
for jf in sorted(d.glob("judge_*.md")):
    if jf.name == "judge_bundle.md":
        continue
    blocks = re.findall(r"```json\s*(\{.*?\})\s*```", jf.read_text(), re.S)
    if not blocks:
        print(f"{jf.stem}: (no json)")
        continue
    data = json.loads(blocks[-1])
    agg = defaultdict(lambda: {"lines": [], "persona": []})
    for sid, v in data.items():
        cond, writer, task = idmap[sid].split("_")
        agg[(cond, writer)]["lines"] += v.get("lines", [])
        if v.get("persona_use") is not None:
            agg[(cond, writer)]["persona"].append(v["persona_use"])
    print(f"== {jf.stem}")
    for (cond, writer), a in sorted(agg.items()):
        ls = a["lines"]
        doms = Counter(l.get("domain", "?") for l in ls)
        n = len(ls) or 1
        classic = sum(c for k, c in doms.items() if k in CLASSIC) / n
        conc = sum(l.get("concreteness", 0) for l in ls) / n
        rev = sum(bool(l.get("reversal")) for l in ls) / n
        risk = sum(bool(l.get("fact_risk")) for l in ls)
        persona = Counter(a["persona"])
        print(f"{cond}\t{writer}\t補助線{len(ls)}本\t種類{len(doms)}\t典型領域{classic:.0%}\t具体性{conc:.1f}\t反転{rev:.0%}\t事実の危うさ{risk}\t得意領域{dict(persona)}")
        print("\t\t" + "、".join(f"{k}{c}" for k, c in doms.most_common()))
