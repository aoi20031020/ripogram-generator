"""
Demo script for metrics on Japanese lipogram evaluation.

This script shows how to compute:
- Constraint check (reading-based)
- VRR (unweighted)
- TTR
- N-gram repetition rate

If an OpenAI API key is available (.env with OPENAI_API_KEY), it will also
demonstrate generating rewritten outputs via RipogramRewriter for:
- sequential (context-aware token-level rewriting)
- oneshot (single-call rewriting)

Otherwise, it falls back to a fixed example.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Ensure project root is on sys.path when running this file directly
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ripogram.metrics import (
    check_constraint,
    compute_vrr,
    compute_ttr,
    ngram_repetition_rate,
)

try:
    from ripogram.config import Config
    from ripogram.core.rewriter import RipogramRewriter

    _CAN_USE_LLM = True
except Exception:
    _CAN_USE_LLM = False


def print_metrics(label: str, original: str, rewritten: str, banned):
    print(f"\n=== {label} ===")
    print(rewritten)

    cc = check_constraint(rewritten, banned, mode="reading")
    print("[Constraint] violated=", cc.violated, "found=", cc.found, "count=", cc.count)

    vrr = compute_vrr(original, rewritten)
    print(f"[VRR] {vrr:.3f}")

    ttr = compute_ttr(rewritten)
    bigram_rep = ngram_repetition_rate(rewritten, n=2)
    trigram_rep = ngram_repetition_rate(rewritten, n=3)
    print(f"[TTR] {ttr:.3f}")
    print(f"[n-gram repetition] bi={bigram_rep:.3f}, tri={trigram_rep:.3f}")


def main():
    load_dotenv()

    original = "猿も木から落ちる。石の上にも三年。"
    banned = ["い", "さ"]

    seq_text = None
    oneshot_text = None

    if _CAN_USE_LLM and os.getenv("OPENAI_API_KEY"):
        try:
            cfg = Config()
            rewriter = RipogramRewriter(api_key=cfg.openai_api_key, model_name=cfg.model_name)
            # sequential (context-aware token-level)
            seq_text = rewriter.rewrite_text_with_context(original, banned, verbose=False)
            # oneshot (single-call baseline)
            oneshot_text = rewriter.rewrite_text_one_shot(original, banned, verbose=False)
        except Exception as e:
            print(f"LLM not available: {e}. Falling back to a manual example.")

    if seq_text is None:
        # Manual toy example for both, when LLM is unavailable
        seq_text = "猿も木から落ちる。辛抱は大切。"
    if oneshot_text is None:
        oneshot_text = seq_text

    print("=== Input ===")
    print(original)

    print_metrics("Sequential (rewrite_text_with_context)", original, seq_text, banned)
    print_metrics("One-shot (rewrite_text_one_shot)", original, oneshot_text, banned)


if __name__ == "__main__":
    main()
