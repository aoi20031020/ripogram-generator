# 日本語リポグラムジェネレーター (Ripogram Generator)

OpenAI GPT-4 を使用して日本語のリポグラム（特定の文字を使わない文章）を生成する Python ライブラリです。

## 概要

**リポグラム（Lipogram）** とは、特定の文字を使わずに文章を書く言葉遊びの一種です。このプロジェクトでは、AI 技術を活用して日本語の文章から指定した文字を除いた自然な文章を自動生成します。

## 主な機能

- **日本語形態素解析**: fugashi ライブラリを使用した高精度な日本語トークン化
- **AI 文章変換**: OpenAI GPT-4 による自然な単語置換
- **コマンドライン対応**: 簡単に使える CLI インターフェース
- **Web アプリ**: Streamlit ベースの直感的な Web インターフェース
- **文脈考慮**: 文全体の意味を保持した高品質な変換
- **詳細出力**: 変換過程を確認できる verbose モード
- **設定可能**: 禁止文字やモデルの柔軟な設定

## インストール

1. リポジトリをクローンまたはダウンロード
2. 依存関係をインストール:

```bash
pip install -r requirements.txt
```

3. 環境変数を設定:

```bash
cp .env.example .env
# .envファイルを編集してOpenAI APIキーを追加
```

## 設定

`.env`ファイルに以下の変数を設定してください:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

## 使用方法

### 1. Web アプリケーション（推奨）

直感的な Web インターフェースを使用:

```bash
streamlit run streamlit_app.py
```

ブラウザで `http://localhost:8501` にアクセスして使用できます。

**Web アプリの特徴:**

- 使いやすい GUI
- リアルタイム変換
- 例文の自動入力
- 変換過程の詳細表示
- 結果のコピー機能
- 統計情報の表示

### 2. コマンドラインインターフェース

基本的な使用方法:

```bash
python -m ripogram.cli "さるも木から落ちる" --banned-chars "さ,い"
```

詳細出力付き:

```bash
python -m ripogram.cli "さるも木から落ちる" --banned-chars "さ,い" --verbose
```

### 3. Python API

```python
from ripogram.config import Config
from ripogram.core.rewriter import RipogramRewriter

# 設定を読み込み
config = Config()

# リライターを初期化
rewriter = RipogramRewriter(
    api_key=config.openai_api_key,
    model_name=config.model_name
)

# 文章を変換（文脈考慮版）
result = rewriter.rewrite_text_with_context(
    text="さるも木から落ちる",
    banned_chars=["さ", "い"],
    verbose=True
)

print(result)
```

## コマンドラインオプション

- `sentence`: 変換する日本語文章（必須）
- `--banned-chars, -b`: 禁止文字（カンマ区切り、必須）
- `--env-file, -e`: カスタム.env ファイルのパス
- `--model, -m`: 使用する OpenAI モデル（デフォルト: gpt-4.1-nano）
- `--verbose, -v`: 詳細出力を有効化

## 使用例

```bash
# 基本例
python -m ripogram.cli "犬も歩けば棒に当たる" --banned-chars "い,た"

# 異なるモデルを使用
python -m ripogram.cli "さるも木から落ちる" --banned-chars "さ,い" --model "gpt-4"

# 詳細出力
python -m ripogram.cli "つきよのよるにいちまいのてがみをかきました" --banned-chars "つ,よ,い,て" --verbose

# 複数文の処理
python -m ripogram.cli "猿も木から落ちる。石の上にも三年。" --banned-chars "い,さ"
```

## プロジェクト構造

```
ripogram/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── tokenizer.py      # fugashiを使用した日本語トークン化
│   ├── rewriter.py       # OpenAI GPT-4による単語置換
│   └── utils.py          # ユーティリティ関数
├── cli.py                # コマンドラインインターフェース
├── config.py             # 設定管理
├── streamlit_app.py      # Streamlit Webアプリケーション
├── test_ripogram.py      # テストファイル
├── requirements.txt      # 依存関係
├── .env.example          # 環境変数テンプレート
└── README.md
```

## 技術仕様

### 対応モデル

- gpt-4.1-nano（推奨・デフォルト）
- gpt-4
- gpt-4-turbo
- gpt-3.5-turbo

### 処理フロー

1. **形態素解析**: fugashi による日本語文章の分割
2. **禁止文字検出**: 表記と読みの両方で禁止文字をチェック
3. **文脈考慮変換**: 文全体の意味を保持した単語置換
4. **品質検証**: 変換結果の再検証と必要に応じた再変換

## 動作要件

- Python 3.7 以上
- OpenAI API キー
- requirements.txt に記載の依存関係

## ライセンス

このプロジェクトはオープンソースです。詳細はライセンスファイルを確認してください。

## 貢献

バグ報告や機能提案は、GitHub の Issues でお知らせください。プルリクエストも歓迎します。
