# 日本語リポグラム実験サマリー（2025-11 時点）

このドキュメントは、`data/dev_500.csv` を用いて実施した日本語リポグラム実験（sequential vs oneshot）の要約です。  
卒論・中間発表用の「結果の一枚もの」として使えるレベルを目標にしています。

---

## 1. 目的

- 日本語において、特定のかなを読みレベルで一切含まないリポグラム文を自動生成する。
- 同一の LLM（OpenAI GPT 系）を用いたときに、
  - 文全体を一度で言い換える **oneshot**（一発生成）
  - 文脈とトークン単位の書き換えを組み合わせる **sequential**（逐次生成）
  のどちらが **制約遵守（リポグラムとして正しいか）** と **書き換えの性質** の面で優れているかを比較する。

---

## 2. データセット

- 元コーパス: `data/jpn_sentences.csv`
  - Tatoeba 由来の日本語例文コーパス（`id, lang, text`）。
- 前処理 1: ベース文抽出 `scripts/generate_base_200.py`
  - 条件:
    - 文字数 20〜60
    - ひらがな or 漢字を含む（`[ぁ-ん一-龥]`）
  - 上記条件を満たす文からランダムに 200 文サンプル。
  - 出力: `data/base_200.csv`
    - `base_id, text, genre=tatoeba, source_id=tatoeba:<元ID>`
- 前処理 2: 制約付きパターン展開 `scripts/generate_dev_from_base.py`
  - 禁止セット（banned_chars）:
    - **easy**（単音禁止）: `"い"`, `"さ"`, `"ら"`
    - **medium**（行禁止）: `"あ,い,う,え,お"`, `"か,き,く,け,こ"`
  - 各ベース文に対し、上記セットごとに
    - banned 内のいずれかのかなが表記に含まれる場合のみ、その組を 1 行として採用。
    - 1 文あたり最大 3 セットまで（同一文の過度な増殖を防ぐ）。
  - 出力: `data/dev_500.csv`
    - 465 行（約 500 パターン）
    - 列: `id, text, banned_chars, constraint_type (easy/medium), genre=tatoeba, source_id`

---

## 3. 手法（モデル・生成方式）

- 実装: `ripogram/core/rewriter.py`（`RipogramRewriter`）
- モデル:
  - OpenAI Chat Completions API
  - 実験では `Config.DEFAULT_MODEL = "gpt-4.1-nano"` をベースに使用。
- 生成方式:
  1. **oneshot**（一発生成）
     - `rewrite_text_one_shot(text, banned_chars, ...)`
     - 文全体を 1 回のプロンプトで書き換え。
     - プロンプト内容:
       - 共通ルール `_common_lipogram_rules(banned_chars)`  
         - 禁止文字は読み（ひらがな）での使用が禁止  
         - 出力全文の読みから禁止かなを完全排除  
         - 「猫／ネコ科」のような読みまで含めた例示  
         - 意味保持・自然さ・句読点維持
       - 入力文と禁止かなを明示し、「説明無しで書き換え後の文のみ出力」を要求。
  2. **sequential**（逐次生成）
     - `rewrite_text_with_context(text, banned_chars, ...)`
     - 手順:
       1. `split_into_sentences` で文を分割（`。！？` 区切り）。
       2. 各文を形態素解析し、トークンごとに
          - 表記 or 読みに禁止かなを含むトークンを検出。
       3. 禁止トークンに対し、`rewrite_token_with_context` を用いて
          - 全文 / 現在の文 / 品詞などの文脈情報を与えたプロンプトで単語単位の言い換えを試行。
          - 失敗履歴に基づく再試行戦略（同義語→上位概念→意訳）を最大 10 回。
       4. 置き換えたトークンで文を再構成し、全文を再結合。
     - プロンプト内容:
       - oneshot と同じ `_common_lipogram_rules` を組み込みつつ、
         「変換後の単語の読みから禁止かなを完全排除」「出力は単語のみ」など単語レベルの制約を追加。

---

## 4. 評価指標

評価は `ripogram/metrics.py` と `scripts/evaluate_jp.py` によって自動計算。

- 制約遵守（主指標）
  - `check_constraint(output, banned_chars, mode="reading")`
  - 生成文をトークン化し、読み（カタカナ→ひらがな）を連結した文字列に禁止かなが含まれるかを判定。
  - 出力:
    - `constraint_violated`（True/False）
    - `constraint_count`（禁止かなの出現数）
    - `constraint_found`（見つかった禁止かなの集合）
- VRR（Vocabulary Replacement Rate）
  - `compute_vrr(original, output)`
  - 記号を除いたトークン列同士を比較し、置き換わったトークンの割合を算出。
  - トークン長が異なる場合は LCS を用いた近似。
- TTR（Type-Token Ratio）
  - `compute_ttr(output)`
  - 内容語トークンのユニーク表層数 / 総トークン数。
