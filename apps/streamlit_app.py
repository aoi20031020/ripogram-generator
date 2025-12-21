"""
Streamlit Web Application for Ripogram Generation
日本語リポグラム生成のためのWebアプリケーション
"""

import sys
import os
from pathlib import Path
from typing import List

# Ensure project root is on sys.path (so `import ripogram` works regardless of CWD)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from ripogram.core.rewriter import RipogramRewriter
from ripogram.config import Config
import streamlit as st
import traceback
import base64

# NOTE: sys.path is configured above before importing ripogram.


# Page configuration
st.set_page_config(
    page_title="日本語リポグラムジェネレーター",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)


def parse_banned_chars(banned_chars_str: str) -> List[str]:
    """Parse banned characters string into list."""
    if not banned_chars_str.strip():
        return []
    return [char.strip() for char in banned_chars_str.split(",")]


def display_conversion_result(result: str, original: str, banned_chars: List[str]):
    """Display the conversion result with formatting."""
    st.subheader("🟢 変換結果")

    # Display original and result side by side
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**元の文章:**")
        st.markdown(f"""
        <div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 5px solid #ff6b6b;">
        <p style="margin: 0; font-size: 16px; line-height: 1.6; color: #333;">{original}</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("**変換後:**")
        st.markdown(f"""
        <div style="background-color: #e8f5e8; padding: 15px; border-radius: 10px; border-left: 5px solid #4caf50;">
        <p style="margin: 0; font-size: 16px; line-height: 1.6; color: #333; font-weight: 500;">{result}</p>
        </div>
        """, unsafe_allow_html=True)

    # Copy buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📋 元の文章をコピー", help="元の文章をクリップボードにコピー"):
            st.write("📋 元の文章がコピーされました（手動でコピーしてください）")
            st.code(original, language="text")

    with col2:
        if st.button("📋 変換結果をコピー", help="変換結果をクリップボードにコピー"):
            st.write("📋 変換結果がコピーされました（手動でコピーしてください）")
            st.code(result, language="text")

    # Display statistics
    st.markdown("**統計情報:**")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("元の文字数", len(original))
    with col2:
        st.metric("変換後文字数", len(result))
    with col3:
        st.metric("禁止文字数", len(banned_chars))


def show_pdf_slideshow():
    """Display PDF as a slideshow with navigation."""
    st.title("🎓 研究発表スライドショー")
    st.markdown("** 中央大学国際情報学部４年 | 22G1104002B 橋本 葵**")

    # Initialize session state for slide navigation
    if 'current_slide' not in st.session_state:
        st.session_state.current_slide = 1
    if 'fullscreen_mode' not in st.session_state:
        st.session_state.fullscreen_mode = False

    total_slides = 16  # Total number of slides in the PDF

    # Display controls
    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown(
            f"**スライド: {st.session_state.current_slide} / {total_slides}**")

    with col2:
        if st.button("🔍 最大化", help="PDFを画面に合わせて最大化"):
            st.session_state.fullscreen_mode = not st.session_state.fullscreen_mode

    # Display PDF with specific page
    pdf_path = Path("中間発表リポグラム.pptx.pdf")

    if pdf_path.exists():
        try:
            with open(pdf_path, "rb") as f:
                pdf_data = f.read()

            pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')

            # Display current mode
            if st.session_state.fullscreen_mode:
                fullscreen_status = "🔍 最大化モード"
            else:
                fullscreen_status = "📄 標準モード"
            
            st.markdown(f"**表示モード:** {fullscreen_status}")

            # Display PDF with specific page focused
            if st.session_state.fullscreen_mode:
                # Fullscreen overlay - PDFサイズに最適化
                pdf_display = f"""
                <div style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: 9999; background: white; padding: 10px; box-sizing: border-box;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                        <h3>🎓 研究発表スライドショー - スライド {st.session_state.current_slide}/{total_slides}</h3>
                        <button onclick="window.parent.postMessage({{type: 'streamlit:setComponentValue', value: 'close_fullscreen'}}, '*')" 
                                style="background: #ff4444; color: white; border: none; padding: 8px 16px; border-radius: 5px; cursor: pointer; font-size: 14px;">
                            ❌ 終了
                        </button>
                    </div>
                    <div style="width: 100%; height: calc(100vh - 50px); display: flex; justify-content: center; align-items: center; background: #f5f5f5;">
                        <div style="width: 90%; height: 90%; max-width: 1200px; border: 2px solid #4CAF50; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);">
                            <iframe 
                                src="data:application/pdf;base64,{pdf_base64}#page={st.session_state.current_slide}&toolbar=0&navpanes=0&scrollbar=0&view=Fit" 
                                width="100%" 
                                height="100%" 
                                type="application/pdf"
                                style="border: none;">
                                <p>PDFを表示できません。ブラウザがPDF表示をサポートしていない可能性があります。</p>
                            </iframe>
                        </div>
                    </div>
                </div>
                """

                # Use components.html for fullscreen overlay
                import streamlit.components.v1 as components
                components.html(pdf_display, height=800, scrolling=False)

            else:
                # Standard display - PDFのアスペクト比に合わせて調整
                pdf_display = f"""
                <div style="width: 100%; max-width: 900px; margin: 0 auto;">
                    <div style="position: relative; width: 100%; padding-bottom: 70.7%; /* 16:9のアスペクト比に近い */ border: 1px solid #ddd; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);">
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

            # Force refresh when slide changes by adding a unique element
            st.markdown(
                f"<!-- Slide {st.session_state.current_slide} -->", unsafe_allow_html=True)

            # Keyboard shortcuts info
            st.markdown("---")
            st.info("💡 **キーボードショートカット:** ← → キーでスライドを移動できます（PDFビューアー内で）")

            # Close slideshow button
            if st.button("❌ スライドショーを閉じる", type="secondary"):
                st.session_state.show_pdf_slideshow = False
                st.rerun()

        except Exception as e:
            st.error(f"❌ PDFの読み込みに失敗しました: {str(e)}")
    else:
        st.error("❌ PDFファイルが見つかりません: 中間発表リポグラム.pptx.pdf")


def main():
    """Main Streamlit application."""

    # Initialize session state
    if 'show_pdf_slideshow' not in st.session_state:
        st.session_state.show_pdf_slideshow = False

    # Check if PDF slideshow should be displayed
    if st.session_state.show_pdf_slideshow:
        show_pdf_slideshow()
        return

    # Title and description
    st.title("📝 日本語リポグラムジェネレーター")
    st.markdown("""
    **リポグラム（Lipogram）** とは、特定の文字を使わずに文章を書く言葉遊びです。
    このアプリでは、AI（GPT-4.1 nano）を使って日本語の文章から指定した文字を除いた自然な文章を生成します。
    """)

    # Sidebar for settings
    with st.sidebar:
        st.header("⚙️ 設定")

        # Model selection
        model_options = [
            "gpt-4.1-nano",
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

        # PDF Slideshow section
        st.markdown("---")
        st.markdown("**📄 研究発表スライド:**")

        if st.button("🎬 PDFスライドショーを表示", use_container_width=True):
            st.session_state.show_pdf_slideshow = True
            st.rerun()

    # Main input area
    st.header("📝 入力")

    # Initialize session state for examples
    if 'example_text' not in st.session_state:
        st.session_state.example_text = ""
    if 'example_banned' not in st.session_state:
        st.session_state.example_banned = ""

    # Example buttons
    st.markdown("**使用例:** 以下のボタンをクリックすると、入力欄に例文が自動入力されます")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("例1: 基本的な例", help="夏目漱石「吾輩は猫である」冒頭文"):
            st.session_state.example_text = "吾輩は猫である。"
            st.session_state.example_banned = "い"

    with col2:
        if st.button("例2: 複数文", help="有名なことわざ2つを組み合わせた例"):
            st.session_state.example_text = "猿も木から落ちる。石の上にも三年。"
            st.session_state.example_banned = "い,さ"

    with col3:
        if st.button("例3: 厳しい制約", help="川端康成「雪国」冒頭文での難しい例"):
            st.session_state.example_text = "国境の長いトンネルを抜けると雪国であった。"
            st.session_state.example_banned = "い,と,ぬ,ゆ"

    # Text input with session state values
    input_text = st.text_area(
        "変換したい文章を入力してください:",
        value=st.session_state.example_text,
        height=150,
        placeholder="例: 今日は良い天気です。公園で猫と犬が遊んでいます。",
        help="複数の文章を入力できます。句点で自動的に文単位で処理されます。"
    )

    # Banned characters input with session state values
    banned_chars_input = st.text_input(
        "禁止文字（カンマ区切り）:",
        value=st.session_state.example_banned,
        placeholder="例: い,し,た",
        help="使用を禁止する文字をカンマで区切って入力してください"
    )

    # Clear button
    if st.button("🗑️ 入力をクリア", help="入力欄をクリアします"):
        st.session_state.example_text = ""
        st.session_state.example_banned = ""
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
                display_conversion_result(result, input_text, banned_chars)

                # Success message
                st.success("✅ 変換が完了しました！")

            except ValueError as e:
                st.error(f"❌ 設定エラー: {str(e)}")
                st.info("💡 .envファイルにOpenAI APIキーが正しく設定されているか確認してください。")

            except Exception as e:
                st.error(f"❌ エラーが発生しました: {str(e)}")
                if st.checkbox("詳細なエラー情報を表示"):
                    st.code(traceback.format_exc())

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray;'>
    <p>日本語リポグラム生成器 | Powered by OpenAI GPT-4.1 nano</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
