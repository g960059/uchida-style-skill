#!/usr/bin/env python3
"""skill 適用前後の比較ページ（最終報告）を作る。

- H1〜H8：heldout の skill 適用前（before）と適用後（v4）
- O1〜O4：内田樹の原文と同じテーマで書いた適用前（before）と適用後（v4.1）。原文は本文を載せず、リンクと点数だけ
- 点数：読み物としての評価（reader/）と、文体の再現度の評価（heldout/judge*）

usage: build_compare_html.py <template.html> <out.html> <R3dir>
R3dir には原文を含む3者比較の束（.map.txt と judge_*.md）がある。原文の本文はページに入れない。
"""
import html
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVAL = HERE.parent
sys.path.insert(0, str(HERE))
import contrast_stats as cs  # noqa: E402
import flow_stats as fs  # noqa: E402

AXES = ["interest", "readability", "immersion", "exhilaration", "insight", "dynamics",
        "voice", "no_ai_smell", "memorability", "overall", "read_more"]

TOPICS = {
    "h1": ("SNSでの一斉批判", "エッセイ", "heldout"),
    "h2": ("ふるさと納税", "書き換え", "heldout"),
    "h3": ("なぜ勉強しなければならないのか", "高校での講演録", "heldout"),
    "h4": ("AIに仕事を奪われる不安", "新聞の質問回答", "heldout"),
    "h5": ("推し活", "雑誌コラム", "heldout"),
    "h6": ("公園の「禁止」看板", "地域情報誌への寄稿", "heldout"),
    "h7": ("キャッシュレス", "ブログ", "fresh"),
    "h8": ("ご祝儀の相場", "新聞コラム", "fresh"),
    "o1": ("笑いと人文知", "新聞コラム", "orig"),
    "o2": ("生成AIと書くこと", "受験生向け雑誌への寄稿", "orig"),
    "o3": ("「〇〇ファースト」と投票", "週刊誌のコラム", "orig"),
    "o4": ("農業と教育", "新聞コラム（連載の一回）", "orig"),
}
ORIG = {  # 原文（本文は載せない）
    "o1": ("笑いと人文知", "https://blog.tatsuru.com/2026/10/16_0831.html"),
    "o2": ("さよならAI", "https://blog.tatsuru.com/2026/11/09_1126.html"),
    "o3": ("小さな問題から大きな問題へ", "https://blog.tatsuru.com/2026/10/03_1717.html"),
    "o4": ("農業を基幹産業に", "https://blog.tatsuru.com/2026/10/16_0822.html"),
}
STYLE_BUNDLE = {("before", t): b for b, ts in {"judgeA": "h1 h2 h3", "judgeB": "h4 h5 h6", "judgeE": "h7 h8"}.items() for t in ts.split()}
STYLE_BUNDLE.update({("v4", t): b for b, ts in {"judgeC": "h1 h2 h3", "judgeD": "h4 h5 h6", "judgeE": "h7 h8"}.items() for t in ts.split()})


def load_json(path):
    blocks = re.findall(r"```json\s*(\{.*?\})\s*```", Path(path).read_text(), re.S)
    return json.loads(blocks[-1]) if blocks else {}


def read_map(d):
    return dict(l.split() for l in (Path(d) / ".map.txt").read_text().splitlines() if l.strip())


def reader_scores(dirs):
    """{name: {judge: {axis: v, "rank": n, "of": m}}} と、集計用の平均を返す。"""
    per = defaultdict(dict)
    agg = defaultdict(lambda: defaultdict(list))
    wins = defaultdict(lambda: [0, 0])
    for d in map(Path, dirs):
        idmap = read_map(d)
        for judge in ("opus", "gemini"):
            data = load_json(d / f"judge_{judge}.md")
            for sid, sc in data.get("scores", {}).items():
                name = idmap[sid]
                per[name][judge] = {k: sc.get(k) for k in AXES}
                cond, writer, _ = name.split("_")
                for k in AXES:
                    if sc.get(k) is not None:
                        agg[(d.name, judge, writer, cond)][k].append(float(sc[k]))
            for order in data.get("rankings", {}).values():
                for i, sid in enumerate(order):
                    per[idmap[sid]].setdefault(judge, {}).update({"rank": i + 1, "of": len(order)})
                pos = {idmap[s]: i for i, s in enumerate(order)}
                for writer in ("gpt", "opus"):
                    b = [n for n in pos if n.startswith(f"before_{writer}_")]
                    a = [n for n in pos if n.startswith(f"v4_{writer}_") or n.startswith(f"after_{writer}_")]
                    if a and b:
                        wins[(d.name, judge, writer, "after>before")][0] += pos[a[0]] < pos[b[0]]
                        wins[(d.name, judge, writer, "after>before")][1] += 1
                    o = [n for n in pos if n.startswith("orig_")]
                    if a and o:
                        wins[(d.name, judge, writer, "after>orig")][0] += pos[a[0]] < pos[o[0]]
                        wins[(d.name, judge, writer, "after>orig")][1] += 1
                    if b and o:
                        wins[(d.name, judge, writer, "before>orig")][0] += pos[b[0]] < pos[o[0]]
                        wins[(d.name, judge, writer, "before>orig")][1] += 1
    return per, agg, wins


