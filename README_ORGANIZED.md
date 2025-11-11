# 統合リポグラム生成システム

## プロジェクト概要

このプロジェクトは、日本語と英語の両方に対応したリポグラム（特定の文字を使わない文章）生成システムです。

- **日本語版**: OpenAI GPT-4を使用したLLMベースのアプローチ
- **英語版**: BERT + WordNetを使用した意味的類似性ベースのアプローチ

## 📁 プロジェクト構造

```
ripogram/
├── 📱 apps/                          # Webアプリケーション
│   ├── streamlit_app.py              # 日本語版Streamlitアプリ
│   ├── english_streamlit_app.py      # 英語版Streamlitアプリ
│   └── integrated_streamlit_app.py   # 統合版Streamlitアプリ
│
├── 🧪 tests/                         # テストファイル
│   ├── test_ripogram.py              # 日本語版テスト
│   └── test_english_ripogram.py      # 英語版テスト
│
├── 📚 docs/                          # ドキュメント
│   ├── README_ENGLISH.md             # 英語版ドキュメント
│   └── 中間発表リポグラム.pptx.pdf    # 研究発表資料
│
├── 🎯 examples/                      # 例文・デモ
│   ├── demo_integrated.py            # 統合デモスクリプト
│   ├── pdf_viewer.py                 # PDF表示ツール
│   └── ripogram_gen_ipynb.ipynb      # Jupyter Notebook例
│
├── 🔧 ripogram/                      # メインパッケージ
│   ├── __init__.py
│   ├── cli.py                        # 日本語版CLI
│   ├── english_cli.py                # 英語版CLI
│   ├── config.py                     # 設定管理
│   └── core/                         # コアモジュール
│       ├── __init__.py
│       ├── utils.py                  # 共通ユーティリティ
│       ├── tokenizer.py              # 日本語トークナイザー
│       ├── rewriter.py               # 日本語リライター
│       ├── english_tokenizer.py      # 英語トークナイザー
│       └── english_bert_rewriter.py  # 英語BERTリライター
│
├── ⚙️ 設定ファイル
│   ├── .env.example                  # 環境変数テンプレート
│   ├── requirements.txt              # Python依存関係
│   ├── .gitignore                    # Git除外設定
│   └── README.md                     # メインドキュメント
```

## 🚀 クイックスタート

### 1. 環境設定

```bash
# 依存関係のインストール
pip install -r requirements.txt

# 英語処理用の追加設定
python -m spacy download en_core_web_sm

# 環境変数の設定
cp .env.example .env
# .envファイルにOpenAI APIキーを設定
```

### 2. 使用方法

#### Webアプリケーション

```bash
# 日本語版
streamlit run apps/streamlit_app.py

# 英語版
streamlit run apps/english_streamlit_app.py

# 統合版（推奨）
streamlit run apps/integrated_streamlit_app.py
```

#### コマンドライン

```bash
# 日本語版
python -m ripogram.cli

# 一発生成（ベースライン）モードの例
python -m ripogram.cli "猿も木から落ちる。" -b "い,さ" -M oneshot -v

# 英語版
python -m ripogram.english_cli --interactive
```

#### デモ実行

```bash
# 統合デモ
python examples/demo_integrated.py

# 指標デモ（VRR/制約/多様性）
python examples/demo_metrics.py

# 一括評価（CSV/JSONL → CSV）
python scripts/evaluate_jp.py --input data/dev.csv --output results.csv --model gpt-4.1-nano --verbose
```

## 🔧 技術仕様

### 日本語版（LLMベース）
- **エンジン**: OpenAI GPT-4
- **手法**: プロンプトベースの文脈理解
- **特徴**: 自然な日本語表現の生成

### 英語版（BERT + WordNetベース）
- **エンジン**: BERT + WordNet
- **手法**: 意味的類似性による単語置換
- **特徴**: 高精度な意味保持

## 📊 評価指標

- **制約満足度**: 禁止文字の除去率
- **意味保持度**: 元文との意味的類似性
- **自然性**: 生成文の流暢さ
- **処理速度**: 単語/秒での処理性能

## 🧪 テスト実行

```bash
# 日本語版テスト
python tests/test_ripogram.py

# 英語版テスト
python tests/test_english_ripogram.py

# 統合デモ
python examples/demo_integrated.py
```

## 📚 ドキュメント

- [英語版詳細ドキュメント](docs/README_ENGLISH.md)
- [研究発表資料](docs/中間発表リポグラム.pptx.pdf)
- [評価指標と使い方（METRICS）](docs/METRICS.md)
- [実験ガイド（発表用）](docs/EXPERIMENT_JP.md)

## 🎯 使用例

### 日本語例
```
入力: 吾輩は猫である。
禁止文字: い
出力: 吾輩は猫である。（「い」を含まない表現に変換）
```

### 英語例
```
Input: The cat sat on the mat.
Banned: e
Output: That cat sat on that mat.
```

## 🔄 開発・貢献

1. リポジトリをフォーク
2. 機能ブランチを作成
3. テストを追加・実行
4. プルリクエストを送信

## 📄 ライセンス

このプロジェクトは中央大学国際情報学部での学術研究の一環です。

## 👤 作成者

- **橋本 葵**
- **所属**: 中央大学国際情報学部
- **研究分野**: 制約付きテキスト生成

## 🔗 関連リンク

- [研究発表資料](docs/中間発表リポグラム.pptx.pdf)
- [英語版ドキュメント](docs/README_ENGLISH.md)
- [GitHubリポジトリ](https://github.com/aoi20031020/ripogram-generator)
