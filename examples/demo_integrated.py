"""
Demonstration script for the integrated Japanese/English lipogram generator.
統合日本語・英語リポグラム生成システムのデモンストレーション
"""

import sys
import os
import time

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def print_header(title: str):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n🔹 {title}")
    print("-" * 40)


def demo_japanese():
    """Demonstrate Japanese lipogram generation."""
    print_header("日本語リポグラム生成デモ")

    try:
        from ripogram.core.rewriter import RipogramRewriter
        from ripogram.config import Config

        print("✅ 日本語モジュールの読み込み成功")

        # Check API key
        try:
            config = Config()
            if not config.openai_api_key:
                print("❌ OpenAI APIキーが設定されていません")
                print("💡 .envファイルにOPENAI_API_KEYを設定してください")
                return
            print("✅ OpenAI APIキー設定確認済み")
        except Exception as e:
            print(f"❌ 設定エラー: {e}")
            return

        # Demo examples
        examples = [
            {
                "text": "吾輩は猫である。",
                "banned": ["い"],
                "description": "夏目漱石「吾輩は猫である」- 'い'を避ける"
            },
            {
                "text": "今日は良い天気です。",
                "banned": ["い", "て"],
                "description": "日常会話 - 'い'と'て'を避ける"
            }
        ]

        for i, example in enumerate(examples, 1):
            print_section(f"例 {i}: {example['description']}")
            print(f"入力文: {example['text']}")
            print(f"禁止文字: {', '.join(example['banned'])}")

            print("🤖 GPTで変換中...")
            print("💡 実際の変換にはAPIキーが必要です")
            print("📝 デモモード: 変換処理をスキップします")

    except ImportError as e:
        print(f"❌ 日本語モジュールの読み込みエラー: {e}")
        print("💡 必要な依存関係をインストールしてください: pip install openai")


def demo_english():
    """Demonstrate English lipogram generation."""
    print_header("English Lipogram Generation Demo")

    try:
        from ripogram.core.english_bert_rewriter import EnglishBertRewriter
        from ripogram.core.english_tokenizer import EnglishTokenizer

        print("✅ English modules loaded successfully")

        # Test tokenizer first
        print_section("WordNet Synonym Test")
        tokenizer = EnglishTokenizer()

        test_words = ["happy", "quick", "cat", "run"]
        for word in test_words:
            synonyms = tokenizer.get_synonyms(word)
            print(f"'{word}' synonyms: {', '.join(synonyms[:5])}...")

        print_section("BERT Model Loading Test")
        print("🔄 Loading BERT model (this may take a moment)...")

        try:
            rewriter = EnglishBertRewriter("bert-base-uncased")
            print("✅ BERT model loaded successfully")

            # Demo examples
            examples = [
                {
                    "text": "The cat sat on the mat.",
                    "banned": ["e"],
                    "description": "Classic 'no E' lipogram"
                },
                {
                    "text": "Hello world!",
                    "banned": ["l", "o"],
                    "description": "Avoiding 'l' and 'o'"
                }
            ]

            for i, example in enumerate(examples, 1):
                print_section(f"Example {i}: {example['description']}")
                print(f"Input: {example['text']}")
                print(f"Banned chars: {', '.join(example['banned'])}")

                try:
                    print("🔄 Generating lipogram...")
                    start_time = time.time()

                    result = rewriter.rewrite_text(
                        example["text"],
                        example["banned"],
                        similarity_threshold=0.4,
                        verbose=False
                    )

                    processing_time = time.time() - start_time

                    print(f"✨ Result: {result}")
                    print(f"⏱️  Processing time: {processing_time:.2f}s")

                    # Verify result
                    banned_found = []
                    for char in example["banned"]:
                        if char.lower() in result.lower():
                            banned_found.append(char)

                    if banned_found:
                        print(
                            f"⚠️  Warning: Still contains: {', '.join(banned_found)}")
                    else:
                        print("✅ Success: No banned characters found")

                except Exception as e:
                    print(f"❌ Generation error: {e}")

        except Exception as e:
            print(f"❌ BERT model loading error: {e}")
            print("💡 Make sure PyTorch and transformers are installed")
            print("💡 First run may take time to download models")

    except ImportError as e:
        print(f"❌ English module import error: {e}")
        print("💡 Install required dependencies:")
        print("   pip install torch transformers nltk spacy scikit-learn")
        print("   python -m spacy download en_core_web_sm")