def style_scores():
    out = {}
    for b in ("judgeA", "judgeB", "judgeC", "judgeD", "judgeE"):
        d = EVAL / "heldout" / b
        idmap = read_map(d)
        for judge in ("opus", "gemini"):
            data = load_json(d / f"judge_{judge}.md")
            for sid, name in idmap.items():
                out.setdefault((b, name), {})[judge] = data.get(sid, {}).get("overall")
    return out


def mark_contrast(text):
    """contrast_stats.py と同じ判定で、対比文型の箇所を <mark> で囲んだ段落HTMLのリストを返す。"""
    paras = [p.strip() for p in text.strip().splitlines() if p.strip()]
    sents = []
    for i, p in enumerate(paras):
        for s in re.split(r"(?<=[。！？])", p):
            if s:
                sents.append([i, s, False])
    for a, b in zip(sents, sents[1:]):
        sa, sb = a[1].rstrip("。！？"), b[1].rstrip("。！？")
        if cs.NEG_END.search(sa) and not cs.CONCESSIVE.search(sa) and cs.POS_END.search(sb):
            a[2] = b[2] = True
    out = [[] for _ in paras]
    for i, s, hit in sents:
        esc = html.escape(s)
        esc = cs.INLINE.sub(lambda m: f'<mark class="inline">{m.group(0)}</mark>', esc)
        out[i].append(f'<mark class="pair">{esc}</mark>' if hit else esc)
    return ["".join(x) for x in out]


def piece(path, reader, style=None):
    text = Path(path).read_text()
    lines = [l for l in text.strip().splitlines() if l.strip()]
    title = None
    if lines and len(lines[0]) <= 30 and "。" not in lines[0]:
        title, text = lines[0].strip(), "\n".join(lines[1:])
    chars, _, _, _, total, per = cs.stats(text)
    npar, one, _, _ = fs.stats(text)
    return {
        "title": title, "paras": mark_contrast(text), "chars": chars,
        "contrast": total, "per1000": round(per, 2), "paras_n": npar, "one_sent": round(one, 2),
        "reader": reader, "style": style,
    }


def summarize(agg, group):
    out = {}
    for (dname, judge, writer, cond), d in agg.items():
        if dname not in group:
            continue
        key = f"{judge}|{writer}|{'after' if cond in ('v4', 'after') else cond}"
        for k, v in d.items():
            out.setdefault(key, defaultdict(list))[k] += v
    return {k: {a: round(sum(v) / len(v), 2) for a, v in d.items()} for k, d in out.items()}


def main(tpl, out, r3):
    per, agg, wins = reader_scores([EVAL / "reader" / "R1", EVAL / "reader" / "R2", r3])
    style = style_scores()
    topics = []
    for t, (name, genre, group) in TOPICS.items():
        if group == "orig":
            prompt = (EVAL / "orig" / f"{t}.md").read_text()
            base, after = EVAL / "orig", "after"
        else:
            prompt = (EVAL / "heldout" / f"{t}.md").read_text()
            base, after = EVAL / "heldout", "v4"
        original = prompt.split("---")[1].strip() if "---" in prompt else None
        plines = prompt.strip().splitlines()
        item = {
            "id": t, "name": name, "genre": genre, "group": group,
            "prompt": plines[0] if original else plines[-1],
            "original": original, "pieces": {},
        }
        for m in ("gpt", "opus"):
            item["pieces"][m] = {}
            for cond, label in (("before", "before"), (after, "after")):
                sty = None
                if group != "orig":
                    sty = style.get((STYLE_BUNDLE[(cond, t)], f"{cond}_{m}_{t}"))
                item["pieces"][m][label] = piece(base / cond / f"{m}_{t}.md", per.get(f"{cond}_{m}_{t}", {}), sty)
        if group == "orig":
            title, url = ORIG[t]
            item["orig"] = {"title": title, "url": url, "reader": per.get(f"orig_uchida_{t}", {})}
        topics.append(item)
    data = {
        "topics": topics,
        "summary": {
            "heldout": summarize(agg, {"R1", "R2"}),
            "orig": summarize(agg, {Path(r3).name}),
        },
        "wins": {"|".join(k): v for k, v in wins.items()},
    }
    js = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    Path(out).write_text(Path(tpl).read_text().replace("__DATA__", js))
    print(f"wrote {out}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
