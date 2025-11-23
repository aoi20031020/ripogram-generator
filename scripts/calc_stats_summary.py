"""
Compute basic statistics and paired t-tests for Japanese lipogram experiments.

Usage:
  python scripts/calc_stats_summary.py --input results/results_500.csv
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from scipy import stats


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute summary stats and t-tests.")
    parser.add_argument("--input", "-i", required=True, help="Path to results CSV")
    args = parser.parse_args()

    path = Path(args.input)
    df = pd.read_csv(path)

    # success flag
    df["success"] = ~df["constraint_violated"]

    # overall success rate by method
    agg = df.groupby("method")["success"].mean().reset_index()
    print("=== Overall success rate by method (reading-based) ===")
    for _, row in agg.iterrows():
        print(f"{row['method']:10s}: {row['success']*100:5.1f}%")
    print()

    # basic descriptive stats by method for selected metrics
    metrics = ["vrr", "ttr", "time_sec"]
    available_metrics = [m for m in metrics if m in df.columns]
    if available_metrics:
        print("=== Descriptive statistics by method ===")
        for m in available_metrics:
            print(f"\n[{m}]")
            g = df.groupby("method")[m]
            desc = g.describe()  # count, mean, std, min, 25%, 50%, 75%, max
            # add IQR = 75% - 25%
            desc["IQR"] = desc["75%"] - desc["25%"]
            # print selected columns
            for method, row in desc.iterrows():
                print(
                    f"{method:10s}: "
                    f"mean={row['mean']:.3f}, sd={row['std']:.3f}, "
                    f"median={row['50%']:.3f}, IQR={row['IQR']:.3f}, "
                    f"N={int(row['count'])}"
                )
        print()

    # pivot to wide format: one row per id
    wide = df.pivot_table(
        index="id",
        columns="method",
        values=["success", "vrr", "ttr"],
        aggfunc="first",
    )
    wide.columns = [f"{v}_{m}" for v, m in wide.columns]
    wide = wide.reset_index()

    # paired t-test for success flag (RQ1)
    success_seq = wide["success_sequential"].astype(float)
    success_one = wide["success_oneshot"].astype(float)
    t_success, p_success = stats.ttest_rel(success_seq, success_one)
    print("=== Paired t-test: success flag (sequential vs oneshot) ===")
    print(f"t = {t_success:.2f}, p = {p_success:.3e}")
    print()

    # restrict to pairs where both methods succeed (RQ2)
    both_ok = wide[(wide["success_sequential"] == True) &
                   (wide["success_oneshot"] == True)]
    if not both_ok.empty:
        vrr_seq = both_ok["vrr_sequential"]
        vrr_one = both_ok["vrr_oneshot"]
        t_vrr, p_vrr = stats.ttest_rel(vrr_seq, vrr_one)
        print("=== Paired t-test: VRR (both methods succeed) ===")
        print(f"t = {t_vrr:.2f}, p = {p_vrr:.3e}")

        ttr_seq = both_ok["ttr_sequential"]
        ttr_one = both_ok["ttr_oneshot"]
        t_ttr, p_ttr = stats.ttest_rel(ttr_seq, ttr_one)
        print("=== Paired t-test: TTR (both methods succeed) ===")
        print(f"t = {t_ttr:.2f}, p = {p_ttr:.3e}")
    else:
        print("No pairs where both methods succeed; VRR/TTR tests skipped.")


if __name__ == "__main__":
    main()
