"""
Simple analysis script for Japanese lipogram experiments.

Usage:
  python scripts/analyze_results.py --input results_500.csv

This script expects the CSV produced by scripts/evaluate_jp.py, i.e. with
columns including at least:
  id, method, constraint_violated, vrr, ttr, constraint_type, genre

It will:
  - Compute success rate (constraint_violated == False) by method
  - Break down success rate by constraint_type and genre
  - Pivot to a wide format (one row per id) to compare sequential vs oneshot
  - Compute per-id differences in success / VRR / TTR
  - Optionally run paired t-tests if scipy is available
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def summarize_success(df: pd.DataFrame) -> None:
    """Print basic success-rate summaries."""
    df["success"] = ~df["constraint_violated"]

    print("=== Success rate by method ===")
    print(df.groupby("method")["success"].mean())
    print()

    if "constraint_type" in df.columns:
        print("=== Success rate by constraint_type x method ===")
        print(df.groupby(["constraint_type", "method"])["success"].mean())
        print()

    if "genre" in df.columns:
        print("=== Success rate by genre x method ===")
        print(df.groupby(["genre", "method"])["success"].mean())
        print()


def make_wide(df: pd.DataFrame) -> pd.DataFrame:
    """Pivot to wide format: one row per id (and condition), columns per method."""
    df = df.copy()
    df["success"] = ~df["constraint_violated"]

    index_cols = ["id"]
    for col in ["banned_chars", "constraint_type", "genre"]:
        if col in df.columns:
            index_cols.append(col)

    wide = df.pivot_table(
        index=index_cols,
        columns="method",
        values=["success", "vrr", "ttr"],
        aggfunc="first",
    )
    wide.columns = [f"{v}_{m}" for v, m in wide.columns]
    wide = wide.reset_index()

    # Drop rows missing either method
    required_cols = ["success_sequential", "success_oneshot"]
    wide = wide.dropna(subset=[c for c in required_cols if c in wide.columns])

    # Differences
    if {"success_sequential", "success_oneshot"} <= set(wide.columns):
        # cast bool -> int so subtraction is well-defined
        wide["success_sequential"] = wide["success_sequential"].astype(int)
        wide["success_oneshot"] = wide["success_oneshot"].astype(int)
        wide["success_diff"] = wide["success_sequential"] - wide["success_oneshot"]
    if {"vrr_sequential", "vrr_oneshot"} <= set(wide.columns):
        wide["vrr_diff"] = wide["vrr_sequential"] - wide["vrr_oneshot"]
    if {"ttr_sequential", "ttr_oneshot"} <= set(wide.columns):
        wide["ttr_diff"] = wide["ttr_sequential"] - wide["ttr_oneshot"]

    return wide


def analyze_differences(wide: pd.DataFrame) -> None:
    """Analyze per-id differences between sequential and oneshot."""
    if "success_diff" not in wide.columns:
        print("No success_diff column; skipping difference analysis.")
        return

    print("=== Per-id success comparison (sequential vs oneshot) ===")
    total = len(wide)
    more_seq = (wide["success_diff"] > 0).sum()
    more_one = (wide["success_diff"] < 0).sum()
    equal = (wide["success_diff"] == 0).sum()
    print(f"Total pairs: {total}")
    print(f"  seq > one: {more_seq} ({more_seq/total:.3f})")
    print(f"  seq < one: {more_one} ({more_one/total:.3f})")
    print(f"  equal    : {equal} ({equal/total:.3f})")
    print()

    if "constraint_type" in wide.columns:
        print("=== Success: P(seq > one) by constraint_type ===")
        def prob_seq_gt(group: pd.DataFrame) -> float:
            n = len(group)
            return float((group["success_diff"] > 0).sum()) / n if n else float("nan")

        print(wide.groupby("constraint_type").apply(prob_seq_gt))
        print()

    # Only consider pairs where both methods succeeded for VRR/TTR
    if {"success_sequential", "success_oneshot"} <= set(wide.columns):
        both_ok = wide[(wide["success_sequential"] == 1) & (wide["success_oneshot"] == 1)]
        if not both_ok.empty:
            print("=== VRR/TTR differences on pairs where both methods succeed ===")
            cols = [c for c in ["vrr_diff", "ttr_diff"] if c in both_ok.columns]
            print(both_ok[cols].mean())
            print()
            if "constraint_type" in both_ok.columns:
                print("=== VRR/TTR diff by constraint_type (both succeed) ===")
                print(both_ok.groupby("constraint_type")[cols].mean())
                print()


def run_tests(wide: pd.DataFrame) -> None:
    """Optional paired tests using scipy, if available."""
    try:
        from scipy.stats import ttest_rel
    except Exception:
        print("scipy not available; skipping statistical tests.")
        return

    if {"success_sequential", "success_oneshot"} <= set(wide.columns):
        print("=== Paired t-test on success (0/1) ===")
        tt = ttest_rel(wide["success_sequential"], wide["success_oneshot"])
        print(tt)
        print()

    both_ok = wide[(wide.get("success_sequential") == 1) & (wide.get("success_oneshot") == 1)]
    if not both_ok.empty and {"vrr_sequential", "vrr_oneshot"} <= set(both_ok.columns):
        print("=== Paired t-test on VRR (both succeed) ===")
        tt_vrr = ttest_rel(both_ok["vrr_sequential"], both_ok["vrr_oneshot"])
        print(tt_vrr)
        print()

    if not both_ok.empty and {"ttr_sequential", "ttr_oneshot"} <= set(both_ok.columns):
        print("=== Paired t-test on TTR (both succeed) ===")
        tt_ttr = ttest_rel(both_ok["ttr_sequential"], both_ok["ttr_oneshot"])
        print(tt_ttr)
        print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze Japanese lipogram experiment results.")
    parser.add_argument("--input", "-i", required=True, help="Path to results CSV (from evaluate_jp.py)")
    args = parser.parse_args()

    path = Path(args.input)
    df = pd.read_csv(path)

    summarize_success(df)
    wide = make_wide(df)
    analyze_differences(wide)
    run_tests(wide)


if __name__ == "__main__":
    main()