def demo_integrated_features():
    """Demonstrate integrated system features."""
    print_header("統合システム機能デモ")

    print_section("Available Interfaces")
    interfaces = [
        ("CLI (Japanese)", "python -m ripogram.cli"),
        ("CLI (English)", "python -m ripogram.english_cli --interactive"),
        ("Web App (Japanese)", "streamlit run streamlit_app.py"),
        ("Web App (English)", "streamlit run english_streamlit_app.py"),
        ("Integrated Web App", "streamlit run integrated_streamlit_app.py"),
    ]

    for name, command in interfaces:
        print(f"📱 {name}")
        print(f"   Command: {command}")

    print_section("Test Suites")
    test_files = [
        ("Japanese Tests", "python test_ripogram.py"),
        ("English Tests", "python test_english_ripogram.py"),
        ("Integration Demo", "python demo_integrated.py")
    ]

    for name, command in test_files:
        print(f"🧪 {name}")
        print(f"   Command: {command}")

    print_section("Research Documentation")
    docs = [
        ("Research Slides", "中間発表リポグラム.pptx.pdf"),
        ("Japanese README", "README.md"),
        ("English README", "README_ENGLISH.md"),
        ("Requirements", "requirements.txt")
    ]

    for name, file in docs:
        if os.path.exists(file):
            print(f"📄 {name}: ✅ {file}")
        else:
            print(f"📄 {name}: ❌ {file} (not found)")


def main():
    """Main demonstration function."""
    print("🌐 統合リポグラム生成システム デモンストレーション")
    print("   Integrated Lipogram Generation System Demonstration")
    print(f"   Author: 橋本 葵 (Aoi Hashimoto) - 22G1104002B")
    print(f"   Institution: 中央大学国際情報学部")

    # Check Python version
    python_version = sys.version_info
    print(
        f"🐍 Python Version: {python_version.major}.{python_version.minor}.{python_version.micro}")

    if python_version < (3, 8):
        print("⚠️  Warning: Python 3.8+ recommended")

    # Demo menu
    while True:
        print_header("デモメニュー / Demo Menu")
        options = [
            ("1", "日本語リポグラム生成デモ (Japanese Demo)"),
            ("2", "English Lipogram Generation Demo"),
            ("3", "統合システム機能紹介 (Integrated Features)"),
            ("4", "システム要件確認 (System Requirements)"),
            ("q", "終了 (Quit)")
        ]

        for key, desc in options:
            print(f"  {key}. {desc}")

        choice = input("\n選択してください (Enter your choice): ").strip().lower()

        if choice == "1":
            demo_japanese()
        elif choice == "2":
            demo_english()
        elif choice == "3":
            demo_integrated_features()
        elif choice == "4":
            check_system_requirements()
        elif choice in ["q", "quit", "exit"]:
            print("\n👋 デモを終了します。ありがとうございました！")
            print("   Thank you for trying the demo!")
            break
        else:
            print("❌ 無効な選択です。もう一度お試しください。")
            print("   Invalid choice. Please try again.")


def check_system_requirements():
    """Check system requirements and dependencies."""
    print_header("システム要件確認")

    print_section("Python Packages")
    required_packages = [
        ("openai", "OpenAI API client"),
        ("fugashi", "Japanese morphological analyzer"),
        ("python-dotenv", "Environment variable loader"),
        ("streamlit", "Web application framework"),
        ("torch", "PyTorch for BERT models"),
        ("transformers", "Hugging Face transformers"),
        ("nltk", "Natural Language Toolkit"),
        ("spacy", "Advanced NLP processing"),
        ("scikit-learn", "Machine learning utilities")
    ]

    for package, description in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}: {description}")
        except ImportError:
            print(f"❌ {package}: {description} (not installed)")

    print_section("NLTK Data")
    try:
        import nltk
        nltk_data = ["punkt", "averaged_perceptron_tagger", "wordnet"]
        for data in nltk_data:
            try:
                nltk.data.find(f"tokenizers/{data}")
                print(f"✅ NLTK {data}")
            except LookupError:
                try:
                    nltk.data.find(f"taggers/{data}")
                    print(f"✅ NLTK {data}")
                except LookupError:
                    try:
                        nltk.data.find(f"corpora/{data}")
                        print(f"✅ NLTK {data}")
                    except LookupError:
                        print(f"❌ NLTK {data} (not downloaded)")
    except ImportError:
        print("❌ NLTK not available")

    print_section("spaCy Models")
    try:
        import spacy
        try:
            spacy.load("en_core_web_sm")
            print("✅ spaCy English model (en_core_web_sm)")
        except OSError:
            print(
                "❌ spaCy English model (en_core_web_sm) - run: python -m spacy download en_core_web_sm")
    except ImportError:
        print("❌ spaCy not available")

    print_section("Configuration Files")
    config_files = [
        (".env", "Environment variables"),
        (".env.example", "Environment template"),
        ("requirements.txt", "Python dependencies")
    ]

    for file, desc in config_files:
        if os.path.exists(file):
            print(f"✅ {file}: {desc}")
        else:
            print(f"❌ {file}: {desc} (not found)")


if __name__ == "__main__":
    main()
