#!/usr/bin/env python3
"""「〜ではない、〜である」型（否定→肯定の対比）の頻度を計測する。

usage: contrast_stats.py FILE...   → TSV（ファイル名, 字数, 各カウント, 1000字あたり）
"""
import re
import sys

NEG_END = re.compile(r"(では|じゃ)(ない|ありません|なかった)(のである|のだ|んです|のです|んだ|んですね)?[。]?$")
POS_END = re.compile(r"(である|のである|なのである|のだ|なのだ|だ|です|のです|なんです|んです)$")
# 文中の「AではなくB」「AじゃなくてB」「AでなくB」（「だけでなく」は除く）
INLINE = re.compile(r"(?<!だけ)(?<!のみ)(では|じゃ|で)なく(て)?[、，]")
# 「BよりもC」「Bのことじゃない」型は審査員の目視に任せる（機械では過検出が多い）
# 譲歩・部分否定（対比ではないので別集計）
CONCESSIVE = re.compile(r"(わけ|とは限ら|というわけ)(では|じゃ)ない")


def sentences(text):
    text = re.sub(r"\s+", "", text)
    return [s for s in re.split(r"(?<=[。！？])", text) if s]


def stats(text):
    ss = [s.rstrip("。！？") for s in sentences(text)]
    chars = len(re.sub(r"\s", "", text))
    pair = 0  # 「〜ではない。〜である。」の2文対
    for a, b in zip(ss, ss[1:]):
        if NEG_END.search(a) and not CONCESSIVE.search(a) and POS_END.search(b):
            pair += 1
    inline = len(INLINE.findall(text))
    concessive = len(CONCESSIVE.findall(text))
    total = pair + inline
    return chars, pair, inline, concessive, total, total * 1000 / max(chars, 1)


if __name__ == "__main__":
    print("file\tchars\tpair(ではない。〜である)\tinline(ではなく)\tconcessive(わけではない)\ttotal\tper1000")
    for f in sys.argv[1:]:
        c, p, i, k, t, r = stats(open(f, encoding="utf-8").read())
        print(f"{f}\t{c}\t{p}\t{i}\t{k}\t{t}\t{r:.2f}")
