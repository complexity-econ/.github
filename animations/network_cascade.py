#!/usr/bin/env python3
"""
Network cascade animation — automation spreading through a Watts-Strogatz firm network.

Generates a looping GIF showing firms transitioning:
  Traditional (gray) → Hybrid (gold) → Automated (crimson) → Bankrupt (dark gray)

Output: .github/profile/network_cascade.gif
"""

import numpy as np
import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from PIL import Image
import io
import os

# ── Parameters ──────────────────────────────────────────────────────────────
N_NODES = 200
K = 6
P = 0.10
SEED = 42
N_MONTHS = 120
HOLD_FRAMES = 15
FPS = 12
DPI = 100
FIG_SIZE = (6, 6)  # 600×600 px

# Sector shares (GUS 2024)
SECTORS = {
    "BPO/SSC":         {"share": 0.03, "readiness": 0.50, "sigma": 50.0},
    "Manufacturing":   {"share": 0.16, "readiness": 0.45, "sigma": 10.0},
    "Retail/Services": {"share": 0.45, "readiness": 0.40, "sigma": 5.0},
    "Healthcare":      {"share": 0.06, "readiness": 0.25, "sigma": 2.0},
    "Public":          {"share": 0.22, "readiness": 0.08, "sigma": 1.0},
    "Agriculture":     {"share": 0.08, "readiness": 0.12, "sigma": 3.0},
}

# Colors (GitHub dark theme)
BG_COLOR = "#0d1117"
COLORS = {
    "traditional": "#B0B0B0",
    "hybrid":      "#FFD700",
    "automated":   "#DC143C",
    "bankrupt":    "#404040",
}
EDGE_COLOR = "#1a1a2e"
TEXT_COLOR = "#c9d1d9"

# States
TRADITIONAL, HYBRID, AUTOMATED, BANKRUPT = 0, 1, 2, 3

# ── Build graph ─────────────────────────────────────────────────────────────
rng = np.random.default_rng(SEED)
G = nx.watts_strogatz_graph(N_NODES, K, P, seed=SEED)
pos = nx.kamada_kawai_layout(G)

# Assign sectors by shares
sector_names = list(SECTORS.keys())
sector_shares = np.array([SECTORS[s]["share"] for s in sector_names])
sector_shares /= sector_shares.sum()
counts = np.round(sector_shares * N_NODES).astype(int)
counts[-1] = N_NODES - counts[:-1].sum()  # fix rounding

assignments = []
for i, c in enumerate(counts):
    assignments.extend([i] * c)
rng.shuffle(assignments)

# Node attributes
sector_idx = np.array(assignments[:N_NODES])
readiness = np.array([SECTORS[sector_names[s]]["readiness"] for s in sector_idx])
sigma_vals = np.array([SECTORS[sector_names[s]]["sigma"] for s in sector_idx])
risk_profile = rng.uniform(0.3, 1.0, N_NODES)
sigma_thresh = np.minimum(1.0, 0.88 + 0.075 * np.log(sigma_vals) / np.log(10))

# Precompute adjacency for mimetic pressure
adj_list = [list(G.neighbors(n)) for n in range(N_NODES)]

# ── Cascade simulation ──────────────────────────────────────────────────────
states = np.zeros((N_MONTHS, N_NODES), dtype=int)
states[0, :] = TRADITIONAL

for m in range(1, N_MONTHS):
    prev = states[m - 1].copy()
    curr = prev.copy()

    auto_mask = (prev == AUTOMATED)
    global_auto_frac = auto_mask.sum() / N_NODES

    for i in range(N_NODES):
        if prev[i] == BANKRUPT:
            continue

        neighbors = adj_list[i]
        if len(neighbors) > 0:
            local_auto = sum(1 for n in neighbors if prev[n] == AUTOMATED) / len(neighbors)
        else:
            local_auto = 0.0

        if prev[i] == TRADITIONAL:
            if m < 30:
                prob = 0.001 * readiness[i] * risk_profile[i] * sigma_thresh[i]
            else:
                mimetic = 0.10 * local_auto + 0.06 * global_auto_frac
                prob = (risk_profile[i] * 0.015 + mimetic) * readiness[i] * sigma_thresh[i]
            if rng.random() < prob:
                curr[i] = HYBRID

        elif prev[i] == HYBRID:
            if m > 35:
                prob = 0.025 * readiness[i]
                if rng.random() < prob:
                    curr[i] = AUTOMATED

        elif prev[i] == AUTOMATED:
            if m > 40:
                if rng.random() < 0.005:
                    curr[i] = BANKRUPT

    states[m] = curr

