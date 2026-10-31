"""Medium has no tables, so render the case table as a light-theme image."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parent
SURFACE, INK, INK2, RULE = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
plt.rcParams.update({"font.family": "Helvetica Neue", "figure.facecolor": SURFACE, "text.parse_math": False})

def table(name, header, rows, widths, title, height_per_row=0.62):
    fig = plt.figure(figsize=(13, 1.3 + height_per_row * (len(rows) + 1)))
    ax = fig.add_axes([0.02, 0.02, 0.96, 0.96])
    ax.axis("off")
    n = len(rows) + 1
    ax.set_xlim(0, 1)
    ax.set_ylim(0, n + 0.9)
    ax.text(0, n + 0.45, title, fontsize=15, weight="bold", color=INK, va="center")
    xs = [sum(widths[:i]) for i in range(len(widths))]
    for x, h in zip(xs, header):
        ax.text(x, n - 0.5, h, fontsize=12.5, weight="bold", color=INK2, va="center")
    ax.plot([0, 1], [n - 1, n - 1], color=INK, lw=1.2)
    for i, row in enumerate(rows):
        y = n - 1.5 - i
        for j, (x, cell) in enumerate(zip(xs, row)):
            ax.text(x, y, cell, fontsize=12.5, color=INK, va="center", weight="bold" if j == 0 else "normal")
        ax.plot([0, 1], [y - 0.5, y - 0.5], color=RULE, lw=0.8)
    fig.savefig(OUT / name, dpi=200)
    plt.close(fig)

table("table-cases.png",
      ["Case", "Check the question needs", "Reversal network", "Control network"],
      [["Delivery", "Average by zone and zone mix", "NW-4127: average falls, both zones slower", "NW-2863: average falls, both zones faster"],
       ["Complaints", "Rate per shipment, not only count", "NW-7351: count up, rate 4% to 3%", "NW-1594: count up, rate 4% to 6%"],
       ["Contribution", "Credits, one row per invoice", "NW-6208: net $30K to $20K", "NW-3916: net $30K to $35K"],
       ["Refunds", "Policy by promised date, weather out", "NW-5472: 3 shipments, $60", "NW-8045: 6 shipments, $120"]],
      [0.13, 0.29, 0.30, 0.28], "Four cases, each with a reversal network and a control network")
print("ok")
