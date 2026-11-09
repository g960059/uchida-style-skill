#!/usr/bin/env python3
"""judge_*.md 末尾のJSONスコアを .map.txt と突き合わせ、書き手×審査員ごとの平均を出す。

usage: scores.py <rounddir>...
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

KEYS = ["thinking", "voice", "structure", "naturalness", "substance", "no_ai_smell",
        "contrast", "disclosure", "overall", "mistaken_for_real"]



def table_scores(text):
    """JSONがない古い審査結果用：「### サンプル Sxx」以下の表から各項目の点を拾う。"""
    data = {}
    parts = re.split(r"^###\s*(?:サンプル\s*)?(S\d+).*$", text, flags=re.M)
    for sid, body in zip(parts[1::2], parts[2::2]):
        sc = {}
        for k in KEYS:
            m = re.search(r"\|[^|\n]*" + k + r"[^|\n]*\|\s*\**\s*(\d+(?:\.\d+)?)", body)
            if m:
                sc[k] = float(m.group(1))
        if sc:
            data[sid] = sc
    return data


for rd in map(Path, sys.argv[1:]):
    idmap = dict(l.split() for l in (rd / ".map.txt").read_text().splitlines() if l.strip())
    for judge in sorted(rd.glob("judge_*.md")):
        if judge.name == "judge_bundle.md":
            continue
        text = judge.read_text()
        blocks = re.findall(r"```json\s*(\{.*?\})\s*```", text, re.S)
        data = json.loads(blocks[-1]) if blocks else table_scores(text)
        if not data:
            print(f"{rd.name}\t{judge.stem}\t(no scores)")
            continue
        agg = defaultdict(lambda: defaultdict(list))
        for sid, sc in data.items():
            writer = idmap.get(sid, "?").removesuffix(".md").rsplit("_", 1)[0]  # gpt / before_gpt など
            for k in KEYS:
                if k in sc:
                    agg[writer][k].append(float(sc[k]))
        for writer, d in sorted(agg.items()):
            vals = "\t".join(f"{k}={sum(d[k])/len(d[k]):.1f}" for k in KEYS if d[k])
            print(f"{rd.name}\t{judge.stem.replace('judge_','')}\t{writer}\t{vals}")
