#!/bin/bash
# usage: judge_gemini.sh <rounddir> [課題文ファイル]（省略時は prompts/t*.md）  — Gemini 4 Argon (high) で judge_bundle.md を採点し judge_gemini.md へ
set -u
R="$1"; HERE="$(cd "$(dirname "$0")" && pwd)"; PF="${2:-}"
PROMPT="$( { cat "$HERE/../rubric.md"; echo; echo "## 課題文"; if [ -n "$PF" ]; then cat "$PF"; else cat "$HERE"/../prompts/t*.md; fi; echo; echo "# 評価対象サンプル"; cat "$R/judge_bundle.md"; echo; echo "ファイルの読み書きやツールは使わず、評価結果のMarkdownだけを出力してください。"; } )"
agy --model gemini-4-argon-high --print-timeout 900s -p "$PROMPT" > "$R/judge_gemini.md" 2>"$R/.judge_gemini.log"
echo "gemini rc=$?"
