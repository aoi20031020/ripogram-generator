"""
Metrics utilities for evaluating Japanese lipogram generation.

This module intentionally contains no network calls and depends only on the
local tokenizer (fugashi/UniDic via JapaneseTokenizer).

Provided metrics (unweighted):

- Constraint check (reading-based): detects banned kana in reading.
- VRR (Vocabulary Replacement Rate): replaced_tokens / total_tokens.
- TTR (Type-Token Ratio): unique_tokens / total_tokens.
- N-gram repetition rate: proportion of repeated n-grams.
- Runtime measurement helper.

Notes
-----
- "Reading" refers to per-token reading (hiragana). We convert katakana to
  hiragana via existing utility so that banned kana detection is consistent.
- For VRR, we provide a robust implementation using LCS (Longest Common
  Subsequence) over token surfaces to handle insertions/deletions in the
  rewritten text. If token lengths match, a positional comparison is used.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Tuple, Iterable, Optional
from time import perf_counter

from .core.tokenizer import JapaneseTokenizer


# -----------------------------
# Utility dataclasses
# -----------------------------

@dataclass
class ConstraintCheckResult:
    """Result of constraint checking.

    Attributes:
        violated: True if any banned kana is found according to the chosen mode.
        found: A list of banned kana actually found (unique, order preserved).
        count: The total count of banned kana occurrences in the analyzed string.
        mode: 'reading' or 'surface' indicating the basis of detection.
    """

    violated: bool
    found: List[str]
    count: int
    mode: str


# -----------------------------
# Token helpers
# -----------------------------

def _get_tokenizer(tokenizer: Optional[JapaneseTokenizer]) -> JapaneseTokenizer:
    """Return a provided tokenizer or instantiate a default one."""
    return tokenizer if tokenizer is not None else JapaneseTokenizer()


def tokenize_japanese(text: str, tokenizer: Optional[JapaneseTokenizer] = None) -> List[Dict]:
    """Tokenize Japanese text using the project tokenizer.

    Returns list of dicts with keys: 'surface', 'reading', 'pos'.
    """
    tk = _get_tokenizer(tokenizer)
    return tk.tokenize(text)


def _is_content_token(token: Dict) -> bool:
    """Heuristic to exclude symbols/punctuation from counts.

    UniDic pos1="記号" is treated as punctuation. We also exclude whitespace.
    """
    surface = token.get("surface", "")
    pos = token.get("pos", "")
    if not surface or not surface.strip():
        return False
    if pos == "記号":
        return False
    return True


def content_tokens(tokens: Iterable[Dict]) -> List[Dict]:
    """Filter out punctuation/whitespace tokens."""
    return [t for t in tokens if _is_content_token(t)]


# -----------------------------
# Constraint checking
# -----------------------------

def extract_reading(text: str, tokenizer: Optional[JapaneseTokenizer] = None) -> str:
    """Concatenate per-token readings (hiragana) for the whole text."""
    tokens = tokenize_japanese(text, tokenizer)
    return "".join(t.get("reading", t.get("surface", "")) for t in tokens)


def check_constraint(
    text: str,
    banned_kana: List[str],
    tokenizer: Optional[JapaneseTokenizer] = None,
    mode: str = "reading",
) -> ConstraintCheckResult:
    """Check constraint adherence for a text.

    Args:
        text: Input Japanese text.
        banned_kana: List of banned kana (e.g., ['あ','い']). For 行禁止は
            事前に列挙展開したリストを渡してください。
        tokenizer: Optional tokenizer instance.
        mode: 'reading' (default) uses concatenated token readings; 'surface'
            checks the surface string as-is.

    Returns:
        ConstraintCheckResult with violation details.
    """
    if mode not in {"reading", "surface"}:
        raise ValueError("mode must be 'reading' or 'surface'")

    basis = extract_reading(text, tokenizer) if mode == "reading" else text

    found: List[str] = []
    total = 0
    for ch in banned_kana:
        c = basis.count(ch)
        if c > 0:
            found.append(ch)
            total += c

    return ConstraintCheckResult(
        violated=total > 0,
        found=found,
        count=total,
        mode=mode,
    )


# -----------------------------
# VRR (Vocabulary Replacement Rate)
# -----------------------------

def _lcs_length(a: List[str], b: List[str]) -> int:
    """Compute length of LCS between two token sequences (O(n*m))."""
    n, m = len(a), len(b)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        ai = a[i - 1]
        row = dp[i]
        prev_row = dp[i - 1]
        for j in range(1, m + 1):
            if ai == b[j - 1]:
                row[j] = prev_row[j - 1] + 1
            else:
                row[j] = row[j - 1] if row[j - 1] >= prev_row[j] else prev_row[j]
    return dp[n][m]


def compute_vrr(
    original_text: str,
    rewritten_text: str,
    tokenizer: Optional[JapaneseTokenizer] = None,
) -> float:
    """Compute unweighted VRR = replaced_tokens / total_tokens.

    Tokenization is performed for both original and rewritten texts after
    removing punctuation tokens. If token lengths match, a positional
    comparison is used. Otherwise, we approximate replacements via
    1 - LCS_len / len(original_tokens).

    Returns 0.0 when the original has no valid tokens.
    """
    tk = _get_tokenizer(tokenizer)
    orig_tokens = content_tokens(tk.tokenize(original_text))
    rew_tokens = content_tokens(tk.tokenize(rewritten_text))

    orig_surfaces = [t["surface"] for t in orig_tokens]
    rew_surfaces = [t["surface"] for t in rew_tokens]

    total = len(orig_surfaces)
    if total == 0:
        return 0.0

    if len(orig_surfaces) == len(rew_surfaces):
        replaced = sum(1 for o, r in zip(orig_surfaces, rew_surfaces) if o != r)
        return replaced / total

    # Robust fallback: use LCS length to estimate common kept tokens
    lcs_len = _lcs_length(orig_surfaces, rew_surfaces)
    replaced = max(total - lcs_len, 0)
    return replaced / total


# -----------------------------
# Diversity metrics
# -----------------------------

def compute_ttr(text: str, tokenizer: Optional[JapaneseTokenizer] = None) -> float:
    """Compute Type-Token Ratio (unique_surfaces / total_surfaces)."""
    tokens = content_tokens(tokenize_japanese(text, tokenizer))
    surfaces = [t["surface"] for t in tokens]
    total = len(surfaces)
    if total == 0:
        return 0.0
    unique = len(set(surfaces))
    return unique / total


def ngram_repetition_rate(
    text: str, n: int = 2, tokenizer: Optional[JapaneseTokenizer] = None
) -> float:
    """Compute proportion of repeated n-grams in a text.

    We count repeated n-grams beyond their first occurrence:
        sum(max(count(ng)-1, 0)) / total_n_grams
    Returns 0.0 if fewer than n tokens are available.
    """
    tokens = content_tokens(tokenize_japanese(text, tokenizer))
    surfaces = [t["surface"] for t in tokens]
    if len(surfaces) < n:
        return 0.0

    # Build n-grams
    ngrams: List[Tuple[str, ...]] = [
        tuple(surfaces[i : i + n]) for i in range(len(surfaces) - n + 1)
    ]

    total = len(ngrams)
    counts: Dict[Tuple[str, ...], int] = {}
    for ng in ngrams:
        counts[ng] = counts.get(ng, 0) + 1

    repeated = sum(c - 1 for c in counts.values() if c > 1)
    return repeated / total if total > 0 else 0.0


# -----------------------------
# Timing helper
# -----------------------------

def measure_time(fn, *args, **kwargs) -> Tuple[float, object]:
    """Measure execution time of a callable.

    Returns (elapsed_seconds, result)
    """
    start = perf_counter()
    result = fn(*args, **kwargs)
    end = perf_counter()
    return end - start, result


__all__ = [
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

