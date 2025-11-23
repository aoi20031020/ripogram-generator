"""
Plot basic graphs for Japanese lipogram experiment results.

Usage:
  python scripts/plot_results.py --input results/results_500.csv --outdir results

Requires:
  - pandas
  - matplotlib
  (seaborn があれば少し見た目が良くなりますが必須ではありません)
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

try:
    import seaborn as sns  # type: ignore

    _HAS_SEABORN = True
except Exception:  # pragma: no cover
    _HAS_SEABORN = False


def prepare_success(df: pd.DataFrame) -> pd.DataFrame:
    """Add success flag and return copy."""
    df = df.copy()
    df["success"] = ~df["constraint_violated"]
    return df


def plot_success_by_method(df: pd.DataFrame, outdir: Path) -> None:
    """Bar chart: overall success rate by method."""
    agg = (
        df.groupby("method")["success"]
        .mean()
        .reset_index()
        .rename(columns={"success": "success_rate"})
    )

    plt.figure(figsize=(4, 4))
    if _HAS_SEABORN:
        sns.barplot(data=agg, x="method", y="success_rate")
    else:
        plt.bar(agg["method"], agg["success_rate"])
    plt.ylim(0, 1)
    plt.ylabel("Success rate")
    plt.title("Success rate by method (overall)")
    for i, row in agg.iterrows():
        plt.text(
            i,
            row["success_rate"] + 0.01,
            f"{row['success_rate']:.2f}",
            ha="center",
            va="bottom",
        )
    outfile = outdir / "success_by_method.png"
    plt.tight_layout()
    plt.savefig(outfile, dpi=200)
    plt.close()
    print(f"saved {outfile}")


def plot_success_by_constraint(df: pd.DataFrame, outdir: Path) -> None:
    """Grouped bar: success rate by constraint_type x method."""
    if "constraint_type" not in df.columns:
        return

    agg = (
        df.groupby(["constraint_type", "method"])["success"]
        .mean()
        .reset_index()
        .rename(columns={"success": "success_rate"})
    )

    plt.figure(figsize=(6, 4))
    if _HAS_SEABORN:
        sns.barplot(
            data=agg,
            x="constraint_type",
            y="success_rate",
            hue="method",
        )
    else:
        # simple grouped bar without seaborn
        types = agg["constraint_type"].unique()
        methods = agg["method"].unique()
        x = range(len(types))
        width = 0.35
        for j, m in enumerate(methods):
            sub = agg[agg["method"] == m]
            xs = [i + (j - 0.5) * width for i in x]
            plt.bar(xs, sub["success_rate"], width=width, label=m)
        plt.xticks(list(x), types)
        plt.legend()

    plt.ylim(0, 1)
    plt.ylabel("Success rate")
    plt.title("Success rate by constraint_type and method")
    outfile = outdir / "success_by_constraint_type.png"
    plt.tight_layout()
    plt.savefig(outfile, dpi=200)
    plt.close()
    print(f"saved {outfile}")


def make_wide(df: pd.DataFrame) -> pd.DataFrame:
    """Pivot to wide format for VRR/TTR plots."""
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
    return wide


def plot_vrr_box(both_ok: pd.DataFrame, outdir: Path) -> None:
    """Boxplot / violin of VRR for sequential vs oneshot (both succeed)."""
    if {"vrr_sequential", "vrr_oneshot"} - set(both_ok.columns):
        return

    long = pd.melt(
        both_ok,
        id_vars=["id"],
        value_vars=["vrr_sequential", "vrr_oneshot"],
        var_name="method",
        value_name="vrr",
    )
    long["method"] = long["method"].str.replace("vrr_", "", regex=False)

    plt.figure(figsize=(5, 4))
    if _HAS_SEABORN:
        sns.boxplot(data=long, x="method", y="vrr")
    else:
        # simple boxplot without seaborn
        data = [long[long["method"] == m]["vrr"].dropna() for m in ["sequential", "oneshot"]]
        plt.boxplot(data, labels=["sequential", "oneshot"])
    plt.ylabel("VRR")
    plt.title("VRR (pairs where both methods succeed)")
    outfile = outdir / "vrr_box_both_success.png"
    plt.tight_layout()
    plt.savefig(outfile, dpi=200)
    plt.close()
    print(f"saved {outfile}")


def plot_vrr_ttr_scatter(both_ok: pd.DataFrame, outdir: Path) -> None:
    """Scatter plot: VRR vs TTR, colored by method (sequential/oneshot)."""
    required = {"vrr_sequential", "vrr_oneshot", "ttr_sequential", "ttr_oneshot"}
    if required - set(both_ok.columns):
        return

    long = pd.melt(
        both_ok,
        id_vars=["id"],
        value_vars=[
            "vrr_sequential",
            "vrr_oneshot",
            "ttr_sequential",
            "ttr_oneshot",
        ],
        var_name="metric_method",
        value_name="value",
    )

    # reshape into columns: method, vrr, ttr
    long[["metric", "method"]] = long["metric_method"].str.split("_", n=1, expand=True)
    pivot = long.pivot_table(
        index=["id", "method"], columns="metric", values="value", aggfunc="first"
    ).reset_index()

    plt.figure(figsize=(5, 4))
    if _HAS_SEABORN:
        sns.scatterplot(data=pivot, x="vrr", y="ttr", hue="method")
    else:
        for m, color in [("sequential", "tab:blue"), ("oneshot", "tab:orange")]:
            sub = pivot[pivot["method"] == m]
            plt.scatter(sub["vrr"], sub["ttr"], label=m, alpha=0.7, s=20, c=color)
        plt.legend()
    plt.xlabel("VRR")
    plt.ylabel("TTR")
    plt.title("VRR vs TTR (both methods succeed)")
    outfile = outdir / "vrr_ttr_scatter_both_success.png"
    plt.tight_layout()
    plt.savefig(outfile, dpi=200)
    plt.close()
    print(f"saved {outfile}")


def plot_success_vs_vrr(df: pd.DataFrame, outdir: Path) -> None:
    """Success rate as a function of VRR (binned), by method."""
    if "vrr" not in df.columns:
        return

    df = df.copy()
    df["success"] = df["success"].astype(bool)
    # ビンを固定しておく（0.0〜1.0 を 5 区間）
    bins = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]
    labels = ["[0.0,0.2)", "[0.2,0.4)", "[0.4,0.6)", "[0.6,0.8)", "[0.8,1.0]"]
    df["vrr_bin"] = pd.cut(df["vrr"], bins=bins, labels=labels, include_lowest=True)

    agg = (
        df.groupby(["vrr_bin", "method"])["success"]
        .mean()
        .reset_index()
        .rename(columns={"success": "success_rate"})
    )

    plt.figure(figsize=(7, 4))
    if _HAS_SEABORN:
        sns.lineplot(
            data=agg,
            x="vrr_bin",
            y="success_rate",
            hue="method",
            marker="o",
        )
    else:
        methods = agg["method"].unique()
        x_pos = range(len(labels))
        for m in methods:
            sub = agg[agg["method"] == m]
            xs = [labels.index(b) for b in sub["vrr_bin"]]
            plt.plot(xs, sub["success_rate"], marker="o", label=m)
        plt.xticks(list(x_pos), labels)
        plt.legend()

    plt.ylim(0, 1)
    plt.ylabel("Success rate")
    plt.xlabel("VRR bin")
    plt.title("Success rate vs VRR (binned)")
    outfile = outdir / "success_vs_vrr.png"
    plt.tight_layout()
    plt.savefig(outfile, dpi=200)
    plt.close()
    print(f"saved {outfile}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Plot graphs from lipogram experiment results.")
    parser.add_argument("--input", "-i", required=True, help="Path to results CSV")
    parser.add_argument("--outdir", "-o", default="results", help="Output directory for images")
    args = parser.parse_args()

    path = Path(args.input)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(path)
    df = prepare_success(df)

    # basic success plots
    plot_success_by_method(df, outdir)
    plot_success_by_constraint(df, outdir)
    plot_success_vs_vrr(df, outdir)

    # VRR box for pairs where both succeed
    wide = make_wide(df)
    both_ok = wide[(wide.get("success_sequential") == True) & (wide.get("success_oneshot") == True)]
    if not both_ok.empty:
        plot_vrr_box(both_ok, outdir)
        plot_vrr_ttr_scatter(both_ok, outdir)


if __name__ == "__main__":
    main()
