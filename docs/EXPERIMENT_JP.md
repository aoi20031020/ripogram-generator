# 日本語リポグラム実験ガイド（発表用）

このドキュメントは、現実装で実行可能な日本語リポグラム実験の手順・指標・運用の要点を、発表向けに簡潔にまとめたものです。

## 1. 目的とスコープ
- 目的: LLM逐次置換（文脈活用）と LLM一発生成（ベースライン）を比較し、制約遵守・VRR・多様性・実行時間で性能差を検証する。
- スコープ: 日本語のみ（英語は参考実装あり）。JPハイブリッド（BERT+WordNet+LLM）は未実装のため比較対象外。

## 2. 仮説（今回検証可能な範囲）
- H1: 逐次LLMは一発LLMより制約遵守率・VRRで優れる。
- H3: 難易度が高い制約でも、逐次LLMの性能低下が小さい。
- H2（任意）: 可読性・面白さの主観評価で逐次LLMが優れる（A/Bで実施可能）。

## 3. 比較条件（日本語）
- sequential（逐次）: `RipogramRewriter.rewrite_text_with_context`（文脈利用・トークン逐次）
- oneshot（一発）: `RipogramRewriter.rewrite_text_one_shot`（全文を一回で言い換え）

## 4. 評価指標（非加重）
- 制約遵守（読みベース）
  - 形態素の読み（ひらがな）を連結し、禁止音の含有を検査（句読点除外）。
  - 関数: `check_constraint(text, banned, mode="reading")`
- VRR（Vocabulary Replacement Rate: 置換率）
  - 定義: 置換トークン数 / 総トークン数。長さ不一致は LCS 近似で算出。
  - 関数: `compute_vrr(original, rewritten)`
- 多様性
  - TTR（Type-Token Ratio）: `compute_ttr(text)`
  - n-gram 自己重複率: `ngram_repetition_rate(text, n=2/3)`
- 実行時間
  - `measure_time(callable, ...)` で前処理を含む生成時間を取得。
- 実装: `ripogram/metrics.py`（詳細は `docs/METRICS.md`）

## 5. データセット（用意していただく想定）
- 形式: CSV または JSONL。
  - 必須: `text` または `sentence`
  - 任意: `banned_chars`（例: `い,さ`）、`genre`, `difficulty` など
- 行禁止（例: あ行）は事前に展開して `banned_chars` に記述（`あ,い,う,え,お`）。

### CSV 例
```csv
text,banned_chars,genre,difficulty
"猿も木から落ちる。石の上にも三年。","い,さ",proverb,low
"国境の長いトンネルを抜けると雪国であった。","あ,い,う,え,お",literature,high
```

### JSONL 例
```jsonl
{"text": "猿も木から落ちる。", "banned_chars": "い,さ", "genre": "proverb", "difficulty": "low"}
{"text": "今日は良い天気だ。", "banned_chars": "あ,い,う,え,お"}
```

## 6. 実行手順
1) セットアップ
- `pip install -r requirements.txt`
- `.env` に `OPENAI_API_KEY` を設定（`ripogram/config.py` 参照）
- スモークテスト: `python examples/demo_metrics.py`

2) 一括評価（バッチ）
- スクリプト: `scripts/evaluate_jp.py`
- 例（両条件を評価）:
```bash
python scripts/evaluate_jp.py \
  --input data/dev.csv \
  --output results.csv \
  --model gpt-4.1-nano \
  --methods sequential oneshot \
  --verbose
```
- `banned_chars` 列が無い場合は `--banned "あ,い,う,え,お"` を付与
- スモールラン: `--limit 10`

3) 単発検証（CLI）
```bash
# 逐次
python -m ripogram.cli "猿も木から落ちる。" -b "い,さ" -v
# 一発
python -m ripogram.cli "猿も木から落ちる。" -b "い,さ" -M oneshot -v
```

## 7. 出力（results.csv の主要列）
- `id`: 入力の行番号
- `method`: `sequential` / `oneshot`
- `text`: 入力文
- `banned_chars`: 禁止文字（カンマ区切り）
- `output`: 生成文
- `constraint_violated`: 違反有無（True/False）
- `constraint_found`: 検出された禁止音（例: `い,さ`）
- `constraint_count`: 禁止音の総出現回数
- `vrr`: 置換率（0–1）
- `ttr`: Type-Token Ratio（0–1）
- `bigram_rep`, `trigram_rep`: n-gram 自己重複率
- `time_sec`: 生成処理時間（秒）
- （任意メタ情報）`genre`, `difficulty` などはそのままパススルー

## 8. 集計・解析の指針
- 集計: 条件×難易度×ジャンルで平均・分散を算出（遵守率[%]、VRR、時間[秒]）。
- 統計: 条件（2）×難易度（3）×ジャンル（4）で反復測定ANOVA / 混合効果モデル、事後比較はHolm。
- 主観評価（任意）:
  - デザイン: 同一入力で `sequential` vs `oneshot` の A/B 提示（順序カウンタバランス）
  - 評価: 「どちらが読みやすい/面白い？」7段階Likert＋二者選択
  - 解析: Bradley–Terry/Luce モデルで勝率推定＋有意差検定

## 9. 再現性と運用
- 乱数性: LLM温度は既定0.5。必要に応じて固定化（温度を下げる・再試行禁止など）。
- 記録: 入力、`banned_chars`、モデル名、実行日時、スクリプトのコミットを結果と一緒に保存。
- ログ: 例外・APIエラーは標準出力/標準エラーに記録。再実行での差分に注意。

## 10. リスクと対策
- 読みの誤検出: UniDicベースの読みを使用（`katakana_to_hiragana`で正規化）。必要に応じて例外表を導入。
- 助詞群の極端制約: 意味保持の低下が顕著な場合は主観評価で補完。厳格運用時は温度を下げる。
- トークン数大幅変動: VRRはLCS近似で頑健化。極端な圧縮/膨張は別途事例検討。

## 11. 付録：コマンド一覧
- 指標デモ: `python examples/demo_metrics.py`
- 一括評価: `python scripts/evaluate_jp.py --input data/dev.csv --output results.csv --model gpt-4.1-nano`
- CLI（逐次）: `python -m ripogram.cli "…" -b "い,さ" -v`
- CLI（一発）: `python -m ripogram.cli "…" -b "い,さ" -M oneshot -v`

