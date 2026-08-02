"""
Shared visual identity + charting helpers for the Rent Radar study.
Import once per notebook:  import style ; style.setup()
Everything here exists so every chart in the project looks like one system:
same palette, readable fonts, no overlapping text, and clear "which way is good"
signposting on the charts where direction matters.
"""
from __future__ import annotations
import os
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.patheffects import withStroke
import seaborn as sns

# ---------------------------------------------------------------- brand palette
# Sampled directly from the Indian Institute of Technology Mandi logo.
GREEN   = "#00943E"   # forest green mountain
GREEN_L = "#20A255"   # lighter green
ORANGE  = "#E67817"   # orange ridge
BLUE    = "#0094E0"   # blue swoosh
CHARCOAL= "#4D4948"   # gate / body text
INK     = "#2E2A29"   # near-black for headings
GREY    = "#8A8887"   # muted labels
GREY_L  = "#D8D6D5"   # gridlines / fills
PAPER   = "#FFFFFF"
PAPER2  = "#F6F7F7"   # panel background

# Ordered categorical palette (max contrast, colour-blind aware ordering)
CATEGORICAL = [BLUE, ORANGE, GREEN, "#8E5AA8", "#C0392B", GREY, GREEN_L, "#B8860B"]
# Good vs bad accents (used sparingly, never as the only signal)
GOOD = GREEN
BAD  = "#C0392B"

# Continuous maps
SEQ_BLUE  = sns.light_palette(BLUE,   as_cmap=True)
SEQ_GREEN = sns.light_palette(GREEN,  as_cmap=True)
SEQ_ORANGE= sns.light_palette(ORANGE, as_cmap=True)
DIVERGING = sns.diverging_palette(28, 205, s=80, l=45, as_cmap=True)  # orange<->blue

FIG_DIR = os.path.join(os.path.dirname(__file__), "..", "figures")


def setup():
    """Apply the project-wide matplotlib / seaborn theme."""
    sns.set_theme(style="whitegrid")
    mpl.rcParams.update({
        "figure.figsize": (10, 5.8),
        "figure.dpi": 110,
        "savefig.dpi": 150,
        "savefig.bbox": "tight",
        "font.family": "DejaVu Sans",
        "font.size": 12,
        "axes.titlesize": 15,
        "axes.titleweight": "bold",
        "axes.titlecolor": INK,
        "axes.labelsize": 12,
        "axes.labelcolor": CHARCOAL,
        "axes.edgecolor": GREY_L,
        "axes.linewidth": 1.0,
        "axes.grid": True,
        "grid.color": GREY_L,
        "grid.alpha": 0.7,
        "grid.linewidth": 0.7,
        "xtick.color": CHARCOAL,
        "ytick.color": CHARCOAL,
        "text.color": CHARCOAL,
        "legend.frameon": False,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "figure.autolayout": False,
    })
    sns.set_palette(CATEGORICAL)


def save(fig, name: str):
    """Save a figure into ../figures as PNG. Returns the path."""
    os.makedirs(FIG_DIR, exist_ok=True)
    path = os.path.join(FIG_DIR, name if name.endswith(".png") else name + ".png")
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    return path


# ------------------------------------------------------------- annotation tools
def title(ax, headline, sub=None):
    """Two-line title: bold headline sits well clear of a muted subtitle."""
    ax.set_title(headline, loc="left", pad=30 if sub else 10,
                 fontsize=14.5, fontweight="bold", color=INK)
    if sub:
        ax.annotate(sub, xy=(0, 1.015), xycoords="axes fraction",
                    fontsize=10.5, color=GREY, ha="left", va="bottom")


def direction_badge(ax, better="higher", where="upper right"):
    """Small pill that states which direction is good on this chart."""
    arrow = "▲" if better == "higher" else "▼"
    txt = f"{arrow}  {better} = better"
    colour = GOOD
    locs = {
        "upper right": (0.98, 0.96, "right", "top"),
        "upper left": (0.02, 0.96, "left", "top"),
        "lower right": (0.98, 0.06, "right", "bottom"),
        "lower left": (0.02, 0.06, "left", "bottom"),
    }
    x, y, ha, va = locs[where]
    ax.annotate(txt, xy=(x, y), xycoords="axes fraction", ha=ha, va=va,
                fontsize=10.5, fontweight="bold", color="white",
                bbox=dict(boxstyle="round,pad=0.4", fc=colour, ec="none", alpha=0.92))


def callout(ax, xy, text, xytext=None, color=None, fontsize=10.5):
    """Arrow + boxed note pointing at a data point. Keeps text off the data."""
    color = color or ORANGE
    xytext = xytext or (xy[0], xy[1])
    ax.annotate(
        text, xy=xy, xytext=xytext, textcoords="data", fontsize=fontsize,
        color=INK, ha="left", va="center",
        bbox=dict(boxstyle="round,pad=0.35", fc="white", ec=color, lw=1.3, alpha=0.95),
        arrowprops=dict(arrowstyle="-|>", color=color, lw=1.6,
                        connectionstyle="arc3,rad=0.15"),
        zorder=20,
    )


def note(ax, text, where="lower right"):
    """Free-floating insight note anchored to a corner (no arrow)."""
    locs = {
        "lower right": (0.98, 0.04, "right", "bottom"),
        "lower left": (0.02, 0.04, "left", "bottom"),
        "upper right": (0.98, 0.96, "right", "top"),
        "upper left": (0.02, 0.96, "left", "top"),
        "center right": (0.98, 0.5, "right", "center"),
        "center left": (0.02, 0.5, "left", "center"),
    }
    x, y, ha, va = locs.get(where, locs["lower right"])
    ax.annotate(text, xy=(x, y), xycoords="axes fraction", ha=ha, va=va,
                fontsize=10, color=CHARCOAL, style="italic",
                bbox=dict(boxstyle="round,pad=0.4", fc=PAPER2, ec=GREY_L, lw=1))


def bar_labels(ax, fmt="{:.0f}", horizontal=False, pad=3, color=INK, fontsize=10):
    """Put value labels directly on bars so no legend / gridline reading is needed."""
    for c in ax.containers:
        ax.bar_label(c, fmt=fmt.format if callable(fmt.format) else fmt,
                     padding=pad, color=color, fontsize=fontsize, fontweight="bold")


def rupee(x, _=None):
    """Axis formatter: 1200000 -> Rs 12.0L, 55000 -> Rs 55k."""
    x = float(x)
    if abs(x) >= 1e7:
        return f"₹{x/1e7:.1f}Cr"
    if abs(x) >= 1e5:
        return f"₹{x/1e5:.1f}L"
    if abs(x) >= 1e3:
        return f"₹{x/1e3:.0f}k"
    return f"₹{x:.0f}"


def watermark(fig, text="The Outliers  ·  Rent Radar"):
    """Subtle team footer, bottom-left of the figure."""
    fig.text(0.005, 0.005, text, fontsize=8, color=GREY_L, ha="left", va="bottom")
