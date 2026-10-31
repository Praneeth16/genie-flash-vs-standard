"""Figures built from the synthetic input data only (no Genie output).
fig1-delivery-reversal.png and anim-mix-shift.gif. Light theme."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
import numpy as np

OUT = Path(__file__).resolve().parent
SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
LOCAL, REMOTE = "#1baf7a", "#6250d6"
plt.rcParams.update({"font.family": "Helvetica Neue", "font.size": 13, "axes.edgecolor": GRID,
                     "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
                     "figure.facecolor": SURFACE, "axes.facecolor": SURFACE})

def slope(ax, title, local, remote, overall, share):
    x = [0, 1]
    for vals, color, name in [(remote, REMOTE, "Remote"), (local, LOCAL, "Local")]:
        ax.plot(x, vals, color=color, lw=2.5, marker="o", ms=9, mec=SURFACE, mew=2, zorder=3)
        ax.text(1.06, vals[1], f"{name} {vals[1]:.0f} day" + ("" if vals[1] == 1 else "s"), va="center", color=INK, fontsize=12)
        ax.text(-0.06, vals[0], f"{vals[0]:.0f}", va="center", ha="right", color=INK2, fontsize=12)
    ax.plot(x, overall, color=INK, lw=2.5, ls=(0, (4, 3)), marker="D", ms=8, mec=SURFACE, mew=2, zorder=4)
    ax.text(1.06, overall[1], f"All parcels {overall[1]:.1f} days", va="center", color=INK, fontsize=12, weight="bold")
    ax.text(-0.06, overall[0], f"{overall[0]:.1f}", va="center", ha="right", color=INK, fontsize=12, weight="bold")
    ax.set_xlim(-0.35, 1.9)
    ax.set_ylim(0, 10.5)
    ax.set_xticks(x, ["September", "October"])
    ax.set_yticks([0, 2, 4, 6, 8, 10])
    ax.set_ylabel("Average delivery days")
    ax.grid(axis="y", color=GRID, lw=0.8)
    for s in ["top", "right", "left"]:
        ax.spines[s].set_visible(False)
    ax.set_title(title, loc="left", color=INK, fontsize=14, weight="bold", pad=26)
    ax.text(0, 1.03, share, transform=ax.transAxes, color=INK2, fontsize=11.5)

fig, axes = plt.subplots(1, 2, figsize=(13, 5.6))
slope(axes[0], "NW-4127: both zones get slower", [2, 3], [8, 9], [6.8, 4.2], "Local share of parcels rises from 20% to 80%")
slope(axes[1], "NW-2863: both zones get faster", [2, 1], [8, 7], [6.8, 5.8], "Local share of parcels stays at 20%")
fig.text(0.01, 0.01, "Synthetic Meridian Parcel data. Values are computed from the input tables, not from Genie.", color=INK2, fontsize=10.5)
fig.tight_layout(rect=(0, 0.04, 1, 1))
fig.savefig(OUT / "fig1-delivery-reversal.png", dpi=200)
plt.close(fig)

# Animation: local share 20% -> 80% while each zone gets one day slower.
frames = 60
def state(t):
    share = 0.2 + 0.6 * t
    lo, re = 2 + t, 8 + t
    return share, lo, re, share * lo + (1 - share) * re

fig = plt.figure(figsize=(9, 4.6))
ax_bar = fig.add_axes([0.06, 0.62, 0.88, 0.14])
ax_days = fig.add_axes([0.06, 0.16, 0.88, 0.26])

def draw(i):
    t = min(max(i - 12, 0) / (frames - 12), 1.0)
    t = 0.5 - 0.5 * np.cos(np.pi * t)
    share, lo, re, avg = state(t)
    month = "September" if t == 0 else ("October" if t == 1 else "")
    for ax in (ax_bar, ax_days):
        ax.clear()
        ax.set_facecolor(SURFACE)
    ax_bar.barh(0, share, color=LOCAL, height=0.8)
    ax_bar.barh(0, 1 - share - 0.004, left=share + 0.004, color=REMOTE, height=0.8)
    ax_bar.text(0.01, 0, f"Local {share:.0%}", va="center", color="white", fontsize=12, weight="bold")
    ax_bar.text(0.99, 0, f"Remote {1 - share:.0%}", va="center", ha="right", color="white", fontsize=12, weight="bold")
    ax_bar.set_xlim(0, 1)
    ax_bar.axis("off")
    ax_bar.set_title("Mix of 1,000 parcels" + (f" in {month}" if month else ""), loc="left", color=INK, fontsize=13, weight="bold")
    ax_days.axhline(0, color=GRID, lw=1.5)
    for x, c, name, y in [(lo, LOCAL, "Local", 0.55), (re, REMOTE, "Remote", 0.55)]:
        ax_days.plot([x], [0], "o", ms=13, color=c, mec=SURFACE, mew=2, zorder=3)
        ax_days.text(x, y, f"{name}\n{x:.1f} days", ha="center", color=INK, fontsize=11.5)
    ax_days.plot([avg], [0], "D", ms=13, color=INK, mec=SURFACE, mew=2, zorder=4)
    ax_days.text(avg, -0.95, f"All parcels\n{avg:.1f} days", ha="center", color=INK, fontsize=11.5, weight="bold")
    ax_days.set_xlim(0, 10.5)
    ax_days.set_ylim(-1.1, 1.2)
    ax_days.set_yticks([])
    ax_days.set_xticks(range(0, 11, 2))
    for s in ["top", "right", "left"]:
        ax_days.spines[s].set_visible(False)
    ax_days.set_xlabel("Average delivery days (left is faster)", color=INK2)
    fig.texts.clear()
    fig.text(0.06, 0.48, "Both zones move right. The average moves left.", color=INK2, fontsize=11.5)

anim = FuncAnimation(fig, draw, frames=frames + 24, interval=80)
anim.save(OUT / "anim-mix-shift.gif", writer=PillowWriter(fps=12), dpi=110)
print("ok")
