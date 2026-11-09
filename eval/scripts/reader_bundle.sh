#!/bin/bash
# usage: reader_bundle.sh <outdir> <task>...  — heldout/{before,v4}/{gpt,opus}_<task>.md を課題ごとにまとめ、課題内でシャッフルした束を作る
# 計測値や文体への言及は付けない（読み物としての評価用）。対応表は .map.txt
set -eu
OUT="$1"; shift; HERE="$(cd "$(dirname "$0")" && pwd)"; H="$HERE/../heldout"
mkdir -p "$OUT"; : > "$OUT/.map.txt"; : > "$OUT/judge_bundle.md"; : > "$OUT/prompts.md"
i=0
for t in "$@"; do
  T=$(echo "$t" | tr a-z A-Z)
  # 課題文は「課題Hn（…）」の行を残し、本文はそのまま渡す
  cat "$H/$t.md" >> "$OUT/prompts.md"; echo >> "$OUT/prompts.md"
  echo "# 課題$T の文章" >> "$OUT/judge_bundle.md"; echo >> "$OUT/judge_bundle.md"
  for f in $(for c in before v4; do for m in gpt opus; do echo "$H/$c/${m}_$t.md"; done; done | awk 'BEGIN{srand()}{print rand()"\t"$0}' | sort | cut -f2); do
    i=$((i+1)); id=$(printf "S%02d" $i)
    echo "$id $(basename "$(dirname "$f")")_$(basename "$f" .md)" >> "$OUT/.map.txt"
    { echo "## サンプル $id（課題$T）"; echo; cat "$f"; echo; echo; } >> "$OUT/judge_bundle.md"
  done
done
echo "bundled $i samples into $OUT"
