#!/usr/bin/env python3
"""
Simple test script for ripogram functionality.
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, '.')

def test_basic_functionality():
    """Test basic functionality without API calls."""
    try:
        from ripogram.core.utils import katakana_to_hiragana, contains_banned
        from ripogram.core.tokenizer import JapaneseTokenizer
        
        print("🔵 Testing utility functions...")
        
        # Test katakana to hiragana conversion
        katakana_text = "サル"
        hiragana_result = katakana_to_hiragana(katakana_text)
        print(f"カタカナ→ひらがな: {katakana_text} → {hiragana_result}")
        
        # Test banned character detection
        banned_chars = ["さ", "い"]
        test_text = "さる"
        is_banned = contains_banned(test_text, banned_chars)
        print(f"禁止文字チェック: '{test_text}' contains {banned_chars} → {is_banned}")
        
        print("🔵 Testing tokenizer...")
        
        # Test tokenizer (this requires fugashi to be installed)
        try:
            tokenizer = JapaneseTokenizer()
            sentence = "さるも木から落ちる"
            tokens = tokenizer.tokenize(sentence)
            
            print(f"入力文: {sentence}")
            for token in tokens:
                print(f"  - {token['surface']} (読み: {token['reading']}, 品詞: {token['pos']})")
                
        except ImportError as e:
            print(f"⚠️  Tokenizer test skipped: {e}")
            print("   Install fugashi with: pip install fugashi[unidic-lite]")
        
        print("✅ Basic functionality tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    return True

def test_cli_help():
    """Test CLI help functionality."""
    try:
        print("\n🔵 Testing CLI help...")
        os.system("python -m ripogram.cli --help")
        print("✅ CLI help test completed!")
        return True
    except Exception as e:
        print(f"❌ CLI test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting ripogram tests...\n")
    
    success = True
    success &= test_basic_functionality()
    success &= test_cli_help()
    
    if success:
        print("\n🎉 All tests passed!")
        print("\n📝 Next steps:")
        print("1. Create a .env file with your OpenAI API key")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Test with: python -m ripogram.cli 'さるも木から落ちる' --banned-chars 'さ,い' --verbose")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
