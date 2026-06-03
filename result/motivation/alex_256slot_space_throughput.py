#!/usr/bin/env python3
"""Space vs Throughput for Memory-Matched ALEX-256 Variants.

Reads checked-in benchmark summaries from this directory and:
  1. Prints the combined plot_data table (dataset × index × throughput × memory).
  2. Prints the melted throughput_data table.
  3. Saves insert and read scatter plots as PNG files.

Usage:
  uv run --extra notebook python3 result/motivation/alex_256slot_space_throughput.py
"""

# NOTE: This script depends on motivation_single_thread_uniform_100m_shuffled_summary.csv,
# which is produced by a separate experiment (test_suite=22, 100M bulkload). If that
# experiment is re-run, this script may produce different results. Re-run both experiments
# together to keep the plot consistent.

from pathlib import Path

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

sns.set_theme(style="whitegrid", context="talk")

plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.sans-serif"] = ["Carlito"]
plt.rcParams["font.size"] = 14
plt.rcParams["axes.titlesize"] = 16
plt.rcParams["axes.labelsize"] = 14
plt.rcParams["legend.fontsize"] = 13
plt.rcParams["legend.title_fontsize"] = 13

RESULT_DIR = Path(__file__).resolve().parent
MOTIVATION_SUMMARY = RESULT_DIR / "motivation_single_thread_uniform_100m_shuffled_summary.csv"
TUNING_SUMMARY = RESULT_DIR / "alex_256slot_dataset_load_factor_summary.csv"

DATASETS = ["linear", "covid", "fb-1", "osm"]
BASELINE_INDEXES = ["art", "alex", "lipp", "lipp-256slot"]
TUNED_INDEXES = {
    "linear": "alex-256slot",
    "covid": "alex-256slot-lf024",
    "fb-1": "alex-256slot-lf020",
    "osm": "alex-256slot-lf019",
}

# ── Load ────────────────────────────────────────────────────────────────────

motivation_full = pd.read_csv(MOTIVATION_SUMMARY)
motivation_full = motivation_full.rename(
    columns={
        "index_type": "index",
        "insert_throughput_mops_avg": "insert_mops_avg",
        "read_throughput_mops_avg": "read_mops_avg",
    }
)
motivation_full = motivation_full[motivation_full["dataset"].isin(DATASETS)]

motivation = motivation_full[motivation_full["index"].isin(BASELINE_INDEXES)]
motivation = motivation[["dataset", "index", "insert_mops_avg", "read_mops_avg", "memory_gib"]]

tuning = pd.read_csv(TUNING_SUMMARY)
tuned_rows = []
for dataset, index in TUNED_INDEXES.items():
    if dataset == "linear":
        row = motivation_full[
            (motivation_full["dataset"] == dataset) & (motivation_full["index"] == index)
        ]
    else:
        row = tuning[(tuning["dataset"] == dataset) & (tuning["index"] == index)]
    if row.empty:
        raise ValueError(f"Missing tuned row for {dataset=} {index=}")
    tuned_rows.append(row.iloc[0])
tuned = pd.DataFrame(tuned_rows)[
    ["dataset", "index", "insert_mops_avg", "read_mops_avg", "memory_gib"]
]

plot_data = pd.concat([motivation, tuned], ignore_index=True)
plot_data["index"] = pd.Categorical(
    plot_data["index"],
    categories=BASELINE_INDEXES + list(TUNED_INDEXES.values()),
    ordered=True,
)
plot_data = plot_data.sort_values(["dataset", "index"]).reset_index(drop=True)

# ── Print table: plot_data ──────────────────────────────────────────────────

print("=" * 80)
print("plot_data (combined baseline + tuned rows)")
print("=" * 80)
print(plot_data.to_string(index=False))
print()

# ── Melt ────────────────────────────────────────────────────────────────────

throughput_data = plot_data.melt(
    id_vars=["dataset", "index", "memory_gib"],
    value_vars=["insert_mops_avg", "read_mops_avg"],
    var_name="phase",
    value_name="throughput_mops",
)
throughput_data["phase"] = throughput_data["phase"].map(
    {"insert_mops_avg": "insert", "read_mops_avg": "read"}
)

print("=" * 80)
print("throughput_data (melted)")
print("=" * 80)
print(throughput_data.to_string(index=False))
print()

# ── Normalize legend labels ─────────────────────────────────────────────────
# Merge all alex-256slot(-lf*) variants into a single "alex-256slot" label
# for cleaner plot legends. The printed tables above retain original names.
throughput_data["index"] = throughput_data["index"].str.replace(
    r"^alex-256slot(-.+)?$", "alex-256slot", regex=True
)

# ── Plot: insert throughput ─────────────────────────────────────────────────

insert_data = throughput_data[throughput_data["phase"] == "insert"]
fig, axes = plt.subplots(1, len(DATASETS), figsize=(22, 5), sharey=False)
for ax, dataset in zip(axes, DATASETS):
    data = insert_data[insert_data["dataset"] == dataset]
    sns.scatterplot(
        data=data,
        x="memory_gib",
        y="throughput_mops",
        hue="index",
        style="index",
        s=140,
        ax=ax,
    )
    for _, row in data.iterrows():
        ax.annotate(
            row["index"],
            (row["memory_gib"], row["throughput_mops"]),
            xytext=(6, 4),
            textcoords="offset points",
            fontsize=9,
        )
    ax.set_title(dataset)
    ax.set_xlabel("Space (GiB)")
    ax.set_ylabel("Insert throughput (Mops/s)")
    ax.get_legend().remove()
handles, labels = axes[-1].get_legend_handles_labels()
fig.legend(
    handles, labels, loc="upper center", bbox_to_anchor=(0.5, 1.08), ncol=3, title="Index"
)
fig.tight_layout(rect=(0, 0, 1, 0.90))
insert_path = RESULT_DIR / "alex_256slot_space_throughput_insert.png"
fig.savefig(insert_path, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"Saved: {insert_path}")

# ── Plot: read throughput ───────────────────────────────────────────────────

read_data = throughput_data[throughput_data["phase"] == "read"]
fig, axes = plt.subplots(1, len(DATASETS), figsize=(22, 5), sharey=False)
for ax, dataset in zip(axes, DATASETS):
    data = read_data[read_data["dataset"] == dataset]
    sns.scatterplot(
        data=data,
        x="memory_gib",
        y="throughput_mops",
        hue="index",
        style="index",
        s=140,
        ax=ax,
    )
    for _, row in data.iterrows():
        ax.annotate(
            row["index"],
            (row["memory_gib"], row["throughput_mops"]),
            xytext=(6, 4),
            textcoords="offset points",
            fontsize=9,
        )
    ax.set_title(dataset)
    ax.set_xlabel("Space (GiB)")
    ax.set_ylabel("Read throughput (Mops/s)")
    ax.get_legend().remove()
handles, labels = axes[-1].get_legend_handles_labels()
fig.legend(
    handles, labels, loc="upper center", bbox_to_anchor=(0.5, 1.08), ncol=3, title="Index"
)
fig.tight_layout(rect=(0, 0, 1, 0.90))
read_path = RESULT_DIR / "alex_256slot_space_throughput_read.png"
fig.savefig(read_path, dpi=150, bbox_inches="tight")
plt.close(fig)
print(f"Saved: {read_path}")
print()
print("Done.")
