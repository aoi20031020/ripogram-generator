"""
PDF Viewer functions for displaying presentation slides
PDFスライド表示機能
"""

import streamlit as st
import base64
from pathlib import Path


def show_pdf_viewer():
    """Display PDF as slideshow."""
    st.title("🎓 研究発表スライド（PDF版）")
    st.markdown("**2025/05/25 | 中央大学国際情報学部４年 | 22G1104002B 橋本 葵**")

    pdf_path = Path("中間発表リポグラム.pptx.pdf")

    if not pdf_path.exists():
        st.error("❌ PDFファイルが見つかりません: 中間発表リポグラム.pptx.pdf")
        return

    # PDF display options
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        display_mode = st.radio(
            "表示モード",
            ["📖 埋め込み表示", "🔗 ダウンロードリンク", "📱 モバイル対応表示"],
            horizontal=True
        )

    if display_mode == "📖 埋め込み表示":
        display_embedded_pdf(pdf_path)
    elif display_mode == "🔗 ダウンロードリンク":
        display_download_link(pdf_path)
    else:
        display_mobile_friendly(pdf_path)


def display_embedded_pdf(pdf_path: Path):
    """Display PDF embedded in the page."""
    try:
        with open(pdf_path, "rb") as f:
            pdf_data = f.read()

        # Encode PDF to base64
        pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')

        # Create PDF viewer HTML
        pdf_display = f"""
        <div style="width: 100%; height: 800px; border: 1px solid #ddd; border-radius: 10px; overflow: hidden;">
            <iframe 
                src="data:application/pdf;base64,{pdf_base64}" 
                width="100%" 
                height="100%" 
                type="application/pdf"
                style="border: none;">
                <p>PDFを表示できません。ブラウザがPDF表示をサポートしていない可能性があります。</p>
            </iframe>
        </div>
        """

        st.markdown(pdf_display, unsafe_allow_html=True)

        # Additional controls
        st.markdown("---")
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🔄 再読み込み"):
                st.rerun()

        with col2:
            st.markdown(f"**ファイルサイズ:** {len(pdf_data) / 1024:.1f} KB")

        with col3:
            st.download_button(
                label="📥 PDFダウンロード",
                data=pdf_data,
                file_name="中間発表リポグラム.pdf",
                mime="application/pdf"
            )

    except Exception as e:
        st.error(f"❌ PDFの読み込みに失敗しました: {str(e)}")


def display_download_link(pdf_path: Path):
    """Display download link for PDF."""
    try:
        with open(pdf_path, "rb") as f:
            pdf_data = f.read()

        st.info("📄 PDFファイルをダウンロードして表示してください。")

        # Large download button
        st.download_button(
            label="📥 研究発表スライドをダウンロード",
            data=pdf_data,
            file_name="中間発表リポグラム.pdf",
            mime="application/pdf",
            use_container_width=True
        )

        # File information
        st.markdown("---")
        st.markdown("**ファイル情報:**")
        col1, col2 = st.columns(2)

        with col1:
            st.metric("ファイルサイズ", f"{len(pdf_data) / 1024:.1f} KB")

        with col2:
            st.metric("ページ数", "16ページ")

        # Instructions
        st.markdown("---")
        st.markdown("""
        **表示方法:**
        1. 上のボタンをクリックしてPDFをダウンロード
        2. ダウンロードしたファイルをPDFビューアーで開く
        3. フルスクリーンモードでプレゼンテーション表示
        """)

    except Exception as e:
        st.error(f"❌ PDFの読み込みに失敗しました: {str(e)}")


