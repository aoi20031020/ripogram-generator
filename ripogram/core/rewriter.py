"""
OpenAI GPT-4 based word rewriter for ripogram generation.
"""

import re
from typing import List, Set, Tuple, Optional
from openai import OpenAI
from .tokenizer import JapaneseTokenizer
from .utils import contains_banned


class RipogramRewriter:
    """Rewrite Japanese text to avoid banned characters using OpenAI GPT-4."""
    
    def __init__(self, api_key: str, model_name: str = "gpt-4"):
        """
        Initialize the rewriter.
        
        Args:
            api_key: OpenAI API key
            model_name: OpenAI model name (default: gpt-4)
        """
        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name
        self.tokenizer = JapaneseTokenizer()
    
    def split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences based on Japanese punctuation.
        
        Args:
            text: Input text to split
            
        Returns:
            List of sentences
        """
        # Split by Japanese sentence endings (。！？)
        sentences = re.split(r'([。！？])', text)
        
        # Recombine sentences with their punctuation
        result = []
        for i in range(0, len(sentences) - 1, 2):
            if i + 1 < len(sentences):
                sentence = sentences[i] + sentences[i + 1]
                if sentence.strip():
                    result.append(sentence)
        
        # Handle case where text doesn't end with punctuation
        if len(sentences) % 2 == 1 and sentences[-1].strip():
            result.append(sentences[-1])
        
        return result
    
    def rewrite_token_with_context(
        self, 
        original_word: str, 
        current_sentence: str,
        full_text: str,
        banned_chars: List[str],
        failed_attempts: Optional[List[str]] = None,
        pos: str = "名詞",
        max_attempts: int = 10
    ) -> Tuple[str, str]:
        """
        Rewrite a single token using enhanced context information.
        
        Args:
            original_word: Original word to replace
            current_sentence: The sentence containing the word
            full_text: The complete text for broader context
            banned_chars: List of banned characters
            failed_attempts: List of previously failed replacement attempts
            pos: Part of speech
            max_attempts: Maximum retry attempts
            
        Returns:
            Tuple of (replacement_word, replacement_reading)
        """
        if failed_attempts is None:
            failed_attempts = []
        
        for attempt in range(max_attempts):
            # Build enhanced prompt with full context
            base_prompt = f"""
以下の単語「{original_word}」は、禁止文字「{'、'.join(banned_chars)}」を含むため、文脈に合った自然な表現に**単語単位**で言い換えてください。

【日本語リポグラムのルール】
・禁止文字「{'、'.join(banned_chars)}」は**読み（ひらがな）**での使用が禁止されています
・変換後の単語を**ひらがなで読んだ時**に禁止文字が一文字でも含まれてはいけません
・例：「猫」（ねこ）が禁止なら「ネコ科」（ねこか）も「ね」「こ」を含むため禁止です

【文脈情報】
・全体の文章：「{full_text}」
・現在の文：「{current_sentence}」
・対象の単語：「{original_word}」
・品詞：「{pos}」

【重要】
・文全体の意味と流れを保持してください
・文法的に自然な表現を選んでください
・変換後の単語の読み（ひらがな）に禁止文字「{'、'.join(banned_chars)}」が**一文字も含まれない**こと
"""
            
            # Add failed attempts information if any
            if failed_attempts:
                base_prompt += f"""
・以下の候補は既に試行済みで使用できません：「{'」「'.join(failed_attempts)}」
・これらとは**全く異なる**新しい表現を考えてください。
"""
            
            # Add strategy based on attempt number
            if attempt < 3:
                strategy = "・文脈に最も適した同義語や類義語で言い換えてください。"
            elif attempt < 6:
                strategy = "・より広い概念や上位概念で、文の流れを保つ表現を選んでください。"
            else:
                strategy = "・文脈に応じた意訳や、文全体の意味を保つ別の表現方法を試してください。"
            
            prompt = base_prompt + strategy + """
