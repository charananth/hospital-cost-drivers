"""Static report figures."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

SURFACE = "#fcfcfb"
TEXT = "#0b0b0b"
MUTED = "#52514e"
GRID = "#e6e5e0"
SERIES = {
    "total_exp": ("Total operating expense", "#2a78d6"),
    "cost_per_fte": ("Employee cost per FTE", "#eb6834"),
    "overhead_exp_per_fte": ("Overhead expense per FTE", "#1baf7a"),
    "fte": ("FTEs", "#eda100"),
    "adj_days": ("Adjusted patient days", "#e87ba4"),
    "discharges": ("Discharges", "#6250d6"),
}
FACTORS = {
    "volume": ("Volume", "#6250d6"),
    "staffing": ("Staffing per adjusted day", "#eda100"),
    "wage": ("Cost per FTE", "#eb6834"),
    "real_wage": ("Real cost per FTE", "#eb6834"),
    "inflation": ("Medical inflation", "#2a78d6"),
}


def style(ax):
    ax.set_facecolor(SURFACE)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.spines["bottom"].set_color(MUTED)
    ax.tick_params(colors=MUTED, length=0)


def plot_index(index, path, cohort):
    fig, ax = plt.subplots(figsize=(9, 5.2), facecolor=SURFACE)
    style(ax)
    ends = []
    for col, (label, color) in SERIES.items():
        ax.plot(index.index, index[col], color=color, linewidth=2, marker="o",
                markersize=5, markeredgecolor=SURFACE, label=label)
        ends.append([index[col].iloc[-1], f"{label} ({index[col].iloc[-1] / 100:.1f}x)"])
    # Nudge end labels apart so close series stay readable.
    ends.sort()
    gap = (index.max().max() - index.min().min()) * 0.055
    ys = [ends[0][0]]
    for value, _ in ends[1:]:
        ys.append(max(value, ys[-1] + gap))
    for (_, text), y in zip(ends, ys):
        ax.annotate(text, (index.index[-1], y), xytext=(10, 0), textcoords="offset points",
                    va="center", color=TEXT, fontsize=9, annotation_clip=False)
    ax.set_xticks(index.index)
    ax.set_ylabel("Index, 2004 = 100", color=MUTED)
    ax.set_title(f"Costs grew far faster than volume ({cohort} hospitals)",
                 loc="left", color=TEXT, fontsize=13)
    ax.legend(frameon=False, loc="upper left", fontsize=9, labelcolor=MUTED)
    fig.tight_layout(rect=(0, 0, 0.8, 1))
    fig.savefig(path, dpi=200)
    plt.close(fig)


def plot_decomposition(table, path, cohort):
    data = table[table["end"] - table["start"] == 5]
    periods = sorted(data["start"].unique())
    groups = ["patient", "overhead"]
    factors = [f for f in FACTORS if f in set(data["factor"])]
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.8), sharey=True, facecolor=SURFACE)
    for ax, group in zip(axes, groups):
        style(ax)
        part = data[data["group"] == group].pivot(index="start", columns="factor", values="effect")
        part = part.reindex(periods)[factors] / 1e9
        pos, neg = np.zeros(len(periods)), np.zeros(len(periods))
        x = np.arange(len(periods))
        for factor in factors:
            values = part[factor].to_numpy()
            bottom = np.where(values >= 0, pos, neg)
            label, color = FACTORS[factor]
            ax.bar(x, values, bottom=bottom, width=0.55, color=color, label=label,
                   edgecolor=SURFACE, linewidth=1.5)
            pos += np.clip(values, 0, None)
            neg += np.clip(values, None, 0)
        ax.axhline(0, color=MUTED, linewidth=0.8)
        ax.set_xticks(x, [f"{p}–{str(p + 5)[2:]}" for p in periods])
        ax.set_title(f"{group.capitalize()} labor", loc="left", color=TEXT, fontsize=11)
    axes[0].set_ylabel("Change in employee cost ($B, nominal)", color=MUTED)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, frameon=False, loc="lower center", ncol=len(factors),
               fontsize=9, labelcolor=MUTED)
    fig.suptitle(f"What drove employee cost growth ({cohort} hospitals)",
                 x=0.02, ha="left", color=TEXT, fontsize=13)
    fig.tight_layout(rect=(0, 0.07, 1, 0.97))
    fig.savefig(path, dpi=200)
    plt.close(fig)
