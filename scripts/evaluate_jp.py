"""
Batch evaluation script for Japanese lipogram generation.

This script runs two rewriting modes (sequential token-level vs one-shot
baseline) and computes metrics for each row in an input dataset.

Input format:
  - CSV or JSONL with at least a 'text' column. Optionally:
      'banned_chars' (e.g., "い,さ")
      'genre', 'difficulty' (any metadata are preserved if present)
  - If 'banned_chars' is missing, you must provide it via --banned.

Output:
  - CSV with columns: id, method, text, banned_chars, output, constraint_violated,
    constraint_found, constraint_count, vrr, ttr, bigram_rep, trigram_rep, time_sec,
    plus passthrough metadata columns (e.g., genre, difficulty) if present.

Usage examples:
  python scripts/evaluate_jp.py --input data/dev.csv --output results.csv --model gpt-4.1-nano
  python scripts/evaluate_jp.py --input data/dev.jsonl --methods sequential oneshot \
      --banned "あ,い,う,え,お" --limit 50

Notes:
  - Requires OPENAI_API_KEY in environment or .env (via ripogram.Config).
  - Network calls only happen for rewriting; metrics are local.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
from typing import List, Dict, Any, Iterable

from dotenv import load_dotenv

from ripogram.config import Config
from ripogram.core.rewriter import RipogramRewriter
from ripogram.metrics import (
    check_constraint,
    compute_vrr,
    compute_ttr,
    ngram_repetition_rate,
    measure_time,
)


def parse_banned(s: str) -> List[str]:
    return [c.strip() for c in s.split(",") if c.strip()]


def read_rows(path: str) -> List[Dict[str, Any]]:
    ext = os.path.splitext(path)[1].lower()
    rows: List[Dict[str, Any]] = []
    if ext in {".csv"}:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                rows.append(r)
    elif ext in {".jsonl", ".ndjson"}:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
    else:
        raise ValueError("Unsupported input format. Use CSV or JSONL.")
    return rows


def write_rows(path: str, rows: Iterable[Dict[str, Any]]):
    rows = list(rows)
    if not rows:
        # Create an empty file with no header
        open(path, "w", encoding="utf-8").close()
        return
    fieldnames = list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def main():
    parser = argparse.ArgumentParser(description="Evaluate Japanese lipogram generation (batch)")
    parser.add_argument("--input", "-i", required=True, help="Path to input CSV/JSONL")
    parser.add_argument("--output", "-o", required=True, help="Path to output CSV")
    parser.add_argument("--methods", nargs="+", default=["sequential", "oneshot"],
                        choices=["sequential", "oneshot"], help="Methods to evaluate")
    parser.add_argument("--banned", type=str, help="Fallback banned chars if column is missing (e.g., 'い,さ')")
    parser.add_argument("--limit", type=int, default=0, help="Process at most N rows (0=all)")
    parser.add_argument("--model", type=str, default="gpt-4.1-nano", help="OpenAI model name")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    load_dotenv()
    cfg = Config()
    if args.model:
        cfg.model_name = args.model

    banned_default: List[str] = parse_banned(args.banned) if args.banned else []

    rows = read_rows(args.input)
    if args.limit and args.limit > 0:
        rows = rows[: args.limit]

    rewriter = RipogramRewriter(api_key=cfg.openai_api_key, model_name=cfg.model_name)

    outputs: List[Dict[str, Any]] = []
    for idx, row in enumerate(rows):
        text = (row.get("text") or row.get("sentence") or "").strip()
        if not text:
            continue
        banned_str = (row.get("banned_chars") or row.get("banned") or "").strip()
        banned = parse_banned(banned_str) if banned_str else banned_default
        if not banned:
            raise ValueError("No banned characters provided (row lacks 'banned_chars' and --banned not set)")

        meta = {k: v for k, v in row.items() if k not in {"text", "sentence", "banned", "banned_chars"}}

        for method in args.methods:
            if method == "sequential":
                elapsed, out_text = measure_time(
                    rewriter.rewrite_text_with_context, text, banned, False
                )
            else:  # oneshot
                elapsed, out_text = measure_time(
                    rewriter.rewrite_text_one_shot, text, banned, False
                )

            # Metrics
            cc = check_constraint(out_text, banned, mode="reading")
            vrr = compute_vrr(text, out_text)
            ttr = compute_ttr(out_text)
            rep2 = ngram_repetition_rate(out_text, n=2)
            rep3 = ngram_repetition_rate(out_text, n=3)

            rec: Dict[str, Any] = {
                "id": idx,
                "method": method,
                "text": text,
                "banned_chars": ",".join(banned),
                "output": out_text,
                "constraint_violated": cc.violated,
                "constraint_found": ",".join(cc.found),
                "constraint_count": cc.count,
                "vrr": round(vrr, 6),
                "ttr": round(ttr, 6),
                "bigram_rep": round(rep2, 6),
                "trigram_rep": round(rep3, 6),
                "time_sec": round(elapsed, 6),
            }
            rec.update(meta)
            outputs.append(rec)

            if args.verbose:
                print(f"[{idx}] {method} | violated={cc.violated} vrr={vrr:.3f} ttr={ttr:.3f} time={elapsed:.2f}s")

    write_rows(args.output, outputs)
    if args.verbose:
        print(f"Saved {len(outputs)} rows to {args.output}")


if __name__ == "__main__":
    main()