・出力は置き換えた語句 **一単語のみ** にしてください。
・絶対に説明文や補足は付けず、単語だけを出力してください。
"""
            
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.5,
                    max_tokens=100
                )
                
                candidate = response.choices[0].message.content
                if candidate is None:
                    continue
                candidate = candidate.strip()
                
                # Clean up the candidate (remove quotes, parentheses, etc.)
                candidate = re.sub(
                    r'[「」『』"\'（）()［］\[\]]', '', candidate
                ).split()[0]
                
                # Tokenize the candidate to get its reading
                candidate_tokens = self.tokenizer.tokenize(candidate)
                if candidate_tokens:
                    # Get the full reading by concatenating all token readings
                    candidate_reading = ''.join([token['reading'] for token in candidate_tokens])
                    
                    # Check if candidate is valid (no banned characters)
                    if (not contains_banned(candidate, banned_chars) and
                            not contains_banned(candidate_reading, banned_chars)):
                        return candidate, candidate_reading
                    else:
                        # Add failed candidate to history for next attempt
                        if candidate not in failed_attempts:
                            failed_attempts.append(candidate)
                        
            except Exception as e:
                print(f"[API Error] Attempt {attempt + 1}: {e}")
                continue
        
        # Fallback: return original word if all attempts fail
        original_tokens = self.tokenizer.tokenize(original_word)
        original_reading = (original_tokens[0]['reading']
                            if original_tokens else original_word)
        return original_word, original_reading
    
    def rewrite_text_with_context(
        self, 
        text: str, 
        banned_chars: List[str],
        verbose: bool = False
    ) -> str:
        """
        Rewrite text using sentence-level context for improved accuracy.
        
        Args:
            text: Input text to rewrite
            banned_chars: List of banned characters
            verbose: Whether to print detailed output
            
        Returns:
            Rewritten text
        """
        sentences = self.split_into_sentences(text)
        rewritten_sentences = []
        
        for i, sentence in enumerate(sentences):
            if verbose:
                print(f"\n📝 文 {i+1}: {sentence}")
                print("-" * 50)
            
            tokens = self.tokenizer.tokenize(sentence)
            new_tokens = []
            
            for token_info in tokens:
                surface = token_info['surface']
                reading = token_info['reading']
                pos = token_info['pos']
                
                if verbose:
                    print(f"トークン：{surface}（読み：{reading}）")
                
                # Check if token contains banned characters
                if (contains_banned(surface, banned_chars) or
                        contains_banned(reading, banned_chars)):
                    
                    if verbose:
                        print(f"❌ 禁止文字を含む：{surface}（読み：{reading}）")
                    
                    # Track failed attempts for this token
                    failed_attempts: List[str] = []
                    replacement = surface
                    replacement_reading = reading
                    
                    # Try to rewrite the token with enhanced context
                    max_retries = 5
                    for retry in range(max_retries):
                        if verbose and retry > 0:
                            print(f"   🔄 再試行 {retry}: 失敗履歴 {failed_attempts}")
                        
                        replacement, replacement_reading = self.rewrite_token_with_context(
                            surface, sentence, text, banned_chars, failed_attempts.copy(), pos
                        )
                        
                        # Check if replacement is valid
                        surface_has_banned = contains_banned(replacement, banned_chars)
                        reading_has_banned = contains_banned(replacement_reading, banned_chars)
                        
                        if not surface_has_banned and not reading_has_banned:
                            # Success! Break out of retry loop
                            break
                        else:
                            # Always add failed attempt to history (avoid duplicates)
                            if replacement not in failed_attempts:
                                failed_attempts.append(replacement)
                            if verbose:
                                print(f"   ❌ 失敗: 「{replacement}」を履歴に追加")
                    
                    if verbose:
                        # Check if replacement still contains banned characters
                        surface_has_banned = contains_banned(replacement, banned_chars)
                        reading_has_banned = contains_banned(replacement_reading, banned_chars)
                        
                        if surface_has_banned or reading_has_banned:
                            print(f"⚠️  「{surface}」→「{replacement}」（読み：{replacement_reading}）")
                            if surface_has_banned:
                                print(f"   表記に禁止文字が含まれています: {replacement}")
                            if reading_has_banned:
                                # Show detailed reading analysis
                                banned_in_reading = [char for char in banned_chars if char in replacement_reading]
                                print(f"   読みに禁止文字が含まれています: {replacement_reading}")
                                print(f"   検出された禁止文字: {banned_in_reading}")
                        else:
                            print(f"👉 「{surface}」→「{replacement}」（読み：{replacement_reading}）")
                    
                    new_tokens.append(replacement)
                else:
                    new_tokens.append(surface)
            
            rewritten_sentence = ''.join(new_tokens)
            rewritten_sentences.append(rewritten_sentence)
            
            if verbose:
                print(f"🟢 変換後の文: {rewritten_sentence}")
        
        return ''.join(rewritten_sentences)
    
    def rewrite_token(
        self, 
        original_word: str, 
        context: str, 
        banned_chars: List[str],
        failed_attempts: Optional[List[str]] = None,
        pos: str = "名詞",
        max_attempts: int = 10
    ) -> Tuple[str, str]:
        """
        Rewrite a single token using OpenAI GPT-4 with failure history.
        
        Args:
            original_word: Original word to replace
            context: Sentence context
            banned_chars: List of banned characters
            failed_attempts: List of previously failed replacement attempts
            pos: Part of speech
            max_attempts: Maximum retry attempts
            
        Returns:
            Tuple of (replacement_word, replacement_reading)
        """
        if failed_attempts is None:
            failed_attempts = []
        
        for attempt in range(max_attempts):
            # Build dynamic prompt based on attempt number and failed history
            base_prompt = f"""
