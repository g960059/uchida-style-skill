#!/bin/bash
# skill一式を1つのテキストに連結して標準出力へ
D="$(cd "$(dirname "$0")/../../skills/uchida-style" && pwd)"
for f in "$D/SKILL.md" "$D"/references/*.md; do
  echo "===== FILE: ${f#$D/} ====="
  cat "$f"
  echo
done
