#!/bin/bash
# usage: gen_codex.sh <outdir> <mode: skill|naive|plain> <task.md>...
# GPT 6 astra (high) で課題を執筆し <outdir>/gpt_<task>.md に保存
set -u
OUT="$1"; MODE="$2"; shift 2
HERE="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$OUT"
for T in "$@"; do
  name=$(basename "$T" .md)
  (
    {
      case "$MODE" in
        skill) echo "以下は日本語の文体skill（SKILL.mdと参照ファイル一式）です。このskillに厳密に従って、後に示す課題の文章を書いてください。"; echo; "$HERE/bundle_skill.sh" ;;
        naive) echo "内田樹の文体で、後に示す課題の文章を書いてください。" ;;
        plain) echo "後に示す課題の文章を書いてください。" ;;
      esac
      echo; echo "===== 課題 ====="; cat "$T"; echo
      echo "出力は完成した本文（タイトルがあればタイトルを1行目に）のみ。前置き・解説・ファイル操作は不要です。どうしても注記したいことがあれば、本文の後に「----NOTE----」という行を置き、その後に書いてください（評価対象からは除外されます）。"
    } | codex exec -m gpt-6-astra -c model_reasoning_effort="high" --skip-git-repo-check --ephemeral -s read-only \
        -C "$OUT" -o "$OUT/gpt_${name}.md" - >"$OUT/.gpt_${name}.log" 2>&1
    rc=$?
    # 注記は本文から分離して保存
    if grep -q '^----NOTE----' "$OUT/gpt_${name}.md" 2>/dev/null; then
      sed -n '/^----NOTE----/,$p' "$OUT/gpt_${name}.md" > "$OUT/.gpt_${name}.note"
      sed -i '' '/^----NOTE----/,$d' "$OUT/gpt_${name}.md"
    fi
    echo "done $name rc=$rc"
  ) &
done
wait
