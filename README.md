# uchida-style skill

日本語の文章からAI臭さを消し、展開に起伏を足し、最後まで読ませるための Agent Skill。手本として、内田樹の随筆・ブログ・講演録の文体（常識の問いを立て直し、平易な語りで思いがけない場所に着地する文体）を使う。短文（〜3000字）と長文（4000〜8000字の長編エッセイ・講演録・新書の章）の両方で検証している。

文体の**特徴を規則として記述したもの**で、本人へのなりすましや、発言・引用の捏造はしない設計になっている。

## 使い方

**明示的に呼び出したときだけ動く**設定にしてある（依頼の文面から自動で起動することはない）。

- Claude Code：`/uchida-style` に続けて依頼を書く。例：`/uchida-style ふるさと納税について800字のコラム`。このリポジトリで開けば `.claude/skills/uchida-style` から読み込まれる。他のプロジェクトで使うなら `skills/uchida-style` を `~/.claude/skills/` にコピーする。自動起動は SKILL.md の `disable-model-invocation: true` で止めている。
- Codex：`$uchida-style` に続けて依頼を書く。`.agents/skills/uchida-style` から読み込まれる。自動起動は `agents/openai.yaml` の `policy.allow_implicit_invocation: false` で止めている。
- それ以外：`skills/uchida-style/SKILL.md` と `references/*.md` をプロンプトに入れる（`eval/scripts/bundle_skill.sh` で1ファイルにまとめられる）。

依頼が添えられていないときは、何を書くかを尋ねてから始める。

## 構成

```
skills/uchida-style/
  SKILL.md                     呼び出し方、出力ルール、手順、密度の上限（disable-model-invocation: true）
  agents/openai.yaml           Codex 用の設定（自動起動しない）
  references/
    thinking-patterns.md       思考のエンジン（問いのずらし方）と補助線の系統
    disclosure.md              全体の情報開示・展開（開示の型・入口・常識の扱い・着地のメニュー）
    structure.md               構成と段落のリズム、講演録・短文の型
    voice-and-diction.md       語尾・語彙・表記・温度
    anti-patterns.md           AI臭・カリカチュア・内容上の失敗
    long-form.md               3000字を超える長文の指針（全体の地図、楽章ごとの新しい場面、二度目のひねり、中だるみ対策、小見出し）
    examples.md                オリジナルの模作（実在の文章ではない）
eval/                          評価の仕組みと全ラウンドの結果
```

## 評価のしかた

- 書き手：Claude Opus 5.5（xhigh）と GPT 6 astra（high、codex 経由）
- 審査：Gemini 4 Argon（high、agy 経由）と Claude Opus 5.5（xhigh）。書き手と条件を伏せ、順番をシャッフルした束で採点した。
- 採点項目：思考の型、語り口、構成、自然さ、中身、AI臭のなさ、**対比文型の節度**（「〜ではない、〜である」型の頻度と配置）、**情報開示・展開の設計**、総合、本人誤認率。対比文型と展開は機械計測（`eval/scripts/contrast_stats.py`、`flow_stats.py`）も添えて審査員に渡した。
- 改善案の採否は、審査員の提案をそのまま入れず、理由を付けて判断した（`eval/decisions.md`）。
- 過剰適合の確認のため、改善ループで使った4課題とは別のテーマ（heldout）で前後比較した。

詳細な結果は `eval/RESULTS.md` を参照。
