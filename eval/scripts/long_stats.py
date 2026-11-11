#!/usr/bin/env python3
"""長文の機械計測：字数、段落数、段落長のばらつき、見出し数、対比文型、手癖語、言い回しの重複率。

usage: long_stats.py FILE...
- dup5: 同じ文字5-gram（句読点・空白を除く）が2回以上出る割合。長文で同じ言い回しを繰り返すほど高い。
"""
import re
import statistics
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import contrast_stats as cs  # noqa: E402

HABIT = ["ずいぶん", "厄介", "妙な", "借り", "清算", "帳簿", "勘定", "たぶん", "なのである", "のである"]

print("file\tchars\tparas\tpara_cv\theadings\tcontrast/1000\tdup5\t" + "\t".join(HABIT))
for f in sys.argv[1:]:
    t = Path(f).read_text()
    lines = [l.strip() for l in t.splitlines() if l.strip()]
    heads = [l for l in lines if l.startswith("#") or (len(l) <= 25 and "。" not in l)]
    paras = [l for l in lines if l not in heads]
    lens = [len(p) for p in paras]
    cv = statistics.pstdev(lens) / statistics.mean(lens) if lens else 0
    chars, _, _, _, total, per = cs.stats(t)
    s = re.sub(r"[\s、。「」『』（）！？・…―ー]", "", t)
    grams = Counter(s[i:i + 5] for i in range(len(s) - 4))
    dup = sum(c for c in grams.values() if c > 1) / max(sum(grams.values()), 1)
    habit = "\t".join(str(t.count(w)) for w in HABIT)
    print(f"{f}\t{chars}\t{len(paras)}\t{cv:.2f}\t{len(heads)}\t{per:.2f}\t{dup:.3f}\t{habit}")
