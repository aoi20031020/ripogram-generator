"""
Japanese tokenization module using fugashi.
"""

from typing import List
from fugashi import Tagger
from .utils import katakana_to_hiragana


class JapaneseTokenizer:
    """Japanese tokenizer using fugashi with Unidic."""
    
    def __init__(self):
        """Initialize the tokenizer with fugashi."""
        self.tagger = Tagger()
    
    def get_reading(self, token) -> str:
        """
        Get the reading (hiragana) of a token.
        
        Args:
            token: Fugashi token object
            
        Returns:
            Hiragana reading of the token
        """
        try:
            # Try to get reading from Unidic features
            reading = getattr(token.feature, "kana", None) or \
                     getattr(token.feature, "reading", None)
            if reading and reading != "*":
                return katakana_to_hiragana(reading)
        except Exception as e:
            print(f"[読み取得エラー] {token.surface} : {e}")
        
        # Fallback to surface form converted to hiragana
        return katakana_to_hiragana(token.surface)
    
    def get_pos(self, token) -> str:
        """
        Get the part-of-speech of a token.
        
        Args:
            token: Fugashi token object
            
        Returns:
            Part-of-speech string
        """
        try:
            pos = getattr(token.feature, "pos1", None)
            return pos if pos and pos != "*" else "名詞"
        except Exception as e:
            print(f"[品詞取得エラー] {token.surface} : {e}")
        return "名詞"  # Default to noun
    
    def tokenize(self, sentence: str) -> List[dict]:
        """
        Tokenize a Japanese sentence.
        
        Args:
            sentence: Input Japanese sentence
            
        Returns:
            List of token dictionaries with surface, reading, and pos
        """
        tokens = []
        for token in self.tagger(sentence):
            tokens.append({
                'surface': token.surface,
                'reading': self.get_reading(token),
                'pos': self.get_pos(token),
                'token': token  # Keep original token for reference
            })
        return tokens
