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

    dataset = (
        dataset.replace("_manifest", "")
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

    x = list(range(len(df)))
    width = 0.36

    fig, ax = plt.subplots(figsize=(14.5, 7.8))

    baseline_x = [i - width / 2 for i in x]
    selected_x = [i + width / 2 for i in x]

    ax.bar(
        baseline_x,
        df["baseline_errors"],
        width,
        label="Baseline decoder",
    )
    ax.bar(
        selected_x,
        df["selected_errors"],
        width,
        label="Selected control state",
    )

    for i, row in df.iterrows():
        baseline = float(row["baseline_errors"])
        selected = float(row["selected_errors"])
        reduction = float(row["relative_reduction"])
        delta = int(row["delta_errors"])

        y = max(baseline, selected)
        label = f"{pct(reduction)}\n{delta:+d} errors"

        ax.text(
            i,
            y + max(df["baseline_errors"]) * 0.025,
            label,
            ha="center",
            va="bottom",
            fontsize=9,
        )

    fig.suptitle(
        "Whisper decoder-control states reduce WER across tested model sizes",
        fontsize=17,
        y=0.965,
    )

    subtitle = (
        "Aggregate public results only. Bars compare baseline decoding against selected deterministic "
        "decoder-control states; lower error count is better."
    )
    fig.text(
        0.5,
        0.925,
        textwrap.fill(subtitle, 120),
        ha="center",
        va="top",
        fontsize=10,
    )

    ax.set_ylabel("Word-level edit errors")
    ax.set_xticks(x)
    ax.set_xticklabels(df["label"], rotation=0, ha="center")
    ax.legend(frameon=False, loc="upper right")

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", alpha=0.25)

    group_boundary = 3.5
    ax.axvline(group_boundary, linestyle="--", linewidth=1, alpha=0.5)
    ax.text(
        1.5,
        -0.18,
        "Held-out selector",
        transform=ax.get_xaxis_transform(),
        ha="center",
        va="top",
        fontsize=10,
    )
    ax.text(
        5.5,
        -0.18,
        "Parameter-basin sweeps",
        transform=ax.get_xaxis_transform(),
        ha="center",
        va="top",
        fontsize=10,
    )

    ymax = max(df["baseline_errors"].max(), df["selected_errors"].max())
    ax.set_ylim(0, ymax * 1.18)

    fig.subplots_adjust(top=0.86, bottom=0.18, left=0.07, right=0.97)
    fig.savefig(OUTPUT_PNG, dpi=220, bbox_inches="tight")
    print(f"wrote: {OUTPUT_PNG}")


if __name__ == "__main__":
    main()