以下の単語「{original_word}」は、禁止文字「{'、'.join(banned_chars)}」を含むため、文脈に合った自然な表現に**単語単位**で言い換えてください。

【日本語リポグラムのルール】
・禁止文字「{'、'.join(banned_chars)}」は**読み（ひらがな）**での使用が禁止されています
・変換後の単語を**ひらがなで読んだ時**に禁止文字が一文字でも含まれてはいけません
・例：「猫」（ねこ）が禁止なら「ネコ科」（ねこか）も「ね」「こ」を含むため禁止です

・文の文脈：「{context}」
・対象の単語：「{original_word}」
・品詞：「{pos}」
・変換後の単語の読み（ひらがな）に禁止文字「{'、'.join(banned_chars)}」が**一文字も含まれない**こと
"""
            
            # Add failed attempts information if any
            if failed_attempts:
                base_prompt += f"""
・以下の候補は既に試行済みで使用できません：「{'」「'.join(failed_attempts)}」
・これらとは**全く異なる**新しい表現を考えてください。
"""
            
            # Add strategy based on attempt number
            if attempt < 3:
                strategy = "・直接的な同義語や類義語で言い換えてください。"
            elif attempt < 6:
                strategy = "・より広い概念や上位概念で言い換えてください。"
            else:
                strategy = "・文脈に応じた意訳や別の表現方法を試してください。"
            
            prompt = base_prompt + strategy + """
