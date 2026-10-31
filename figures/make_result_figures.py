"""Result figures from results/summary.json and raw.jsonl. Light theme."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "figures"
S = json.loads((ROOT / "results/summary.json").read_text())
key = {q["qid"]: q for q in json.loads((ROOT / "runner/answer_key.json").read_text())}
raw = [json.loads(l) for l in (ROOT / "results/raw.jsonl").read_text().splitlines()]
SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
COLOR = {"FLASH": "#eb6834", "STANDARD": "#2a78d6"}
NAME = {"FLASH": "Flash", "STANDARD": "Standard"}
plt.rcParams.update({"font.family": "Helvetica Neue", "font.size": 13, "axes.edgecolor": GRID, "text.parse_math": False,
                     "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
                     "figure.facecolor": SURFACE, "axes.facecolor": SURFACE})
FOOT = "Synthetic Meridian Parcel benchmark, 31 October 2026. 5 requests per question per mode."

def clean(ax):
    for s in ["top", "right", "left"]:
        ax.spines[s].set_visible(False)
    ax.tick_params(axis="y", length=0)

def dots(ax, labels, values, ns, xmax, fmt):
    y = np.arange(len(labels))[::-1]
    for i, (yy, lab) in enumerate(zip(y, labels)):
        f, s = values["FLASH"][i], values["STANDARD"][i]
        ax.plot([f, s], [yy, yy], color=GRID, lw=3, zorder=1)
        for m, v, dy in [("FLASH", f, -0.13), ("STANDARD", s, 0.13)]:
            ax.plot([v], [yy + (dy if f == s else 0)], "o", ms=12, color=COLOR[m], mec=SURFACE, mew=2, zorder=3)
        lo, hi = sorted([(f, "FLASH"), (s, "STANDARD")])
        if abs(f - s) < xmax * 0.06:
            ax.text(max(f, s) + xmax * 0.025, yy, f"Flash {fmt(f, ns[i])}, Standard {fmt(s, ns[i])}", va="center", fontsize=11.5, color=INK)
        else:
            ax.text(lo[0] - xmax * 0.025, yy, f"{NAME[lo[1]]} {fmt(lo[0], ns[i])}", va="center", ha="right", fontsize=11.5, color=INK)
            ax.text(hi[0] + xmax * 0.025, yy, f"{NAME[hi[1]]} {fmt(hi[0], ns[i])}", va="center", fontsize=11.5, color=INK)
    ax.set_yticks(y, labels)
    ax.grid(axis="x", color=GRID, lw=0.8)
    clean(ax)

def legend(fig):
    for i, m in enumerate(["FLASH", "STANDARD"]):
        fig.text(0.70 + i * 0.12, 0.93, "●", color=COLOR[m], fontsize=16, va="center")
        fig.text(0.72 + i * 0.12, 0.93, NAME[m], color=INK, fontsize=12.5, va="center")

# Figure 2: pass rate by question level
levels = [("lookup", "Lookup questions"), ("directed", "Directed questions"), ("open", "Open questions"), ("missing", "Missing-evidence questions")]
fig, ax = plt.subplots(figsize=(12, 4.8))
vals = {m: [S["pass"][l][m]["passed"] / S["pass"][l][m]["n"] * 100 for l, _ in levels] for m in COLOR}
ns = [S["pass"][l]["FLASH"]["n"] for l, _ in levels]
dots(ax, [lab for _, lab in levels], vals, ns, 100, lambda v, n: f"{round(v * n / 100)}/{n}")
ax.set_xlim(-12, 118)
ax.set_xticks([0, 25, 50, 75, 100], ["0%", "25%", "50%", "75%", "100%"])
ax.set_xlabel("Responses that meet all four criteria")
fig.suptitle("Pass rate by question level", x=0.02, ha="left", y=0.95, fontsize=15, weight="bold", color=INK)
legend(fig)
fig.text(0.02, 0.02, FOOT, color=INK2, fontsize=10.5)
fig.tight_layout(rect=(0, 0.05, 1, 0.9))
fig.savefig(OUT / "fig2-pass-by-level.png", dpi=200)
plt.close(fig)

# Figure 3: open questions, correct conclusions out of 5
open_q = [q for q in key if key[q]["level"] == "open"]
label = {"delivery": "Delivery", "complaints": "Complaints", "contribution": "Contribution", "refunds": "Refunds"}
labels = [f"{label[key[q]['case']]}, {key[q]['network']} ({key[q]['version']})" for q in open_q]
fig, ax = plt.subplots(figsize=(12, 6))
vals = {m: [S["by_question"][q]["criteria"][m][3] for q in open_q] for m in COLOR}
dots(ax, labels, vals, [5] * len(open_q), 5, lambda v, n: f"{v}/5")
ax.set_xlim(-1.2, 6.6)
ax.set_xticks(range(6))
ax.set_xlabel("Responses with a correct, supported conclusion (criterion 4), out of 5")
fig.suptitle("Open questions: correct conclusions by network", x=0.02, ha="left", y=0.96, fontsize=15, weight="bold", color=INK)
legend(fig)
fig.text(0.02, 0.02, FOOT, color=INK2, fontsize=10.5)
fig.tight_layout(rect=(0, 0.04, 1, 0.92))
fig.savefig(OUT / "fig3-open-conclusions.png", dpi=200)
plt.close(fig)

# Figure 4: completion time by level
fig, ax = plt.subplots(figsize=(12, 5.2))
rng = np.random.default_rng(3)
yt, yl = [], []
for i, (lvl, lab) in enumerate(levels[::-1]):
    for j, m in enumerate(["FLASH", "STANDARD"]):
        ys = [r["elapsed_s"] for r in raw if r["mode"] == m and key[r["qid"]]["level"] == lvl and r["status"] == "completed"]
        yy = i * 1.0 + (0.18 if m == "STANDARD" else -0.18)
        ax.scatter(ys, yy + rng.uniform(-0.09, 0.09, len(ys)), s=22, color=COLOR[m], alpha=0.55, edgecolors="none", zorder=2)
        med = float(np.median(ys))
        ax.plot([med, med], [yy - 0.16, yy + 0.16], color=INK, lw=2.5, zorder=3)
        ax.text(med, yy + 0.2 if m == "STANDARD" else yy - 0.2, f"{med:.0f}s", ha="center",
                va="bottom" if m == "STANDARD" else "top", fontsize=10.5, color=INK)
    yt.append(i)
    yl.append(lab)
ax.set_yticks(yt, yl)
ax.set_xlabel("Completion time per request (seconds). Black tick is the median.")
ax.grid(axis="x", color=GRID, lw=0.8)
clean(ax)
fig.suptitle("Completion time by question level", x=0.02, ha="left", y=0.95, fontsize=15, weight="bold", color=INK)
legend(fig)
fig.text(0.02, 0.02, FOOT, color=INK2, fontsize=10.5)
fig.tight_layout(rect=(0, 0.05, 1, 0.9))
fig.savefig(OUT / "fig4-completion-time.png", dpi=200)
plt.close(fig)
print("ok")
