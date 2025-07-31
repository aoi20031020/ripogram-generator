"""
Integrated Streamlit Web Application for Lipogram Generation
日本語・英語リポグラム生成のための統合Webアプリケーション
"""

import streamlit as st
import sys
import os
import time
import traceback
import base64
from pathlib import Path
from typing import List

# Add the current directory to Python path for imports
sys.path.insert(0, '.')

try:
    # Japanese version imports
    from ripogram.core.rewriter import RipogramRewriter
    from ripogram.config import Config

    # English version imports
    from ripogram.core.english_bert_rewriter import EnglishBertRewriter
    from ripogram.core.english_tokenizer import EnglishTokenizer

    IMPORTS_AVAILABLE = True
except ImportError as e:
    IMPORTS_AVAILABLE = False
    IMPORT_ERROR = str(e)


# Page configuration
st.set_page_config(
    page_title="統合リポグラムジェネレーター",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)


def initialize_session_state():
    """Initialize session state variables."""
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'Japanese'
    if 'japanese_rewriter' not in st.session_state:
        st.session_state.japanese_rewriter = None
    if 'english_rewriter' not in st.session_state:
        st.session_state.english_rewriter = None
    if 'english_model_loaded' not in st.session_state:
        st.session_state.english_model_loaded = False
    if 'history' not in st.session_state:
        st.session_state.history = []
    if 'show_pdf_slideshow' not in st.session_state:
        st.session_state.show_pdf_slideshow = False


def parse_banned_chars(banned_chars_str: str) -> List[str]:
    """Parse banned characters string into list."""
    if not banned_chars_str.strip():
        return []
    # Support both comma and space separation
    if ',' in banned_chars_str:
        return [char.strip() for char in banned_chars_str.split(",")]
    else:
        return banned_chars_str.split()


def load_english_model(model_name: str):
    """Load English BERT model with caching."""
    if st.session_state.english_rewriter is None or not st.session_state.english_model_loaded:
        with st.spinner(f"Loading BERT model: {model_name}..."):
            try:
                st.session_state.english_rewriter = EnglishBertRewriter(
                    model_name)
                st.session_state.english_model_loaded = True
                st.success("✅ BERT model loaded successfully!")
                return True
            except Exception as e:
                st.error(f"❌ Error loading BERT model: {e}")
                return False
    return True


def verify_lipogram(text: str, banned_chars: List[str]) -> tuple:
    """
    Verify if text is a valid lipogram.

    Returns:
        tuple: (is_valid, banned_chars_found)
    """
    banned_found = []
    for char in banned_chars:
        if char.lower() in text.lower():
            banned_found.append(char)

    return len(banned_found) == 0, banned_found


def display_token_analysis(text: str, banned_chars: List[str], language: str):
    """Display token analysis in an expandable section."""
    with st.expander("🔍 Token Analysis", expanded=False):
        if language == 'English':
            tokenizer = EnglishTokenizer()
            tokens = tokenizer.tokenize(text)
        else:
            # For Japanese, we'll use a simple character-based analysis
            tokens = [{'surface': char} for char in text if char.strip()]

        st.write(f"**Total tokens:** {len(tokens)}")

        # Create columns for better layout
        col1, col2 = st.columns(2)

        with col1:
            st.write("**Valid tokens:**")
            valid_tokens = []
            for token in tokens:
                surface = token['surface']
                if not any(char.lower() in surface.lower() for char in banned_chars):
                    valid_tokens.append(surface)

            if valid_tokens:
                st.write(", ".join(valid_tokens[:20]))  # Show first 20
                if len(valid_tokens) > 20:
                    st.write(f"... and {len(valid_tokens) - 20} more")
            else:
                st.write("None")

        with col2:
            st.write("**Tokens with banned characters:**")
            invalid_tokens = []
            for token in tokens:
                surface = token['surface']
                if any(char.lower() in surface.lower() for char in banned_chars):
                    invalid_tokens.append(surface)

            if invalid_tokens:
                st.write(", ".join(invalid_tokens[:20]))  # Show first 20
                if len(invalid_tokens) > 20:
                    st.write(f"... and {len(invalid_tokens) - 20} more")
            else:
                st.write("None")