def display_mobile_friendly(pdf_path: Path):
    """Display mobile-friendly PDF viewer."""
    try:
        with open(pdf_path, "rb") as f:
            pdf_data = f.read()

        st.info("📱 モバイルデバイス向けの表示です。")

        # PDF.js viewer URL
        pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')

        # Use PDF.js for better mobile compatibility
        pdf_js_url = f"https://mozilla.github.io/pdf.js/web/viewer.html?file=data:application/pdf;base64,{pdf_base64}"

        st.markdown(f"""
        <div style="text-align: center; margin: 20px 0;">
            <a href="{pdf_js_url}" target="_blank" style="
                display: inline-block;
                padding: 15px 30px;
                background-color: #4CAF50;
                color: white;
                text-decoration: none;
                border-radius: 10px;
                font-size: 18px;
                font-weight: bold;
            ">
                📱 新しいタブでPDFを開く
            </a>
        </div>
        """, unsafe_allow_html=True)

        # Alternative: Simple iframe with responsive design
        st.markdown("---")
        st.markdown("**または、下記の埋め込み表示をご利用ください:**")

        pdf_display = f"""
        <div style="width: 100%; height: 600px; border: 1px solid #ddd; border-radius: 10px; overflow: hidden;">
            <iframe 
                src="data:application/pdf;base64,{pdf_base64}#toolbar=1&navpanes=1&scrollbar=1&page=1&view=FitH" 
                width="100%" 
                height="100%" 
                type="application/pdf"
                style="border: none;">
                <p>PDFを表示できません。上のリンクから新しいタブで開いてください。</p>
            </iframe>
        </div>
        """

        st.markdown(pdf_display, unsafe_allow_html=True)

        # Download option
        st.markdown("---")
        st.download_button(
            label="📥 PDFダウンロード",
            data=pdf_data,
            file_name="中間発表リポグラム.pdf",
            mime="application/pdf",
            use_container_width=True
        )

    except Exception as e:
        st.error(f"❌ PDFの読み込みに失敗しました: {str(e)}")


def show_pdf_slideshow():
    """Display PDF as a slideshow with navigation."""
    st.title("🎓 研究発表スライドショー")
    st.markdown("**2025/05/25 | 中央大学国際情報学部４年 | 22G1104002B 橋本 葵**")

    # Initialize session state for slide navigation
    if 'current_slide' not in st.session_state:
        st.session_state.current_slide = 1

    total_slides = 16  # Total number of slides in the PDF

    # Navigation controls
    col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])

    with col1:
        if st.button("⏮️ 最初", help="最初のスライドに移動"):
            st.session_state.current_slide = 1

    with col2:
        if st.button("◀️ 前へ", help="前のスライドに移動"):
            if st.session_state.current_slide > 1:
                st.session_state.current_slide -= 1

    with col3:
        st.session_state.current_slide = st.slider(
            "スライド番号",
            min_value=1,
            max_value=total_slides,
            value=st.session_state.current_slide,
            help=f"スライド {st.session_state.current_slide} / {total_slides}"
        )

    with col4:
        if st.button("▶️ 次へ", help="次のスライドに移動"):
            if st.session_state.current_slide < total_slides:
                st.session_state.current_slide += 1

    with col5:
        if st.button("⏭️ 最後", help="最後のスライドに移動"):
            st.session_state.current_slide = total_slides

    # Display current slide info
    st.markdown(
        f"**現在のスライド: {st.session_state.current_slide} / {total_slides}**")

    # Display PDF with specific page
    pdf_path = Path("中間発表リポグラム.pptx.pdf")

    if pdf_path.exists():
        try:
            with open(pdf_path, "rb") as f:
                pdf_data = f.read()

            pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')

            # Display PDF with specific page focused
            pdf_display = f"""
            <div style="width: 100%; height: 700px; border: 1px solid #ddd; border-radius: 10px; overflow: hidden;">
                <iframe 
                    src="data:application/pdf;base64,{pdf_base64}#page={st.session_state.current_slide}&toolbar=1&navpanes=0&scrollbar=0&view=FitH" 
                    width="100%" 
                    height="100%" 
                    type="application/pdf"
                    style="border: none;">
                    <p>PDFを表示できません。ブラウザがPDF表示をサポートしていない可能性があります。</p>
                </iframe>
            </div>
            """

            st.markdown(pdf_display, unsafe_allow_html=True)

            # Keyboard shortcuts info
            st.markdown("---")
            st.info("💡 **キーボードショートカット:** ← → キーでスライドを移動できます（PDFビューアー内で）")

        except Exception as e:
            st.error(f"❌ PDFの読み込みに失敗しました: {str(e)}")
    else:
        st.error("❌ PDFファイルが見つかりません: 中間発表リポグラム.pptx.pdf")
