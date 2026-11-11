#!/usr/bin/env python3
"""任意のディレクトリ構成から、課題ごとにまとめて課題内でシャッフルした伏せ束を作る（読み物としての評価用）。

usage: [WRITERS=gpt,opus] bundle_generic.py <outdir> <base> <conds(カンマ区切り)> <prompts_dir> <task>...
  <base>/<cond>/{gpt,opus}_<task>.md を集める。対応表は <outdir>/.map.txt（名前は <cond>_<writer>_<task>）
"""
import os
import random
import sys
from pathlib import Path

out, base, conds, pdir, *tasks = sys.argv[1:]
out, base, pdir = Path(out), Path(base), Path(pdir)
out.mkdir(parents=True, exist_ok=True)
mp, body, prompts, i = [], [], [], 0
for t in tasks:
    prompts.append((pdir / f"{t}.md").read_text())
    files = [(c, m, base / c / f"{m}_{t}.md") for c in conds.split(",") for m in os.environ.get("WRITERS", "gpt,opus").split(",")]
    random.shuffle(files)
    body.append(f"# 課題{t.upper()} の文章\n")
    for c, m, f in files:
        i += 1
        sid = f"S{i:02d}"
        mp.append(f"{sid} {c}_{m}_{t}")
        body.append(f"## サンプル {sid}（課題{t.upper()}）\n\n{f.read_text().strip()}\n")
(out / ".map.txt").write_text("\n".join(mp) + "\n")
(out / "judge_bundle.md").write_text("\n".join(body))
(out / "prompts.md").write_text("\n".join(prompts))
print(f"bundled {i} samples into {out}")
