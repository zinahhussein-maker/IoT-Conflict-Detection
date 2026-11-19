"""Draws Figs. 14-16 from results/results.json (called by run_all.py; can also be run alone)."""
import json
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
R = json.load(open("results/results.json"))
METHODS = ["random", "static", "ahp", "farid_nogate", "static_shield", "farid_shield", "farid_verify"]
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": "#888", "axes.grid": True, "grid.color": "#e6e6e6", "grid.linewidth": 0.6, "axes.axisbelow": True})
BLUE, GRAY = "#2a78d6", "#9a9a94"
labels = {"random": "Random", "static": "Static", "ahp": "AHP", "farid_nogate": "No gate", "static_shield": "Static +\nShield",
          "farid_shield": "FAR-IoT\nShield", "farid_verify": "FAR-IoT\nVerify"}
cols = [GRAY, GRAY, GRAY, GRAY, GRAY, BLUE, BLUE]
fig, ax = plt.subplots(2, 1, figsize=(3.5, 4.4))
for a, key, title in [(ax[0], "SVR", "(a) Safety-violation rate (lower is better)"), (ax[1], "regret", "(b) Resolution regret (lower is better)")]:
    mu = [R["main"][m][key]["mean"] for m in METHODS]; sd = [R["main"][m][key]["std"] for m in METHODS]
    lo = [min(s, m) for m, s in zip(mu, sd)]                      # error bars clipped at zero
    a.bar(range(len(METHODS)), mu, yerr=[lo, sd], color=cols, width=0.7, capsize=2, error_kw={"elinewidth": 0.7, "ecolor": "#555"})
    top = max(m + s for m, s in zip(mu, sd))
    for i, (v, s) in enumerate(zip(mu, sd)):
        a.text(i, v + s + top * 0.02, f"{v:.3f}", ha="center", va="bottom", fontsize=5.5, color="#333")
    a.set_ylim(0, top * 1.15)
    a.set_xticks(range(len(METHODS))); a.set_xticklabels([labels[m] for m in METHODS], fontsize=5.8)
    a.set_title(title, fontsize=7.5); a.grid(axis="x", visible=False)
fig.tight_layout(); fig.savefig("results/fig14.png", dpi=300)

DR = R["drift"]["rates"]
fig, a = plt.subplots(figsize=(3.5, 2.6))
for m, c, mk, lab in [("static", "#2a78d6", "o", "Static"), ("farid_nogate", "#eb6834", "s", "No gate"),
                      ("farid_shield", "#1baf7a", "^", "FAR-IoT Shield"), ("farid_verify", "#eda100", "D", "FAR-IoT Verify")]:
    a.plot(DR, R["drift"][m], color=c, marker=mk, ms=4, lw=1.5, label=lab)
a.set_xlabel("Drift rate"); a.set_ylabel("Resolution regret"); a.set_ylim(0, 0.3)
a.legend(fontsize=6, frameon=False, ncol=2, loc="upper center", bbox_to_anchor=(0.5, 1.02))
fig.tight_layout(); fig.savefig("results/fig15.png", dpi=300)

fig, a = plt.subplots(figsize=(3.5, 2.4))
hs = sorted(int(h) for h in R["latency_ms"]); a.plot(hs, [R["latency_ms"][str(h)] for h in hs], color=BLUE, marker="o", ms=4, lw=1.5)
a.set_xlabel("Lookahead horizon H"); a.set_ylabel("Median latency per check (ms)")
fig.tight_layout(); fig.savefig("results/fig16.png", dpi=300)
