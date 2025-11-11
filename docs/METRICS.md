# Metrics for Japanese Lipogram Evaluation

This document describes the unweighted metrics implemented in `ripogram/metrics.py` for evaluating Japanese lipogram generation.

## Overview

- Constraint check (reading-based): detects banned kana in the reading string (hiragana) derived from tokenization.
- VRR (Vocabulary Replacement Rate): replaced_tokens / total_tokens (unweighted).
- TTR (Type-Token Ratio): unique_tokens / total_tokens.
- N‑gram repetition rate: proportion of repeated n‑grams (default n=2).
- Timing helper: measure execution time of functions.

All metrics avoid network calls and rely on the local fugashi/UniDic tokenizer.

## Constraint Check (Reading-Based)

We tokenize the text with `JapaneseTokenizer` and concatenate token readings (hiragana). Banned kana are checked against this reading string.

```python
from ripogram.metrics import check_constraint

text = "猿も木から落ちる。"
banned = ["い", "さ"]
res = check_constraint(text, banned, mode="reading")
print(res.violated, res.found, res.count)
```

Notes:
- For 行禁止 (e.g., あ行), expand the set (e.g., `["あ","い","う","え","お"]`) before calling.
- Use `mode="surface"` to check surface text instead of reading.

## VRR (Vocabulary Replacement Rate)

Definition (unweighted): `VRR = replaced_tokens / total_tokens`.

- We exclude punctuation tokens (UniDic pos1=`記号`).
- If the number of tokens is the same between original and rewritten, we compare surfaces positionally.
- Otherwise, we use `1 - LCS_len / len(original_tokens)` as a robust approximation.

```python
from ripogram.metrics import compute_vrr

orig = "国境の長いトンネルを抜けると雪国であった。"
rewr = "国境の長いトンネルを過ぎると雪の国だった。"
vrr = compute_vrr(orig, rewr)
print(f"VRR: {vrr:.3f}")
```

## Diversity

### Type-Token Ratio (TTR)

```python
from ripogram.metrics import compute_ttr

ttr = compute_ttr("石の上にも三年。")
print(f"TTR: {ttr:.3f}")
```

### N‑gram Repetition Rate

We compute the fraction of repeated n‑grams beyond their first occurrence:

`sum(max(count(ng)-1, 0)) / total_n_grams`

```python
from ripogram.metrics import ngram_repetition_rate

rate = ngram_repetition_rate("今日は良い天気。今日は外に行こう。", n=2)
print(f"bigram repetition: {rate:.3f}")
```

## Timing Helper

```python
from ripogram.metrics import measure_time

def foo(x):
    return x**2

elapsed, result = measure_time(foo, 123)
print(elapsed, result)
```

## Notes & Assumptions

- Tokenization uses `JapaneseTokenizer` (fugashi/UniDic). Punctuation tokens (pos1=`記号`) are excluded in VRR/TTR/n‑gram calculations.
- Constraint checks default to `mode="reading"` and operate on concatenated token readings converted to hiragana.
- VRR is unweighted per the current experimental plan.

