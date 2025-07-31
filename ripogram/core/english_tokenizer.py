"""
English tokenization module using NLTK and spaCy.
"""

import nltk
import spacy
from typing import List, Dict
from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')


class EnglishTokenizer:
    """English tokenizer using NLTK and spaCy."""

    def __init__(self):
        """Initialize the tokenizer with spaCy and NLTK."""
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Warning: spaCy English model not found. Please install with: python -m spacy download en_core_web_sm")
            self.nlp = None

    def get_phonetic_representation(self, word: str) -> str:
        """
        Get phonetic representation of a word.
        For simplicity, we'll use the word itself as English doesn't have
        the same reading complexity as Japanese.

        Args:
            word: Input word

        Returns:
            Phonetic representation (lowercase)
        """
        return word.lower()

    def get_pos_tag(self, word: str, context: str = "") -> str:
        """
        Get part-of-speech tag for a word.

        Args:
            word: Input word
            context: Context sentence for better POS tagging

        Returns:
            POS tag
        """
        if self.nlp and context:
            # Use spaCy for better context-aware POS tagging
            doc = self.nlp(context)
            for token in doc:
                if token.text.lower() == word.lower():
                    return token.pos_

        # Fallback to NLTK
        tokens = word_tokenize(word)
        pos_tags = pos_tag(tokens)
        return pos_tags[0][1] if pos_tags else "NN"

    def tokenize(self, sentence: str) -> List[Dict]:
        """
        Tokenize an English sentence.

        Args:
            sentence: Input English sentence

        Returns:
            List of token dictionaries with surface, phonetic, and pos
        """
        tokens = []

        if self.nlp:
            # Use spaCy for better tokenization
            doc = self.nlp(sentence)
            for token in doc:
                if not token.is_space and not token.is_punct:
                    tokens.append({
                        'surface': token.text,
                        'phonetic': self.get_phonetic_representation(token.text),
                        'pos': token.pos_,
                        'lemma': token.lemma_,
                        'token': token
                    })
        else:
            # Fallback to NLTK
            word_tokens = word_tokenize(sentence)
            pos_tags = pos_tag(word_tokens)

            for word, pos in pos_tags:
                if word.isalpha():  # Only include alphabetic tokens
                    tokens.append({
                        'surface': word,
                        'phonetic': self.get_phonetic_representation(word),
                        'pos': pos,
                        'lemma': word.lower(),
                        'token': None
                    })

        return tokens

    def get_synonyms(self, word: str, pos_tag: str = None) -> List[str]:
        """
        Get synonyms for a word using WordNet.

        Args:
            word: Input word
            pos_tag: Part-of-speech tag to filter synonyms

        Returns:
            List of synonyms
        """
        synonyms = set()

        # Convert POS tag to WordNet format
        wordnet_pos = self._convert_pos_to_wordnet(
            pos_tag) if pos_tag else None

        # Get synsets for the word
        synsets = wordnet.synsets(word, pos=wordnet_pos)

        for synset in synsets:
            for lemma in synset.lemmas():
                synonym = lemma.name().replace('_', ' ')
                if synonym.lower() != word.lower():
                    synonyms.add(synonym)

        return list(synonyms)

    def _convert_pos_to_wordnet(self, pos_tag: str) -> str:
        """
        Convert POS tag to WordNet format.

        Args:
            pos_tag: POS tag from spaCy or NLTK

        Returns:
            WordNet POS tag
        """
        if not pos_tag:
            return wordnet.NOUN

        pos_tag = pos_tag.upper()

        if pos_tag.startswith('N') or pos_tag == 'NOUN':
            return wordnet.NOUN
        elif pos_tag.startswith('V') or pos_tag == 'VERB':
            return wordnet.VERB
        elif pos_tag.startswith('J') or pos_tag == 'ADJ':
            return wordnet.ADJ
        elif pos_tag.startswith('R') or pos_tag == 'ADV':
            return wordnet.ADV
        else:
            return wordnet.NOUN
