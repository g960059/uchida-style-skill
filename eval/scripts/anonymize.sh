#!/bin/bash
# usage: anonymize.sh <rounddir>  — <rounddir>/{gpt,opus}_*.md をシャッフルして judge_bundle.md を作る（対応表は .map.txt）
# 各サンプル末尾に「〜ではない、〜である」型の機械計測値を添える
set -eu
R="$1"; HERE="$(cd "$(dirname "$0")" && pwd)"
: > "$R/.map.txt"; : > "$R/judge_bundle.md"
i=0
for f in $(ls "$R"/gpt_*.md "$R"/opus_*.md | awk 'BEGIN{srand()}{print rand()"\t"$0}' | sort | cut -f2); do
  i=$((i+1)); id=$(printf "S%02d" $i)
  task=$(basename "$f" .md | sed 's/^[a-z]*_//')
  echo "$id $(basename "$f")" >> "$R/.map.txt"
  st=$(python3 "$HERE/contrast_stats.py" "$f" | tail -1 | awk -F'\t' '{printf "字数%s／2文対比(〜ではない。〜である)%s回／文中対比(〜ではなく〜)%s回／部分否定(わけではない)%s回／対比計%s回（1000字あたり%s）", $2,$3,$4,$5,$6,$7}')
  fl=$(python3 "$HERE/flow_stats.py" "$f" | tail -1 | awk -F'\t' '{printf "段落数%s／一文段落率%s／段落頭の最初の転回語の位置%s%%地点／進行のメタ言及%s回", $2,$3,$4,$5}')
  { echo "## サンプル $id（課題 $task）"; echo; cat "$f"; echo; echo "> 機械計測（対比）: $st"; echo ">"; echo "> 機械計測（展開）: $fl"; echo; } >> "$R/judge_bundle.md"
done
echo "bundled $i samples"
