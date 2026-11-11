#!/bin/bash
# usage: [RUBRIC=reader_rubric_long.md] judge_reader_gpt.sh <dir>  — GPT 6 astra (high) で <dir>/judge_bundle.md を採点し judge_gpt.md へ
set -u
R="$1"; HERE="$(cd "$(dirname "$0")" && pwd)"
{ cat "$HERE/../${RUBRIC:-reader_rubric.md}"; echo; echo "## 課題文"; cat "$R/prompts.md"; echo; echo "# 評価対象"; cat "$R/judge_bundle.md"; echo
  echo "ファイルの読み書きやツールは使わず、評価結果のMarkdownだけを出力してください。"; } \
  | codex exec -m gpt-6-astra -c model_reasoning_effort="high" --skip-git-repo-check --ephemeral -s read-only \
      -C "$R" -o "$R/judge_gpt.md" - > "$R/.judge_gpt.log" 2>&1
echo "gpt rc=$?"
