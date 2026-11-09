#!/usr/bin/env python3
"""全体の展開に関わる粗い指標を計測する（審査の参考値）。

- paras: 段落数（空行または改行区切り）
- one_sent_ratio: 一文だけの段落の割合
- first_pivot_pct: 段落頭の転回語（でも/しかし/けれども/ところが/だが）が最初に出る位置（本文の何%地点か）
- meta: 進行のメタ言及（話を戻す/前置き/本題/話が逸れ/理由は二つ など）の回数

usage: flow_stats.py FILE...
"""
import re
import sys

PIVOT = re.compile(r"^(でも|しかし|けれども|けれど|ところが|だが|ただ、|ただし)")
META = re.compile(r"話を戻|前置き|本題|話が逸れ|話がそれ|脱線|理由は(二|三|ふた|みっ)つ|(二|三)つある|ここまでが")


def paras(text):
    lines = [l.strip() for l in text.splitlines()]
    return [l for l in lines if l and not l.startswith(("#", ">", "---"))]


def stats(text):
    ps = paras(text)
    total = sum(len(p) for p in ps) or 1
    one = sum(1 for p in ps if len([s for s in re.split(r"[。！？]", p) if s.strip()]) <= 1)
    pos, acc = None, 0
    for p in ps:
        if pos is None and PIVOT.match(p):
            pos = acc * 100 / total
        acc += len(p)
    return len(ps), one / max(len(ps), 1), pos, len(META.findall(text))


if __name__ == "__main__":
    print("file\tparas\tone_sent_ratio\tfirst_pivot_pct\tmeta")
    for f in sys.argv[1:]:
        n, r, p, m = stats(open(f, encoding="utf-8").read())
        print(f"{f}\t{n}\t{r:.2f}\t{'-' if p is None else f'{p:.0f}'}\t{m}")
