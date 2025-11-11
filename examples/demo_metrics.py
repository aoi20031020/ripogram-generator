"""
Demo script for metrics on Japanese lipogram evaluation.

This script shows how to compute:
- Constraint check (reading-based)
- VRR (unweighted)
- TTR
- N-gram repetition rate

If an OpenAI API key is available (.env with OPENAI_API_KEY), it will also
demonstrate generating a rewritten output via RipogramRewriter for a quick
end-to-end check. Otherwise, it falls back to a fixed example.
"""

import os
from dotenv import load_dotenv

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


def main():
    load_dotenv()

    original = "猿も木から落ちる。石の上にも三年。"
    banned = ["い", "さ"]

    # Prepare rewritten text
    rewritten = None
    if _CAN_USE_LLM and os.getenv("OPENAI_API_KEY"):
        try:
            cfg = Config()
            rewriter = RipogramRewriter(api_key=cfg.openai_api_key, model_name=cfg.model_name)
            rewritten = rewriter.rewrite_text_with_context(original, banned, verbose=False)
        except Exception as e:
            print(f"LLM not available: {e}
Falling back to a manual example.")

    if rewritten is None:
        # Manual toy example
        rewritten = "猿も木から落ちる。辛抱は大切。"

    print("=== Input ===")
    print(original)
    print("\n=== Rewritten ===")
    print(rewritten)

    # Constraint (reading-based)
    cc = check_constraint(rewritten, banned, mode="reading")
    print("\n[Constraint] violated=", cc.violated, "found=", cc.found, "count=", cc.count)

    # VRR
    vrr = compute_vrr(original, rewritten)
    print(f"[VRR] {vrr:.3f}")

    # Diversity
    ttr = compute_ttr(rewritten)
    bigram_rep = ngram_repetition_rate(rewritten, n=2)
    trigram_rep = ngram_repetition_rate(rewritten, n=3)
    print(f"[TTR] {ttr:.3f}")
    print(f"[n-gram repetition] bi={bigram_rep:.3f}, tri={trigram_rep:.3f}")


if __name__ == "__main__":
    main()