# ── Render frames ───────────────────────────────────────────────────────────
state_colors = {
    TRADITIONAL: COLORS["traditional"],
    HYBRID: COLORS["hybrid"],
    AUTOMATED: COLORS["automated"],
    BANKRUPT: COLORS["bankrupt"],
}

frames = []

for m in range(N_MONTHS):
    fig, ax = plt.subplots(figsize=FIG_SIZE, facecolor=BG_COLOR)
    ax.set_facecolor(BG_COLOR)
    ax.set_xlim(-1.15, 1.15)
    ax.set_ylim(-1.15, 1.15)
    ax.set_aspect("equal")
    ax.axis("off")

    # Edges
    for u, v in G.edges():
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        ax.plot([x0, x1], [y0, y1], color=EDGE_COLOR, linewidth=0.3, alpha=0.3, zorder=1)

    # Nodes
    node_colors = [state_colors[states[m, i]] for i in range(N_NODES)]
    node_x = [pos[i][0] for i in range(N_NODES)]
    node_y = [pos[i][1] for i in range(N_NODES)]
    ax.scatter(node_x, node_y, c=node_colors, s=30, zorder=2, edgecolors="none")

    # HUD
    auto_count = np.sum((states[m] == AUTOMATED) | (states[m] == BANKRUPT))
    hybrid_count = np.sum(states[m] == HYBRID)
    adoption_pct = (auto_count + hybrid_count) / N_NODES * 100

    ax.text(0.02, 0.98, f"Month {m + 1:>3d}", transform=ax.transAxes,
            fontsize=12, fontweight="bold", color=TEXT_COLOR, va="top",
            fontfamily="monospace")

    ax.text(0.98, 0.98, f"Adoption: {adoption_pct:.1f}%", transform=ax.transAxes,
            fontsize=12, fontweight="bold", color=TEXT_COLOR, va="top", ha="right",
            fontfamily="monospace")

    # Progress bar
    bar_y = 0.03
    bar_h = 0.015
    bar_w = 0.96
    bar_x = 0.02
    progress = m / (N_MONTHS - 1)

    ax.add_patch(plt.Rectangle((bar_x, bar_y), bar_w, bar_h,
                                transform=ax.transAxes, facecolor="#1a1a2e",
                                edgecolor="none", zorder=5))
    ax.add_patch(plt.Rectangle((bar_x, bar_y), bar_w * progress, bar_h,
                                transform=ax.transAxes, facecolor="#DC143C",
                                edgecolor="none", zorder=6))

    # BDP shock flash at month 30
    if m == 29:
        ax.text(0.5, 0.5, "BDP SHOCK", transform=ax.transAxes,
                fontsize=28, fontweight="bold", color="#FFD700",
                ha="center", va="center", alpha=0.8,
                fontfamily="monospace", zorder=10)

    # Legend
    legend_y = 0.12
    for label, color in [("Traditional", COLORS["traditional"]),
                          ("Hybrid", COLORS["hybrid"]),
                          ("Automated", COLORS["automated"]),
                          ("Bankrupt", COLORS["bankrupt"])]:
        ax.plot([], [], "o", color=color, markersize=6, label=label)
    leg = ax.legend(loc="lower left", fontsize=8, frameon=False,
                    labelcolor=TEXT_COLOR, ncol=4,
                    bbox_to_anchor=(0.0, 0.05))

    plt.tight_layout(pad=0.5)

    # Render to PIL Image
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=DPI, facecolor=BG_COLOR)
    plt.close(fig)
    buf.seek(0)
    img = Image.open(buf).copy()
    buf.close()
    frames.append(img)

# Add hold frames at the end
for _ in range(HOLD_FRAMES):
    frames.append(frames[-1].copy())

# ── Save GIF ────────────────────────────────────────────────────────────────
output_dir = os.path.join(os.path.dirname(__file__), "..", "profile")
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "network_cascade.gif")

frames[0].save(
    output_path,
    save_all=True,
    append_images=frames[1:],
    duration=int(1000 / FPS),
    loop=0,
    optimize=True,
)

size_mb = os.path.getsize(output_path) / (1024 * 1024)
print(f"Saved {output_path} ({len(frames)} frames, {size_mb:.1f} MB)")

# Print terminal stats
final = states[-1]
print(f"Terminal: auto={np.sum(final==AUTOMATED)/N_NODES*100:.1f}%, "
      f"hybrid={np.sum(final==HYBRID)/N_NODES*100:.1f}%, "
      f"bankrupt={np.sum(final==BANKRUPT)/N_NODES*100:.1f}%, "
      f"traditional={np.sum(final==TRADITIONAL)/N_NODES*100:.1f}%")
