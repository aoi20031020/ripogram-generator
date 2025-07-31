"""
Streamlit web application for English Lipogram Generation using BERT + WordNet.
"""

import streamlit as st
import sys
import os
import time
from typing import List

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from ripogram.core.english_bert_rewriter import EnglishBertRewriter
    from ripogram.core.english_tokenizer import EnglishTokenizer
except ImportError as e:
    st.error(f"Import error: {e}")
    st.error("Please make sure all dependencies are installed.")
    st.stop()


def initialize_session_state():
    """Initialize session state variables."""
    if 'rewriter' not in st.session_state:
        st.session_state.rewriter = None
    if 'model_loaded' not in st.session_state:
        st.session_state.model_loaded = False
    if 'history' not in st.session_state:
        st.session_state.history = []


def load_model(model_name: str):
    """Load BERT model with caching."""
    if st.session_state.rewriter is None or not st.session_state.model_loaded:
        with st.spinner(f"Loading BERT model: {model_name}..."):
            try:
                st.session_state.rewriter = EnglishBertRewriter(model_name)
                st.session_state.model_loaded = True
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


def display_token_analysis(text: str, banned_chars: List[str]):
    """Display token analysis in an expandable section."""
    with st.expander("🔍 Token Analysis", expanded=False):
        tokenizer = EnglishTokenizer()
        tokens = tokenizer.tokenize(text)

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
                st.write(", ".join(valid_tokens))
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
                st.write(", ".join(invalid_tokens))
            else:
                st.write("None")


def display_synonym_examples():
    """Display synonym examples in sidebar."""
    st.sidebar.markdown("### 📚 WordNet Synonym Examples")

    tokenizer = EnglishTokenizer()

    example_words = ["happy", "quick", "run", "beautiful", "house"]

    for word in example_words:
        synonyms = tokenizer.get_synonyms(word)
        if synonyms:
            with st.sidebar.expander(f"'{word}' synonyms"):
                st.write(", ".join(synonyms[:8]))


def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="English Lipogram Generator",
        page_icon="🎯",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    initialize_session_state()

    # Header
    st.title("🎯 English Lipogram Generator")
    st.markdown(
        "**BERT + WordNet Approach for Constraint-Based Text Rewriting**")

    # Sidebar configuration
    st.sidebar.header("⚙️ Configuration")

    # Model selection
    model_options = {
        "BERT Base (Uncased)": "bert-base-uncased",
        "BERT Large (Uncased)": "bert-large-uncased",
        "DistilBERT": "distilbert-base-uncased"
    }

    selected_model_name = st.sidebar.selectbox(
        "Select BERT Model:",
        options=list(model_options.keys()),
        index=0
    )
    model_name = model_options[selected_model_name]

    # Similarity threshold
    similarity_threshold = st.sidebar.slider(
        "Similarity Threshold:",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.1,
        help="Minimum similarity score for word replacements"
    )

    # Verbose output
    verbose_output = st.sidebar.checkbox(
        "Show Detailed Processing",
        value=False,
        help="Display detailed token processing information"
    )

    # Load model
    if st.sidebar.button("🔄 Load/Reload Model"):
        st.session_state.model_loaded = False
        st.session_state.rewriter = None

    if not st.session_state.model_loaded:
        if not load_model(model_name):
            st.stop()

    # Display synonym examples
    display_synonym_examples()

    # Main interface
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("📝 Input Text")

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

    with col2:
        st.header("🚫 Constraints")

        # Banned characters input
        banned_chars_input = st.text_input(
            "Banned characters (space-separated):",
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
                st.session_state.banned_preset = "e"

        with col_preset2:
            if st.button("No Vowels"):
                st.session_state.banned_preset = "a e i o u"

        if 'banned_preset' in st.session_state:
            banned_chars_input = st.session_state.banned_preset
            banned_chars = banned_chars_input.split()
            del st.session_state.banned_preset
            st.rerun()

    # Generate button
    if st.button("🎯 Generate Lipogram", type="primary", use_container_width=True):
        if not input_text.strip():
            st.error("❌ Please enter some text.")
        elif not banned_chars:
            st.error("❌ Please specify at least one banned character.")
        else:
            # Display input analysis
            display_token_analysis(input_text, banned_chars)

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
                            result = st.session_state.rewriter.rewrite_text(
                                input_text, banned_chars, similarity_threshold, verbose=True
                            )

                        verbose_text = output_buffer.getvalue()
                    else:
                        result = st.session_state.rewriter.rewrite_text(
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

                    # Add to history
                    st.session_state.history.append({
                        'input': input_text,
                        'banned_chars': banned_chars,
                        'result': result,
                        'is_valid': is_valid,
                        'processing_time': processing_time,
                        'similarity_threshold': similarity_threshold
                    })

                    # Download button
                    st.download_button(
                        label="💾 Download Result",
                        data=result,
                        file_name="lipogram_result.txt",
                        mime="text/plain"
                    )

                except Exception as e:
                    st.error(f"❌ Error generating lipogram: {e}")
                    st.error("Please check your input and try again.")

    # History section
    if st.session_state.history:
        st.header("📚 Generation History")

        for i, entry in enumerate(reversed(st.session_state.history[-5:]), 1):
            with st.expander(f"Generation {len(st.session_state.history) - i + 1}"):
                col_hist1, col_hist2 = st.columns(2)

                with col_hist1:
                    st.write("**Input:**")
                    st.text(
                        entry['input'][:100] + "..." if len(entry['input']) > 100 else entry['input'])

                    st.write("**Banned characters:**")
                    st.code(", ".join(entry['banned_chars']))

                with col_hist2:
                    st.write("**Result:**")
                    st.text(
                        entry['result'][:100] + "..." if len(entry['result']) > 100 else entry['result'])

                    status = "✅ Valid" if entry['is_valid'] else "❌ Invalid"
                    st.write(f"**Status:** {status}")
                    st.write(f"**Time:** {entry['processing_time']:.2f}s")

        if st.button("🗑️ Clear History"):
            st.session_state.history = []
            st.rerun()

    # Footer
    st.markdown("---")
    st.markdown(
        "**English Lipogram Generator** - Powered by BERT + WordNet | "
        "Based on research in constraint-based text generation"
    )


if __name__ == "__main__":
    main()
