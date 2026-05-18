#!/usr/bin/env python3
"""
whisper_github_plot_results.py

Purpose
-------
Create a public-facing summary figure for the Whisper decoder-control basin report.

Input
-----
data/public_result_summary.csv

Output
------
figures/decoder_control_error_reduction.png

Usage
-----
Run from inside the repository:

    python make_results_figure.py

Notes
-----
This script only visualizes aggregate public results. It does not require model weights,
audio files, transcripts, or private experimental machinery.
"""

from pathlib import Path
import textwrap

import pandas as pd
import matplotlib.pyplot as plt


INPUT_CSV = Path("data/public_result_summary.csv")
OUTPUT_DIR = Path("figures")
OUTPUT_PNG = OUTPUT_DIR / "decoder_control_error_reduction.png"


def pct(x: float) -> str:
    return f"{100.0 * x:.1f}%"


def make_label(row: pd.Series) -> str:
    model = str(row["model"])
    dataset = str(row["dataset"])

    if row["result_group"] == "heldout_selector":
        model = model.replace("ggml-", "").replace(".en.bin", "")
        dataset = dataset.replace("fold_", "fold ").replace("_to_", " → ")
        return f"{model}\n{dataset}"

    dataset = dataset.replace("_manifest", "")

    if dataset == "medium_specific_hard":
        return f"{model}\nmedium\nspecific hard"

    dataset = (
        dataset
        .replace("small_specific_hard", "small hard")
        .replace("tiny_original_hard", "tiny hard")
        .replace("_", " ")
    )
    return f"{model}\n{dataset}"


def main() -> None:
    if not INPUT_CSV.exists():
        raise FileNotFoundError(f"Missing input file: {INPUT_CSV}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(INPUT_CSV)

    required = {
        "result_group",
        "model",
        "dataset",
        "baseline_errors",
        "selected_errors",
        "delta_errors",
        "relative_reduction",
    }
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"Input is missing required columns: {missing}")

    df = df.copy()
    df["label"] = df.apply(make_label, axis=1)
    df["row_order"] = range(len(df))

    heldout = df[df["result_group"] == "heldout_selector"].copy()
    basin = df[df["result_group"] == "parameter_basin"].copy()

    groups = [
        ("Held-out selector", heldout),
        ("Source-level basin sweeps", basin),
    ]

    fig, axes = plt.subplots(
        1,
        2,
        figsize=(15.5, 7.2),
        gridspec_kw={"width_ratios": [1.05, 1.35]},
    )

    width = 0.36

    for ax, (group_title, g) in zip(axes, groups):
        g = g.reset_index(drop=True)
        x = list(range(len(g)))

        baseline_x = [i - width / 2 for i in x]
        selected_x = [i + width / 2 for i in x]

        ax.bar(
            baseline_x,
            g["baseline_errors"],
            width,
            label="Baseline decoder",
        )
        ax.bar(
            selected_x,
            g["selected_errors"],
            width,
            label="Selected control state",
        )

        ymax = max(g["baseline_errors"].max(), g["selected_errors"].max())
        ax.set_ylim(0, ymax * 1.28)

        for i, row in g.iterrows():
            baseline = float(row["baseline_errors"])
            selected = float(row["selected_errors"])
            reduction = float(row["relative_reduction"])
            delta = int(row["delta_errors"])

            y = max(baseline, selected)
            label = f"{pct(reduction)}\n{delta:+d} errors"

            ax.text(
                i,
                y + ymax * 0.035,
                label,
                ha="center",
                va="bottom",
                fontsize=9,
            )

        ax.set_title(group_title, fontsize=13, pad=14)
        ax.set_xticks(x)
        ax.set_xticklabels(g["label"], rotation=0, ha="center")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.grid(axis="y", alpha=0.25)

    axes[0].set_ylabel("Word-level edit errors")
    axes[1].set_ylabel("Word-level edit errors")

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, frameon=False, loc="upper right", bbox_to_anchor=(0.965, 0.93))

    fig.suptitle(
        "Whisper decoder-control states reduce WER across tested model sizes",
        fontsize=17,
        y=0.985,
    )

    subtitle = (
        "Aggregate public results only. Bars compare baseline decoding against selected deterministic "
        "decoder-control states; lower error count is better. Separate panels use separate y-scales."
    )
    fig.text(
        0.5,
        0.935,
        textwrap.fill(subtitle, 130),
        ha="center",
        va="top",
        fontsize=10,
    )

    fig.subplots_adjust(top=0.84, bottom=0.18, left=0.07, right=0.94, wspace=0.20)
    fig.savefig(OUTPUT_PNG, dpi=220, bbox_inches="tight")
    print(f"wrote: {OUTPUT_PNG}")


if __name__ == "__main__":
    main()
