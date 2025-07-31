"""
BERT-based English lipogram rewriter using transformers and WordNet.
"""

import torch
from transformers import AutoTokenizer, AutoModel
from typing import List, Tuple, Set, Optional
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from .english_tokenizer import EnglishTokenizer
from .utils import contains_banned


class EnglishBertRewriter:
    """BERT-based English lipogram rewriter using semantic similarity."""

    def __init__(self, model_name: str = "bert-base-uncased"):
        """
        Initialize the BERT-based rewriter.

        Args:
            model_name: BERT model name from Hugging Face
        """
        self.model_name = model_name
        self.tokenizer_bert = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.english_tokenizer = EnglishTokenizer()

        # Set model to evaluation mode
        self.model.eval()

    def get_word_embedding(self, word: str, context: str = "") -> np.ndarray:
        """
        Get BERT embedding for a word in context.

        Args:
            word: Target word
            context: Context sentence

        Returns:
            Word embedding vector
        """
        if context:
            # Use context for better embeddings
            text = context
        else:
            text = word

        # Tokenize and encode
        inputs = self.tokenizer_bert(
            text, return_tensors="pt", padding=True, truncation=True)

        with torch.no_grad():
            outputs = self.model(**inputs)
            # Use the mean of the last hidden state as word representation
            embeddings = outputs.last_hidden_state.mean(dim=1)

        return embeddings.numpy().flatten()

    def find_best_synonym(
        self,
        original_word: str,
        context: str,
        banned_chars: List[str],
        failed_attempts: Optional[List[str]] = None,
        pos_tag: str = None
    ) -> Tuple[str, float]:
        """
        Find the best synonym using BERT similarity and WordNet.

        Args:
            original_word: Original word to replace
            context: Context sentence
            banned_chars: List of banned characters
            failed_attempts: Previously failed attempts
            pos_tag: Part-of-speech tag

        Returns:
            Tuple of (best_synonym, similarity_score)
        """
        if failed_attempts is None:
            failed_attempts = []

        # Get synonyms from WordNet
        synonyms = self.english_tokenizer.get_synonyms(original_word, pos_tag)

        # Add common replacements for function words
        common_replacements = {
            'the': ['a', 'this', 'that', 'such'],
            'how': ['what', 'why', 'when'],
            'you': ['we', 'they', 'people'],
            'today': ['now', 'currently', 'this day', 'present'],
            'world': ['earth', 'planet', 'globe', 'universe'],
            'hello': ['hi', 'hey', 'greetings'],
            'and': ['plus', 'with', 'also'],
            'or': ['either', 'maybe'],
            'to': ['toward', 'into'],
            'of': ['from', 'about'],
            'in': ['at', 'on', 'within'],
            'for': ['toward', 'about'],
            'with': ['using', 'via'],
            'by': ['via', 'through'],
            'programming': ['coding', 'development', 'software'],
            'artificial': ['fake', 'synthetic', 'man-made'],
            'intelligence': ['smarts', 'brains', 'wisdom']
        }

        # Add common replacements if available
        if original_word.lower() in common_replacements:
            synonyms.extend(common_replacements[original_word.lower()])

        # Remove duplicates
        synonyms = list(set(synonyms))

        if not synonyms:
            return original_word, 0.0

        # Filter out banned words and failed attempts
        valid_synonyms = []
        for synonym in synonyms:
            # Check if synonym contains banned characters
            if not contains_banned(synonym.lower(), [c.lower() for c in banned_chars]):
                # Check if not in failed attempts
                if synonym.lower() not in [attempt.lower() for attempt in failed_attempts]:
                    valid_synonyms.append(synonym)

        if not valid_synonyms:
            return original_word, 0.0

        # Get BERT embedding for original word in context
        original_embedding = self.get_word_embedding(original_word, context)

        best_synonym = original_word
        best_similarity = 0.0

        # Calculate similarity for each valid synonym
        for synonym in valid_synonyms:
            try:
                # Create context with synonym for better embedding
                synonym_context = context.replace(original_word, synonym, 1)
                synonym_embedding = self.get_word_embedding(
                    synonym, synonym_context)

                # Calculate cosine similarity
                similarity = cosine_similarity(
                    original_embedding.reshape(1, -1),
                    synonym_embedding.reshape(1, -1)
                )[0][0]

                if similarity > best_similarity:
                    best_similarity = similarity
                    best_synonym = synonym

            except Exception as e:
                print(f"Error calculating similarity for {synonym}: {e}")
                continue

        return best_synonym, best_similarity

    def rewrite_sentence(
        self,
        sentence: str,
        banned_chars: List[str],
        similarity_threshold: float = 0.5,
        verbose: bool = False
    ) -> str:
        """
        Rewrite a sentence to avoid banned characters using BERT + WordNet.

        Args:
            sentence: Input sentence
            banned_chars: List of banned characters
            similarity_threshold: Minimum similarity threshold for replacements
            verbose: Whether to print detailed output

        Returns:
            Rewritten sentence
        """
        tokens = self.english_tokenizer.tokenize(sentence)
        new_tokens = []

        if verbose:
            print(f"\n📝 Processing sentence: {sentence}")
            print("-" * 50)

        for i, token_info in enumerate(tokens):
            surface = token_info['surface']
            phonetic = token_info['phonetic']
            pos = token_info['pos']

            if verbose:
                print(f"Token [{i+1}/{len(tokens)}]: {surface} (POS: {pos})")

            # Check if token contains banned characters
            if contains_banned(surface.lower(), [c.lower() for c in banned_chars]):
                if verbose:
                    print(f"❌ Contains banned characters: {surface}")

                # Try to find replacement using BERT + WordNet
                failed_attempts = []
                replacement = surface
                best_similarity = 0.0

                max_retries = 3
                for retry in range(max_retries):
                    if verbose and retry > 0:
                        print(
                            f"   🔄 Retry {retry}: Failed attempts: {failed_attempts}")

                    candidate, similarity = self.find_best_synonym(
                        surface, sentence, banned_chars, failed_attempts, pos
                    )

                    if candidate != surface and similarity >= similarity_threshold:
                        # Check if candidate is valid
                        if not contains_banned(candidate.lower(), [c.lower() for c in banned_chars]):
                            replacement = candidate
                            best_similarity = similarity
                            if verbose:
                                print(
                                    f"   ✅ Found replacement: {surface} → {replacement} (similarity: {similarity:.3f})")
                            break
                        else:
                            failed_attempts.append(candidate)
                            if verbose:
                                print(
                                    f"   ❌ Candidate still contains banned chars: {candidate}")
                    else:
                        if candidate != surface:
                            failed_attempts.append(candidate)
                        if verbose:
                            print(
                                f"   ⚠️  Low similarity or no candidate: {similarity:.3f}")

                if replacement == surface and verbose:
                    print(f"   ⚠️  No valid replacement found for: {surface}")

                new_tokens.append(replacement)
            else:
                if verbose:
                    print(f"✅ Keeping: {surface}")
                new_tokens.append(surface)

        # Reconstruct sentence with proper spacing
        result = self._reconstruct_sentence(sentence, tokens, new_tokens)

        if verbose:
            print(f"\n🟢 Result: {result}")

        return result

    def _reconstruct_sentence(self, original: str, tokens: List[dict], new_tokens: List[str]) -> str:
        """
        Reconstruct sentence maintaining original spacing and punctuation.

        Args:
            original: Original sentence
            tokens: Original token information
            new_tokens: New token surfaces

        Returns:
            Reconstructed sentence
        """
        if len(tokens) != len(new_tokens):
            # Fallback: simple join
            return " ".join(new_tokens)

        result = original
        offset = 0

        # Replace tokens in reverse order to maintain positions
        for i in range(len(tokens) - 1, -1, -1):
            token_info = tokens[i]
            original_surface = token_info['surface']
            new_surface = new_tokens[i]

            if original_surface != new_surface:
                # Find the position of this token in the original sentence
                start_pos = result.lower().find(original_surface.lower(), offset)
                if start_pos != -1:
                    end_pos = start_pos + len(original_surface)
                    result = result[:start_pos] + \
                        new_surface + result[end_pos:]

        return result

    def rewrite_text(
        self,
        text: str,
        banned_chars: List[str],
        similarity_threshold: float = 0.5,
        verbose: bool = False
    ) -> str:
        """
        Rewrite entire text to avoid banned characters.

        Args:
            text: Input text
            banned_chars: List of banned characters
            similarity_threshold: Minimum similarity threshold for replacements
            verbose: Whether to print detailed output

        Returns:
            Rewritten text
        """
        # Split text into sentences
        sentences = self._split_sentences(text)
        rewritten_sentences = []

        if verbose:
            print(f"\n🔵 Processing {len(sentences)} sentences")
            print("=" * 60)

        for i, sentence in enumerate(sentences):
            if verbose and len(sentences) > 1:
                print(f"\n📄 Sentence {i+1}/{len(sentences)}")

            rewritten = self.rewrite_sentence(
                sentence, banned_chars, similarity_threshold, verbose
            )
            rewritten_sentences.append(rewritten)

            if verbose and len(sentences) > 1:
                print("=" * 60)

        return " ".join(rewritten_sentences)

    def _split_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences.

        Args:
            text: Input text

        Returns:
            List of sentences
        """
        # Simple sentence splitting for English
        import re
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
