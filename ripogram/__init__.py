"""
Ripogram (リポグラム) Generation Library

A Python library for generating lipograms in Japanese using OpenAI GPT-4.
Lipograms are texts that avoid using specific characters.
"""

__version__ = "1.0.0"
__author__ = "Your Name"

from .core.rewriter import RipogramRewriter
from .core.tokenizer import JapaneseTokenizer
from .metrics import (
    ConstraintCheckResult,
    tokenize_japanese,
    content_tokens,
    extract_reading,
    check_constraint,
    compute_vrr,
    compute_ttr,
    ngram_repetition_rate,
    measure_time,
)

__all__ = [
    "RipogramRewriter",
    "JapaneseTokenizer",
    # Metrics
    "ConstraintCheckResult",
    "tokenize_japanese",
    "content_tokens",
    "extract_reading",
    "check_constraint",
    "compute_vrr",
    "compute_ttr",
    "ngram_repetition_rate",
    "measure_time",
]
