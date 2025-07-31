"""
Test script for English lipogram generation using BERT + WordNet.
"""

from ripogram.core.english_tokenizer import EnglishTokenizer
from ripogram.core.english_bert_rewriter import EnglishBertRewriter
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_english_tokenizer():
    """Test the English tokenizer."""
    print("🧪 Testing English Tokenizer")
    print("=" * 40)

    tokenizer = EnglishTokenizer()

    # Test sentence
    sentence = "The quick brown fox jumps over the lazy dog."
    print(f"Input: {sentence}")

    tokens = tokenizer.tokenize(sentence)
    print(f"Tokens ({len(tokens)}):")

    for i, token in enumerate(tokens):
        print(
            f"  {i+1}. {token['surface']} (POS: {token['pos']}, Phonetic: {token['phonetic']})")

    # Test synonyms
    print(f"\nSynonyms for 'quick':")
    synonyms = tokenizer.get_synonyms("quick", "ADJ")
    print(f"  {synonyms[:10]}")  # Show first 10 synonyms

    print(f"\nSynonyms for 'jump':")
    synonyms = tokenizer.get_synonyms("jump", "VERB")
    print(f"  {synonyms[:10]}")

    print("✅ English tokenizer test completed\n")


def test_simple_lipogram():
    """Test simple lipogram generation."""
    print("🧪 Testing Simple Lipogram Generation")
    print("=" * 40)

    # Initialize rewriter
    print("🔄 Loading BERT model...")
    rewriter = EnglishBertRewriter("bert-base-uncased")
    print("✅ BERT model loaded")

    # Test cases
    test_cases = [
        {
            "text": "The cat sat on the mat.",
            "banned": ["e"],
            "description": "Avoiding letter 'e'"
        },
        {
            "text": "Hello world! How are you today?",
            "banned": ["l", "o"],
            "description": "Avoiding letters 'l' and 'o'"
        },
        {
            "text": "I love programming and artificial intelligence.",
            "banned": ["a", "i"],
            "description": "Avoiding letters 'a' and 'i'"
        }
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test Case {i}: {test_case['description']}")
        print(f"Input: {test_case['text']}")
        print(f"Banned: {', '.join(test_case['banned'])}")
        print("-" * 40)

        try:
            result = rewriter.rewrite_text(
                test_case["text"],
                test_case["banned"],
                similarity_threshold=0.3,  # Lower threshold for testing
                verbose=True
            )

            # Verify result
            banned_found = []
            for char in test_case["banned"]:
                if char.lower() in result.lower():
                    banned_found.append(char)

            if banned_found:
                print(
                    f"⚠️  Warning: Result contains banned characters: {', '.join(banned_found)}")
            else:
                print("✅ Success: No banned characters found")

        except Exception as e:
            print(f"❌ Error: {e}")

        print("=" * 40)

    print("✅ Simple lipogram test completed\n")


def test_bert_similarity():
    """Test BERT similarity calculation."""
    print("🧪 Testing BERT Similarity")
    print("=" * 40)

    rewriter = EnglishBertRewriter("bert-base-uncased")

    # Test word pairs
    word_pairs = [
        ("cat", "feline"),
        ("quick", "fast"),
        ("jump", "leap"),
        ("house", "home"),
        ("car", "vehicle")
    ]

    context = "The animal moved quickly across the yard."

    for word1, word2 in word_pairs:
        try:
            # Get embeddings
            emb1 = rewriter.get_word_embedding(word1, context)
            emb2 = rewriter.get_word_embedding(word2, context)

            # Calculate similarity
            from sklearn.metrics.pairwise import cosine_similarity
            import numpy as np

            similarity = cosine_similarity(
                emb1.reshape(1, -1),
                emb2.reshape(1, -1)
            )[0][0]

            print(f"'{word1}' vs '{word2}': {similarity:.3f}")

        except Exception as e:
            print(f"Error with '{word1}' vs '{word2}': {e}")

    print("✅ BERT similarity test completed\n")


def test_wordnet_synonyms():
    """Test WordNet synonym retrieval."""
    print("🧪 Testing WordNet Synonyms")
    print("=" * 40)

    tokenizer = EnglishTokenizer()

    test_words = [
        ("happy", "ADJ"),
        ("run", "VERB"),
        ("dog", "NOUN"),
        ("quickly", "ADV"),
        ("beautiful", "ADJ")
    ]

    for word, pos in test_words:
        synonyms = tokenizer.get_synonyms(word, pos)
        print(f"'{word}' ({pos}): {synonyms[:8]}")  # Show first 8 synonyms

    print("✅ WordNet synonyms test completed\n")


def interactive_test():
    """Interactive test mode."""
    print("🎯 Interactive English Lipogram Test")
    print("=" * 40)

    rewriter = EnglishBertRewriter("bert-base-uncased")

    while True:
        print("\nEnter text to convert (or 'quit' to exit):")
        text = input("> ").strip()

        if text.lower() in ['quit', 'exit', 'q']:
            break

        if not text:
            continue

        print("Enter banned characters (space-separated):")
        banned_input = input("> ").strip()

        if not banned_input:
            continue

        banned_chars = banned_input.split()

        print("Show detailed output? (y/n):")
        verbose = input("> ").strip().lower() in ['y', 'yes']

        try:
            result = rewriter.rewrite_text(text, banned_chars, 0.4, verbose)
            print(f"\n✨ Result: {result}")
        except Exception as e:
            print(f"❌ Error: {e}")


def main():
    """Main test function."""
    print("🚀 English Lipogram Generator Test Suite")
    print("=" * 50)

    # Check if required packages are available
    try:
        import torch
        import transformers
        import nltk
        import spacy
        import sklearn
        print("✅ All required packages are available")
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("Please install required packages:")
        print("pip install torch transformers nltk spacy scikit-learn")
        print("python -m spacy download en_core_web_sm")
        return

    print("\nSelect test to run:")
    print("1. English Tokenizer Test")
    print("2. Simple Lipogram Generation Test")
    print("3. BERT Similarity Test")
    print("4. WordNet Synonyms Test")
    print("5. Interactive Test")
    print("6. Run All Tests")

    choice = input("\nEnter choice (1-6): ").strip()

    if choice == "1":
        test_english_tokenizer()
    elif choice == "2":
        test_simple_lipogram()
    elif choice == "3":
        test_bert_similarity()
    elif choice == "4":
        test_wordnet_synonyms()
    elif choice == "5":
        interactive_test()
    elif choice == "6":
        test_english_tokenizer()
        test_wordnet_synonyms()
        test_bert_similarity()
        test_simple_lipogram()
    else:
        print("Invalid choice. Please run the script again.")


if __name__ == "__main__":
    main()
