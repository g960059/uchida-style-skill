#!/bin/bash
# usage: judge_reader_gemini.sh <dir>  — Gemini 4 Argon (high) で <dir>/judge_bundle.md を読み物として採点し judge_gemini.md へ
set -u
R="$1"; HERE="$(cd "$(dirname "$0")" && pwd)"
PROMPT="$( { cat "$HERE/../reader_rubric.md"; echo; echo "## 課題文"; cat "$R/prompts.md"; echo; echo "# 評価対象"; cat "$R/judge_bundle.md"; echo; echo "ファイルの読み書きやツールは使わず、評価結果のMarkdownだけを出力してください。"; } )"
agy --model gemini-4-argon-high --print-timeout 1200s -p "$PROMPT" > "$R/judge_gemini.md" 2>"$R/.judge_gemini.log"
echo "gemini rc=$?"