・出力は置き換えた語句 **一単語のみ** にしてください。
・絶対に説明文や補足は付けず、単語だけを出力してください。
"""
            
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.5,
                    max_tokens=100
                )
                
                candidate = response.choices[0].message.content
                if candidate is None:
                    continue
                candidate = candidate.strip()
                
                # Clean up the candidate (remove quotes, parentheses, etc.)
                candidate = re.sub(
                    r'[「」『』"\'（）()［］\[\]]', '', candidate
                ).split()[0]
                
                # Tokenize the candidate to get its reading
                candidate_tokens = self.tokenizer.tokenize(candidate)
                if candidate_tokens:
                    # Get the full reading by concatenating all token readings
                    candidate_reading = ''.join([token['reading'] for token in candidate_tokens])
                    
                    # Check if candidate is valid (no banned characters)
                    if (not contains_banned(candidate, banned_chars) and
                            not contains_banned(candidate_reading, banned_chars)):
                        return candidate, candidate_reading
                    else:
                        # Add failed candidate to history for next attempt
                        if candidate not in failed_attempts:
                            failed_attempts.append(candidate)
                        
            except Exception as e:
                print(f"[API Error] Attempt {attempt + 1}: {e}")
                continue
        
        # Fallback: return original word if all attempts fail
        original_tokens = self.tokenizer.tokenize(original_word)
        original_reading = (original_tokens[0]['reading']
                            if original_tokens else original_word)
        return original_word, original_reading
    
    def rewrite_sentence(
        self, 
        sentence: str, 
        banned_chars: List[str],
        verbose: bool = False
    ) -> str:
        """
        Rewrite a sentence to avoid banned characters.
        
        Args:
            sentence: Input sentence
            banned_chars: List of banned characters
            verbose: Whether to print detailed output
            
        Returns:
            Rewritten sentence
        """
        tokens = self.tokenizer.tokenize(sentence)
        new_tokens = []
        previous_replacements: Set[str] = set()
        
        for token_info in tokens:
            surface = token_info['surface']
            reading = token_info['reading']
            pos = token_info['pos']
            
            if verbose:
                print(f"トークン：{surface}（読み：{reading}）")
            
            # Check if token contains banned characters
            if (contains_banned(surface, banned_chars) or
                    contains_banned(reading, banned_chars)):
                
                if verbose:
                    print(f"❌ 禁止文字を含む：{surface}"
                          f"（読み：{reading}）")
                
                # Track failed attempts for this token
                failed_attempts: List[str] = []
                replacement = surface
                replacement_reading = reading
                
                # Try to rewrite the token with failure history
                max_retries = 5
                for retry in range(max_retries):
                    if verbose and retry > 0:
                        print(f"   🔄 再試行 {retry}: 失敗履歴 {failed_attempts}")
                    
                    replacement, replacement_reading = self.rewrite_token(
                        surface, sentence, banned_chars, failed_attempts.copy(), pos
                    )
                    
                    # Check if replacement is valid
                    surface_has_banned = contains_banned(replacement, banned_chars)
                    reading_has_banned = contains_banned(replacement_reading, banned_chars)
                    
                    if not surface_has_banned and not reading_has_banned:
                        # Success! Break out of retry loop
                        break
                    else:
                        # Always add failed attempt to history (avoid duplicates)
                        if replacement not in failed_attempts:
                            failed_attempts.append(replacement)
                        if verbose:
                            print(f"   ❌ 失敗: 「{replacement}」を履歴に追加")
                
                if verbose:
                    # Check if replacement still contains banned characters
                    surface_has_banned = contains_banned(replacement, banned_chars)
                    reading_has_banned = contains_banned(replacement_reading, banned_chars)
                    
                    if surface_has_banned or reading_has_banned:
                        print(f"⚠️  「{surface}」→「{replacement}」"
                              f"（読み：{replacement_reading}）")
                        if surface_has_banned:
                            print(f"   表記に禁止文字が含まれています: {replacement}")
                        if reading_has_banned:
                            # Show detailed reading analysis
                            banned_in_reading = [char for char in banned_chars if char in replacement_reading]
                            print(f"   読みに禁止文字が含まれています: {replacement_reading}")
                            print(f"   検出された禁止文字: {banned_in_reading}")
                    else:
                        print(f"👉 「{surface}」→「{replacement}」"
                              f"（読み：{replacement_reading}）")
                
                new_tokens.append(replacement)
                previous_replacements.add(replacement)
            else:
                new_tokens.append(surface)
        
        return ''.join(new_tokens)
