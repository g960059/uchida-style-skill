#!/bin/bash
# usage: [CONDS="before after"] heldout_bundle.sh <outdir> <task>...   例: CONDS="after v4" heldout_bundle.sh heldout/judgeC h1 h2 h3
# heldout/<cond>/{gpt,opus}_<task>.md をシャッフルして <outdir>/judge_bundle.md を作る（対応表は .map.txt）
set -eu
OUT="$1"; shift; HERE="$(cd "$(dirname "$0")" && pwd)"; H="$HERE/../heldout"
mkdir -p "$OUT"; : > "$OUT/.map.txt"; : > "$OUT/judge_bundle.md"; : > "$OUT/prompts.md"
files=()
for t in "$@"; do
  cat "$H/$t.md" >> "$OUT/prompts.md"; echo >> "$OUT/prompts.md"
  for c in ${CONDS:-before after}; do for m in gpt opus; do files+=("$H/$c/${m}_$t.md"); done; done
done
i=0
for f in $(printf '%s\n' "${files[@]}" | awk 'BEGIN{srand()}{print rand()"\t"$0}' | sort | cut -f2); do
  i=$((i+1)); id=$(printf "S%02d" $i)
  cond=$(basename "$(dirname "$f")"); base=$(basename "$f" .md); task=${base#*_}
  echo "$id ${cond}_${base}" >> "$OUT/.map.txt"
  st=$(python3 "$HERE/contrast_stats.py" "$f" | tail -1 | awk -F'\t' '{printf "字数%s／2文対比%s回／文中対比%s回／部分否定%s回／対比計%s回（1000字あたり%s）", $2,$3,$4,$5,$6,$7}')
  fl=$(python3 "$HERE/flow_stats.py" "$f" | tail -1 | awk -F'\t' '{printf "段落数%s／一文段落率%s／段落頭の最初の転回語の位置%s%%地点／進行のメタ言及%s回", $2,$3,$4,$5}')
  { echo "## サンプル $id（課題 $task）"; echo; cat "$f"; echo; echo "> 機械計測（対比）: $st"; echo ">"; echo "> 機械計測（展開）: $fl"; echo; } >> "$OUT/judge_bundle.md"
done
echo "bundled $i samples into $OUT"