- n-gram 反復率
  - `ngram_repetition_rate(output, n=2/3)`
  - 出現回数 2 回目以降の n-gram の総数 / 全 n-gram 数。
- 実行時間
  - `measure_time(callable, ...)` により、1パターンあたりの生成時間を秒単位で記録。

---

## 5. 実験条件（evaluate_jp.py）

- コマンド例:

```bash
python scripts/evaluate_jp.py \
  --input data/dev_500.csv \
  --output results/results_500.csv \
  --methods sequential oneshot \
  --model gpt-4.1-nano \
  --verbose
```

- 各行（1 文 + 1 禁止セット）に対し、
  - `sequential` と `oneshot` の両方式で書き換えを行う。
  - 各方式ごとに、上記指標を計算し `results_500.csv` に出力。

---

## 6. 主な結果の要約

分析スクリプト: `scripts/analyze_results.py`  
（入力: `results/results_500.csv`）

### 6.1 成功率（制約遵守）

- 全体:
  - oneshot: 約 **12.5%**
  - sequential: 約 **91.6%**
- 制約タイプ別:
  - **easy（単音禁止）**
    - oneshot: 約 **27.7%**
    - sequential: 約 **99.0%**
  - **medium（行禁止）**
    - oneshot: 約 **1.5%**
    - sequential: 約 **86.3%**

→ 同じモデル・同じ禁止条件でも、逐次方式の方がリポグラムとして成功する確率が圧倒的に高い。  
特に medium（行禁止）条件で差が顕著。

### 6.2 ペアごとの勝ち負け（同一パターンでの比較）

- 各 `id` について sequential / oneshot の成功フラグを比較（計 465 ペア）。
  - `seq > one`: 368 ペア（**79.1%**）
  - `seq < one`: 0 ペア（**0%**）
  - `equal`（両方成功 or 両方失敗）: 97 ペア（20.9%）

→ 「oneshot だけが勝っているケース」はゼロであり、  
 ほとんどのパターンで sequential の方が制約遵守の観点で優位。

### 6.3 VRR / TTR（両方式とも成功したペア）

- 両方式とも `constraint_violated=False` のペア（58 件）について、
  - `vrr_diff = vrr_sequential - vrr_oneshot ≈ -0.33`
  - `ttr_diff = ttr_sequential - ttr_oneshot ≈ -0.012`
- 解釈:
  - VRR が負 → oneshot の方が単語置き換え率が高く、「より大きく言い換える」傾向。
  - TTR 差はほぼ 0 → 語彙多様性は両方式で大差ない。

→ 制約を満たしているケースに限れば、
  - sequential は **元文に近い形をより保ちつつ**（VRR 低め）  
  - 語彙の多様さは oneshot とほぼ同程度  
という特徴を持つ。

### 6.4 統計的検定（対応あり t 検定）

- success（0/1）:
  - t ≈ 41.96, p ≈ 5.0e-160（df=464）
  - → sequential と oneshot の成功率差は統計的に極めて有意。
- VRR（両方成功ペア）:
  - t ≈ -13.74, p ≈ 9.8e-20（df=57）
  - → oneshot の方が VRR が有意に高い（より大きく書き換える）。
- TTR（両方成功ペア）:
  - p ≈ 0.166
  - → 語彙多様性の差は有意とは言えない。

---

## 7. 可視化（plot_results.py）

スクリプト: `scripts/plot_results.py`  
（入力: `results/results_500.csv`、出力: `results/*.png`）

- `success_by_method.png`
  - oneshot vs sequential の全体成功率のバーグラフ。
- `success_by_constraint_type.png`
  - constraint_type（easy / medium）× method の成功率バー。
- `vrr_box_both_success.png`
  - 両方式とも成功したペアにおける VRR の箱ひげ図。
- `vrr_ttr_scatter_both_success.png`
  - 両方式とも成功したペアにおける VRR vs TTR の散布図（色で method を区別）。

---

## 8. 暫定的な結論と今後の課題

- 暫定結論:
  - **制約遵守の観点では sequential が圧倒的に優位**（特に medium 条件）。
  - **oneshot はより大きな書き換え（高 VRR）を行うが、そのぶん制約違反が頻発**。
  - **語彙多様性（TTR）は両方式で大きな差は見られない**。
- 今後の課題:
  - 文のジャンル（proverb / wiki / aozora など）を増やした上で、genre 別の差を分析。
  - 制約タイプ（単音 vs 複数音 vs 行制約）の水準を増やし、難易度との関係を詳細化。
  - 成功例・失敗例を抽出し、意味保持・自然さに関する人手評価を追加。
  - sequential 方式に対する「oneshot クリーンアップ」のようなハイブリッド戦略の評価。

このサマリーをベースに、卒論本文では各セクションを肉付けし、具体的な例文や図を挿入していく想定です。

