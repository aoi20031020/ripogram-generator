"""
Utility functions for ripogram generation.
"""

from typing import List


def katakana_to_hiragana(katakana: str) -> str:
    """
    Convert katakana characters to hiragana.
    
    Args:
        katakana: String containing katakana characters
        
    Returns:
        String with katakana converted to hiragana
    """
    return ''.join([
        chr(ord(c) - 0x60) if 'ァ' <= c <= 'ン' else c 
        for c in katakana
    ])


def contains_banned(text: str, banned_chars: List[str]) -> bool:
    """
    Check if text contains any banned characters.
    
    Args:
        text: Text to check
        banned_chars: List of banned characters
        
    Returns:
        True if text contains any banned characters, False otherwise
    """
    return any(char in text for char in banned_chars)
