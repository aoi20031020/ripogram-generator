"""
Ripogram (リポグラム) Generation Library

A Python library for generating lipograms in Japanese using OpenAI GPT-4.
Lipograms are texts that avoid using specific characters.
"""

__version__ = "1.0.0"
__author__ = "Your Name"

from .core.rewriter import RipogramRewriter
from .core.tokenizer import JapaneseTokenizer

__all__ = ["RipogramRewriter", "JapaneseTokenizer"]