def show_pdf_slideshow():
    """Display PDF as a slideshow with navigation."""
    st.title("🎓 研究発表スライドショー")
    st.markdown("**中央大学国際情報学部４年 | 22G1104002B 橋本 葵**")

    # Initialize session state for slide navigation
    if 'current_slide' not in st.session_state:
        st.session_state.current_slide = 1

    total_slides = 16  # Total number of slides in the PDF

    # Navigation controls
    col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])

    with col1:
        if st.button("⏮️ 最初", help="最初のスライドに移動"):
            st.session_state.current_slide = 1
            st.rerun()

    with col2:
        if st.button("◀️ 前", help="前のスライドに移動"):
            if st.session_state.current_slide > 1:
                st.session_state.current_slide -= 1
                st.rerun()

    with col3:
        st.markdown(
            f"**スライド: {st.session_state.current_slide} / {total_slides}**")

    with col4:
        if st.button("▶️ 次", help="次のスライドに移動"):
            if st.session_state.current_slide < total_slides:
                st.session_state.current_slide += 1
                st.rerun()

    with col5:
        if st.button("⏭️ 最後", help="最後のスライドに移動"):
            st.session_state.current_slide = total_slides
            st.rerun()

    # Display PDF
    pdf_path = Path("docs/中間発表リポグラム.pdf")

    if pdf_path.exists():
        try:
            with open(pdf_path, "rb") as f:
                pdf_data = f.read()

            pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')

            # Display PDF
            pdf_display = f"""
            <div style="width: 100%; max-width: 900px; margin: 0 auto;">
                <div style="position: relative; width: 100%; padding-bottom: 70.7%; border: 1px solid #ddd; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);">
                    <iframe 
                        src="data:application/pdf;base64,{pdf_base64}#page={st.session_state.current_slide}&toolbar=1&navpanes=0&scrollbar=0&view=Fit" 
                        style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: none;"
                        type="application/pdf">
                        <p>PDFを表示できません。ブラウザがPDF表示をサポートしていない可能性があります。</p>
                    </iframe>
                </div>
            </div>
            """

            st.markdown(pdf_display, unsafe_allow_html=True)

            # Close slideshow button
            if st.button("❌ スライドショーを閉じる", type="secondary"):
                st.session_state.show_pdf_slideshow = False
                st.rerun()

        except Exception as e:
            st.error(f"❌ PDFの読み込みに失敗しました: {str(e)}")
    else:
        st.error("❌ PDFファイルが見つかりません: 中間発表リポグラム.pdf")


