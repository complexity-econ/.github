#!/usr/bin/env python3
"""
Animated bifurcation diagram — PLN vs EUR side-by-side BDP sweep.

Reads Campaign 1 (σ_mult=1.0) terminal CSVs from paper-04 and produces a GIF
that progressively reveals BDP levels, showing the reentrant PLN peak vs flat EUR.

Output: paper-04-phase-diagram/figures/animated_bifurcation.gif
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image
import io
import os

# ── Paths ───────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
P04_DIR = os.path.join(PROJECT_ROOT, "paper-04-phase-diagram")
PLN_DIR = os.path.join(P04_DIR, "simulations", "results", "c1_phase", "pln")
EUR_DIR = os.path.join(P04_DIR, "simulations", "results", "c1_phase", "eur")
OUTPUT_PATH = os.path.join(P04_DIR, "figures", "animated_bifurcation.gif")

# ── Parameters ──────────────────────────────────────────────────────────────
BDP_LEVELS = list(range(0, 5001, 250))  # 0, 250, 500, ..., 5000
HOLD_START = 3
HOLD_END = 4
FPS = 6
DPI = 100
FIG_SIZE = (10, 5)  # 1000×500 px

# Colors
PLN_COLOR = "#1f77b4"
EUR_COLOR = "#d62728"
PLN_FILL = "#1f77b4"
EUR_FILL = "#d62728"
BG_COLOR = "white"
CRIT_COLOR = "#2ca02c"  # green for critical line

# ── Load data ───────────────────────────────────────────────────────────────
def load_adoption(data_dir, regime, bdp_levels):
    """Load TotalAdoption from terminal CSVs for each BDP level."""
    result = {}
    for bdp in bdp_levels:
        fname = f"c1_{regime}_sm1_0_bdp{bdp}_terminal.csv"
        path = os.path.join(data_dir, fname)
        if os.path.exists(path):
            df = pd.read_csv(path, sep=";", decimal=",")
            result[bdp] = df["TotalAdoption"].values * 100  # to percent
        else:
            print(f"Warning: missing {path}")
    return result

print("Loading data...")
pln_data = load_adoption(PLN_DIR, "pln", BDP_LEVELS)
eur_data = load_adoption(EUR_DIR, "eur", BDP_LEVELS)

# Compute means and stds
pln_means = {b: np.mean(v) for b, v in pln_data.items()}
pln_stds = {b: np.std(v) for b, v in pln_data.items()}
eur_means = {b: np.mean(v) for b, v in eur_data.items()}
eur_stds = {b: np.std(v) for b, v in eur_data.items()}

# Y-axis limit
y_max = max(max(pln_means.values()), max(eur_means.values())) + 10

# ── Render frames ───────────────────────────────────────────────────────────
frames = []

for frame_idx in range(len(BDP_LEVELS)):
    visible_bdp = BDP_LEVELS[:frame_idx + 1]

    fig, (ax_pln, ax_eur) = plt.subplots(1, 2, figsize=FIG_SIZE, sharey=True)
    fig.patch.set_facecolor(BG_COLOR)

    for ax, data, means, stds, color, fill, title in [
        (ax_pln, pln_data, pln_means, pln_stds, PLN_COLOR, PLN_FILL, "PLN (floating)"),
        (ax_eur, eur_data, eur_means, eur_stds, EUR_COLOR, EUR_FILL, "EUR + SGP"),
    ]:
        ax.set_facecolor(BG_COLOR)
        ax.set_xlim(-100, 5200)
        ax.set_ylim(0, y_max)
        ax.set_xlabel("BDP (PLN)", fontsize=11)
        ax.set_title(title, fontsize=13, fontweight="bold")
        ax.grid(True, alpha=0.2)

        # Scatter individual seeds
        for bdp in visible_bdp:
            if bdp in data:
                seeds = data[bdp]
                jitter = np.random.default_rng(bdp).uniform(-30, 30, len(seeds))
                ax.scatter(np.full_like(seeds, bdp) + jitter, seeds,
                          color=color, alpha=0.15, s=8, zorder=2, edgecolors="none")

        # Mean line + std band
        vis_bdp_arr = np.array([b for b in visible_bdp if b in means])
        vis_means = np.array([means[b] for b in vis_bdp_arr])
        vis_stds = np.array([stds[b] for b in vis_bdp_arr])

        if len(vis_bdp_arr) > 1:
            ax.plot(vis_bdp_arr, vis_means, color=color, linewidth=2, zorder=4)
            ax.fill_between(vis_bdp_arr, vis_means - vis_stds, vis_means + vis_stds,
                           color=fill, alpha=0.15, zorder=3)

    ax_pln.set_ylabel("Adoption (%)", fontsize=11)

    # PLN critical point annotation (when BDP=500 is visible)
    if 500 in visible_bdp and 500 in pln_means:
        ax_pln.axvline(500, color=CRIT_COLOR, linestyle="--", linewidth=1.5, alpha=0.7, zorder=5)
        ax_pln.text(600, y_max * 0.92, r"BDP$_c$ = 500",
                   fontsize=10, color=CRIT_COLOR, fontweight="bold", zorder=6)

    # EUR SGP annotation (when enough points show flatness)
    if frame_idx >= 8:
        ax_eur.text(2500, y_max * 0.85, "SGP fiscal\nceiling",
                   fontsize=10, color=EUR_COLOR, fontweight="bold",
                   ha="center", alpha=0.7, zorder=6,
                   bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                            edgecolor=EUR_COLOR, alpha=0.5))

    # Frame counter
    fig.text(0.5, 0.01, f"BDP = {visible_bdp[-1]:,} PLN",
            ha="center", fontsize=11, fontweight="bold", color="#555555")

    plt.tight_layout(rect=[0, 0.04, 1, 1])

    # Render to PIL
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=DPI, facecolor=BG_COLOR)
    plt.close(fig)
    buf.seek(0)
    img = Image.open(buf).copy()
    buf.close()
    frames.append(img)

# Hold frames
all_frames = []
for _ in range(HOLD_START):
    all_frames.append(frames[0].copy())
all_frames.extend(frames)
for _ in range(HOLD_END):
    all_frames.append(frames[-1].copy())

# ── Save GIF ────────────────────────────────────────────────────────────────
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

all_frames[0].save(
    OUTPUT_PATH,
    save_all=True,
    append_images=all_frames[1:],
    duration=int(1000 / FPS),
    loop=0,
    optimize=True,
)

size_mb = os.path.getsize(OUTPUT_PATH) / (1024 * 1024)
print(f"Saved {OUTPUT_PATH} ({len(all_frames)} frames, {size_mb:.1f} MB)")