def japanese_page():
    """Japanese lipogram generation page."""
    st.title("📝 日本語リポグラムジェネレーター")
    st.markdown("""
    **リポグラム（Lipogram）** とは、特定の文字を使わずに文章を書く言葉遊びです。
    このページでは、AI（GPT-4）を使って日本語の文章から指定した文字を除いた自然な文章を生成します。
    """)

    # Settings in sidebar
    with st.sidebar:
        st.header("⚙️ 日本語設定")

        # Model selection
        model_options = [
            "gpt-4.1-nano",
            "gpt-4o-mini",
            "gpt-4",
            "gpt-4-turbo",
            "gpt-3.5-turbo"
        ]
        selected_model = st.selectbox(
            "使用モデル",
            model_options,
            index=0,
            help="使用するOpenAI GPTモデルを選択してください"
        )

        # Verbose mode
        verbose_mode = st.checkbox(
            "詳細表示モード",
            value=False,
            help="変換過程の詳細を表示します"
        )

        # API key status
        st.markdown("---")
        st.markdown("**API設定状況:**")
        try:
            config = Config()
            if config.openai_api_key:
                st.success("✅ OpenAI APIキーが設定されています")
            else:
                st.error("❌ OpenAI APIキーが設定されていません")
        except Exception as e:
            st.error(f"❌ 設定エラー: {str(e)}")

    # Main input area
    st.header("📝 入力")

    # Initialize session state for examples
    if 'jp_example_text' not in st.session_state:
        st.session_state.jp_example_text = ""
    if 'jp_example_banned' not in st.session_state:
        st.session_state.jp_example_banned = ""

    # Example buttons
    st.markdown("**使用例:** 以下のボタンをクリックすると、入力欄に例文が自動入力されます")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("例1: 基本的な例", help="夏目漱石「吾輩は猫である」冒頭文"):
            st.session_state.jp_example_text = "吾輩は猫である。"
            st.session_state.jp_example_banned = "い"

    with col2:
        if st.button("例2: 複数文", help="有名なことわざ2つを組み合わせた例"):
            st.session_state.jp_example_text = "猿も木から落ちる。石の上にも三年。"
            st.session_state.jp_example_banned = "い,さ"

    with col3:
        if st.button("例3: 厳しい制約", help="川端康成「雪国」冒頭文での難しい例"):
            st.session_state.jp_example_text = "国境の長いトンネルを抜けると雪国であった。"
            st.session_state.jp_example_banned = "い,と,ぬ,ゆ"

    # Text input
    input_text = st.text_area(
        "変換したい文章を入力してください:",
        value=st.session_state.jp_example_text,
        height=150,
        placeholder="例: 今日は良い天気です。公園で猫と犬が遊んでいます。",
        help="複数の文章を入力できます。句点で自動的に文単位で処理されます。"
    )

    # Banned characters input
    banned_chars_input = st.text_input(
        "禁止文字（カンマ区切り）:",
        value=st.session_state.jp_example_banned,
        placeholder="例: い,し,た",
        help="使用を禁止する文字をカンマで区切って入力してください"
    )

    # Clear button
    if st.button("🗑️ 入力をクリア", help="入力欄をクリアします"):
        st.session_state.jp_example_text = ""
        st.session_state.jp_example_banned = ""
        st.rerun()

    # Generate button
    if st.button("🚀 リポグラム生成", type="primary", use_container_width=True):
        if not input_text.strip():
            st.error("❌ 文章を入力してください。")
            return

        if not banned_chars_input.strip():
            st.error("❌ 禁止文字を入力してください。")
            return

        # Parse banned characters
        banned_chars = parse_banned_chars(banned_chars_input)

        if not banned_chars:
            st.error("❌ 有効な禁止文字を入力してください。")
            return

        # Show processing message
        with st.spinner(f"🤖 {selected_model}で変換中..."):
            try:
                # Load configuration
                config = Config()
                config.model_name = selected_model

                # Initialize rewriter
                rewriter = RipogramRewriter(
                    api_key=config.openai_api_key,
                    model_name=config.model_name
                )

                # Display processing info
                st.info(f"📊 処理情報: モデル={selected_model}, 禁止文字={banned_chars}")

                if verbose_mode:
                    # Create a container for verbose output
                    verbose_container = st.container()

                    # Capture verbose output
                    import io
                    from contextlib import redirect_stdout

                    output_buffer = io.StringIO()

                    with redirect_stdout(output_buffer):
                        result = rewriter.rewrite_text_with_context(
                            text=input_text,
                            banned_chars=banned_chars,
                            verbose=True
                        )

                    # Display verbose output
                    verbose_output = output_buffer.getvalue()
                    if verbose_output:
                        with verbose_container:
                            st.subheader("🔍 変換過程の詳細")
                            st.code(verbose_output, language="text")
                else:
                    # Process without verbose output
                    result = rewriter.rewrite_text_with_context(
                        text=input_text,
                        banned_chars=banned_chars,
                        verbose=False
                    )

                # Display results
                st.subheader("🟢 変換結果")

                # Display original and result side by side
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**元の文章:**")
                    st.markdown(f"""
                    <div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 5px solid #ff6b6b;">
                    <p style="margin: 0; font-size: 16px; line-height: 1.6; color: #333;">{input_text}</p>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    st.markdown("**変換後:**")
                    st.markdown(f"""
                    <div style="background-color: #e8f5e8; padding: 15px; border-radius: 10px; border-left: 5px solid #4caf50;">
                    <p style="margin: 0; font-size: 16px; line-height: 1.6; color: #333; font-weight: 500;">{result}</p>
                    </div>
                    """, unsafe_allow_html=True)

                # Display statistics
                st.markdown("**統計情報:**")
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("元の文字数", len(input_text))
                with col2:
                    st.metric("変換後文字数", len(result))
                with col3:
                    st.metric("禁止文字数", len(banned_chars))

                # Success message
                st.success("✅ 変換が完了しました！")

                # Add to history
                st.session_state.history.append({
                    'language': 'Japanese',
                    'input': input_text,
                    'banned_chars': banned_chars,
                    'result': result,
                    'model': selected_model
                })

            except ValueError as e:
                st.error(f"❌ 設定エラー: {str(e)}")
                st.info("💡 .envファイルにOpenAI APIキーが正しく設定されているか確認してください。")

            except Exception as e:
                st.error(f"❌ エラーが発生しました: {str(e)}")
                if st.checkbox("詳細なエラー情報を表示"):
                    st.code(traceback.format_exc())


def english_page():
    """English lipogram generation page."""
    st.title("🎯 English Lipogram Generator")
    st.markdown("""
    **Lipogram** is a form of constrained writing where certain letters are deliberately avoided.
    This page uses BERT + WordNet approach to generate English lipograms by replacing words containing banned characters with semantically similar alternatives.
    """)

    # Settings in sidebar
    with st.sidebar:
        st.header("⚙️ English Settings")

        # Model selection
        model_options = {
            "BERT Base (Uncased)": "bert-base-uncased",
            "BERT Large (Uncased)": "bert-large-uncased",
            "DistilBERT": "distilbert-base-uncased"
        }

        selected_model_name = st.selectbox(
            "Select BERT Model:",
            options=list(model_options.keys()),
            index=0
        )
        model_name = model_options[selected_model_name]

        # Similarity threshold
        similarity_threshold = st.slider(
            "Similarity Threshold:",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            step=0.1,
            help="Minimum similarity score for word replacements"
        )

        # Verbose output
        verbose_output = st.checkbox(
            "Show Detailed Processing",
            value=False,
            help="Display detailed token processing information"
        )

        # Load model
        if st.button("🔄 Load/Reload Model"):
            st.session_state.english_model_loaded = False
            st.session_state.english_rewriter = None

        if not st.session_state.english_model_loaded:
            if not load_english_model(model_name):
                st.stop()

        # Display synonym examples
        st.markdown("### 📚 WordNet Synonym Examples")

        tokenizer = EnglishTokenizer()
        example_words = ["happy", "quick", "run", "beautiful", "house"]

        for word in example_words:
            synonyms = tokenizer.get_synonyms(word)
            if synonyms:
                with st.expander(f"'{word}' synonyms"):
                    st.write(", ".join(synonyms[:8]))

    # Main input area
    st.header("📝 Input")

    # Initialize session state for examples
    if 'en_example_text' not in st.session_state:
        st.session_state.en_example_text = ""
    if 'en_example_banned' not in st.session_state:
        st.session_state.en_example_banned = ""

    # Example buttons
    st.markdown("**Examples:** Click the buttons below to load example text")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Example 1: No 'E'", help="Classic lipogram avoiding the letter 'e'"):
            st.session_state.en_example_text = "The cat sat on the mat."
            st.session_state.en_example_banned = "e"

    with col2:
        if st.button("Example 2: No Vowels", help="Challenging example avoiding multiple vowels"):
            st.session_state.en_example_text = "Hello world! How are you today?"
            st.session_state.en_example_banned = "a e i o u"

    with col3:
        if st.button("Example 3: Complex", help="Complex sentence with multiple constraints"):
            st.session_state.en_example_text = "I love programming and artificial intelligence."
            st.session_state.en_example_banned = "a i"

    # Text input methods
    input_method = st.radio(
        "Input method:",
        ["Type text", "Upload file"],
        horizontal=True
    )

    input_text = ""

    if input_method == "Type text":
        input_text = st.text_area(
            "Enter your text:",
            value=st.session_state.en_example_text,
            height=150,
            placeholder="Type or paste your text here..."
        )
    else:
        uploaded_file = st.file_uploader(
            "Upload a text file:",
            type=['txt'],
            help="Upload a .txt file"
        )

        if uploaded_file is not None:
            try:
                input_text = str(uploaded_file.read(), "utf-8")
                st.text_area("File content:", value=input_text,
                             height=150, disabled=True)
            except Exception as e:
                st.error(f"Error reading file: {e}")

    # Banned characters input
    banned_chars_input = st.text_input(
        "Banned characters (space-separated):",
        value=st.session_state.en_example_banned,
        placeholder="e a i o u",
        help="Enter characters that should not appear in the output"
    )

    banned_chars = banned_chars_input.split() if banned_chars_input else []

    if banned_chars:
        st.write("**Banned characters:**")
        for char in banned_chars:
            st.code(char, language=None)

    # Quick presets
    st.write("**Quick presets:**")
    col_preset1, col_preset2 = st.columns(2)

    with col_preset1:
        if st.button("No 'E'"):
            st.session_state.en_example_banned = "e"
            st.rerun()

    with col_preset2:
        if st.button("No Vowels"):
            st.session_state.en_example_banned = "a e i o u"
            st.rerun()

    # Clear button
    if st.button("🗑️ Clear Input", help="Clear input fields"):
        st.session_state.en_example_text = ""
        st.session_state.en_example_banned = ""
        st.rerun()

    # Generate button
    if st.button("🎯 Generate Lipogram", type="primary", use_container_width=True):
        if not input_text.strip():
            st.error("❌ Please enter some text.")
        elif not banned_chars:
            st.error("❌ Please specify at least one banned character.")
        else:
            # Display input analysis
            display_token_analysis(input_text, banned_chars, 'English')

            # Generate lipogram
            with st.spinner("🔄 Generating lipogram..."):
                start_time = time.time()

                try:
                    if verbose_output:
                        # Capture verbose output
                        import io
                        from contextlib import redirect_stdout

                        output_buffer = io.StringIO()
                        with redirect_stdout(output_buffer):
                            result = st.session_state.english_rewriter.rewrite_text(
                                input_text, banned_chars, similarity_threshold, verbose=True
                            )

                        verbose_text = output_buffer.getvalue()
                    else:
                        result = st.session_state.english_rewriter.rewrite_text(
                            input_text, banned_chars, similarity_threshold, verbose=False
                        )
                        verbose_text = ""

                    processing_time = time.time() - start_time

                    # Display results
                    st.header("✨ Generated Lipogram")

                    # Result text
                    st.text_area(
                        "Result:",
                        value=result,
                        height=150,
                        help="Generated lipogram text"
                    )

                    # Verification
                    is_valid, banned_found = verify_lipogram(
                        result, banned_chars)

                    col_result1, col_result2, col_result3 = st.columns(3)

                    with col_result1:
                        if is_valid:
                            st.success("✅ Valid lipogram!")
                        else:
                            st.error(
                                f"❌ Contains banned chars: {', '.join(banned_found)}")

                    with col_result2:
                        st.info(f"⏱️ Processing time: {processing_time:.2f}s")

                    with col_result3:
                        st.info(
                            f"📊 Similarity threshold: {similarity_threshold}")

                    # Verbose output
                    if verbose_output and verbose_text:
                        with st.expander("🔍 Detailed Processing Log", expanded=False):
                            st.text(verbose_text)

                    # Download button
                    st.download_button(
                        label="💾 Download Result",
                        data=result,
                        file_name="lipogram_result.txt",
                        mime="text/plain"
                    )

                    # Add to history
                    st.session_state.history.append({
                        'language': 'English',
                        'input': input_text,
                        'banned_chars': banned_chars,
                        'result': result,
                        'is_valid': is_valid,
                        'processing_time': processing_time,
                        'similarity_threshold': similarity_threshold
                    })

                except Exception as e:
                    st.error(f"❌ Error generating lipogram: {e}")
                    st.error("Please check your input and try again.")


def history_page():
    """History page showing generation history."""
    st.title("📚 Generation History")
    st.markdown(
        "View your previous lipogram generations from both Japanese and English modes.")

    if not st.session_state.history:
        st.info(
            "📝 No generation history yet. Generate some lipograms to see them here!")
        return

    # Filter options
    col1, col2 = st.columns(2)

    with col1:
        language_filter = st.selectbox(
            "Filter by language:",
            ["All", "Japanese", "English"]
        )

    with col2:
        if st.button("🗑️ Clear All History"):
            st.session_state.history = []
            st.rerun()

    # Filter history
    filtered_history = st.session_state.history
    if language_filter != "All":
        filtered_history = [
            entry for entry in st.session_state.history if entry['language'] == language_filter]

    st.write(f"**Showing {len(filtered_history)} entries**")

    # Display history
    for i, entry in enumerate(reversed(filtered_history), 1):
        with st.expander(f"{entry['language']} Generation #{len(filtered_history) - i + 1}"):
            col_hist1, col_hist2 = st.columns(2)

            with col_hist1:
                st.write("**Input:**")
                st.text(
                    entry['input'][:200] + "..." if len(entry['input']) > 200 else entry['input'])

                st.write("**Banned characters:**")
                st.code(", ".join(entry['banned_chars']))

            with col_hist2:
                st.write("**Result:**")
                st.text(
                    entry['result'][:200] + "..." if len(entry['result']) > 200 else entry['result'])

                if entry['language'] == 'Japanese':
                    st.write(f"**Model:** {entry.get('model', 'Unknown')}")
                else:
                    status = "✅ Valid" if entry.get(
                        'is_valid', False) else "❌ Invalid"
                    st.write(f"**Status:** {status}")
                    st.write(
                        f"**Time:** {entry.get('processing_time', 0):.2f}s")
                    st.write(
                        f"**Threshold:** {entry.get('similarity_threshold', 0):.1f}")


def main():
    """Main Streamlit application."""
    initialize_session_state()

    # Check imports
    if not IMPORTS_AVAILABLE:
        st.error(f"❌ Import Error: {IMPORT_ERROR}")
        st.error("Please make sure all dependencies are installed.")
        st.info("Run: pip install -r requirements.txt")
        st.stop()

    # Check if PDF slideshow should be displayed
    if st.session_state.show_pdf_slideshow:
        show_pdf_slideshow()
        return

    # Sidebar navigation
    with st.sidebar:
        st.title("🌐 Navigation")

        # Page selection
        page_options = ["📝 Japanese", "🎯 English", "📚 History", "🎓 Research"]
        selected_page = st.radio("Select Page:", page_options)

        # Update current page
        if selected_page == "📝 Japanese":
            st.session_state.current_page = 'Japanese'
        elif selected_page == "🎯 English":
            st.session_state.current_page = 'English'
        elif selected_page == "📚 History":
            st.session_state.current_page = 'History'
        elif selected_page == "🎓 Research":
            st.session_state.show_pdf_slideshow = True
            st.rerun()

        st.markdown("---")

        # Quick stats
        if st.session_state.history:
            st.markdown("**Quick Stats:**")
            japanese_count = len(
                [h for h in st.session_state.history if h['language'] == 'Japanese'])
            english_count = len(
                [h for h in st.session_state.history if h['language'] == 'English'])
            st.write(f"🇯🇵 Japanese: {japanese_count}")
            st.write(f"🇺🇸 English: {english_count}")
            st.write(f"📊 Total: {len(st.session_state.history)}")

    # Main content area
    if st.session_state.current_page == 'Japanese':
        japanese_page()
    elif st.session_state.current_page == 'English':
        english_page()
    elif st.session_state.current_page == 'History':
        history_page()

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray;'>
    <p>🌐 統合リポグラム生成器 | 日本語: OpenAI GPT-4 | English: BERT + WordNet</p>
    <p>Based on research in constraint-based text generation</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
