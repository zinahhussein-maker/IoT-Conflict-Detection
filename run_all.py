"""Regenerates every number and figure of Section VIII (v2 simulator).
Usage: python run_all.py   -> results/results.json, results/fig14.png, fig15.png, fig16.png"""
import json, time, os
import numpy as np
from scipy.stats import wilcoxon
from far_iot.experiment import run_single
from far_iot.environment import build_invariants, initial_state, env_auto_transitions
from far_iot.shield import VerifyGate

os.makedirs("results", exist_ok=True)
SEEDS, T = range(20), 800
METHODS = ["random", "static", "ahp", "farid_nogate", "static_shield", "farid_shield", "farid_verify"]
R = {}

def agg(rs, key):
    v = np.array([r[key] for r in rs]); return {"mean": float(v.mean()), "std": float(v.std()),
        "min": float(v.min()), "max": float(v.max()), "nonzero": int((v > 1e-12).sum()), "values": v.tolist()}

def table(tag, **kw):
    out = {}
    for m in METHODS:
        rs = [run_single(m, seed=s, T=T, **kw) for s in SEEDS]
        out[m] = {k: agg(rs, k) for k in ["SVR", "SVR_door", "SVR_humid", "SVR_fan_heater", "regret",
                  "max_owner_override_rate", "gate_intervention_rate", "deferred_rate", "n_conflicts",
                  "total_nonconflicting_applied", "total_nonconflicting_dropped"]}
        print(tag, m, round(out[m]["SVR"]["mean"], 3), round(out[m]["regret"]["mean"], 3), flush=True)
    return out

t0 = time.time()
R["main"] = table("main")                                            # v2 default: non-conflicting rules applied and gated
R["ungated_noncf"] = table("ungated", gate_nonconflicting=False)     # non-conflicting rules bypass the gate
R["old_scope"] = table("old", apply_nonconflicting=False)            # previous scope: only conflict winners applied
R["strict"] = {m: {k: agg([run_single(m, seed=s, T=T, strict_block=True) for s in SEEDS], k) for k in ["SVR", "SVR_door", "SVR_humid", "regret", "deferred_rate"]}
               for m in ["farid_shield", "static_shield"]}

# statistics: exact paired Wilcoxon signed-rank tests (zero differences discarded), one-sided Shield > Verify,
# Holm-Bonferroni over the two scenario-level tests
def exact(a, b, alt):
    d = np.array(a) - np.array(b); d = d[d != 0]
    return (float(wilcoxon(d, alternative=alt, method="exact").pvalue) if len(d) else 1.0), int(len(d))
R["stats"] = {}
for key, name in [("SVR_door", "door_trap"), ("SVR_humid", "humid_trap"), ("SVR", "overall")]:
    p, n = exact(R["main"]["farid_shield"][key]["values"], R["main"]["farid_verify"][key]["values"], "greater")
    R["stats"][name] = {"p_exact": p, "n_nonzero_pairs": n}
ps = sorted([(R["stats"]["door_trap"]["p_exact"], "door_trap"), (R["stats"]["humid_trap"]["p_exact"], "humid_trap")])
for k, (p, name) in enumerate(ps):
    R["stats"][name]["p_holm"] = min(1.0, max(p * (2 - j) for j, (p, _) in enumerate(ps[:k + 1])))
p, n = exact(R["main"]["static_shield"]["SVR"]["values"], R["main"]["farid_shield"]["SVR"]["values"], "two-sided")
R["stats"]["static_shield_vs_farid_shield"] = {"p_exact": p, "n_nonzero_pairs": n}
print("stats", R["stats"], flush=True)

# ablation 1: drift (regret), 5 seeds per point
DR = [0.0, 0.25, 0.5, 1.0, 2.0]
R["drift"] = {"rates": DR}
for m in ["static", "farid_nogate", "farid_shield", "farid_verify"]:
    R["drift"][m] = [float(np.mean([run_single(m, seed=s, T=T, drift_rate=d)["regret"] for s in range(5)])) for d in DR]
    R["drift"][m + "_std"] = [float(np.std([run_single(m, seed=s, T=T, drift_rate=d)["regret"] for s in range(5)])) for d in DR]
print("drift done", flush=True)

# ablation 2: invariant count (SVR), 5 seeds
R["invcount"] = {}
for m in ["farid_nogate", "farid_shield", "farid_verify"]:
    R["invcount"][m] = [float(np.mean([run_single(m, seed=s, T=T, n_invariants=k)["SVR"] for s in range(5)])) for k in [1, 2, 3, 4]]
print("invcount", R["invcount"], flush=True)

# ablation 3: Verify lookahead latency vs horizon (median of 2000 calls per horizon)
inv = build_invariants(); s0 = initial_state(); act = {"door_lock": "LOCKED"}
R["latency_ms"] = {}
for h in range(1, 13):
    g = VerifyGate(inv, bounded_horizon=h, env_transitions=env_auto_transitions())
    ts = []
    for _ in range(2000):
        a = time.perf_counter(); g._reachable_safe(s0, act); ts.append((time.perf_counter() - a) * 1e3)
    R["latency_ms"][h] = float(np.median(ts))
print("latency", R["latency_ms"], flush=True)
R["runtime_s"] = time.time() - t0
json.dump(R, open("results/results.json", "w"), indent=1)

import plots  # draws Figs. 14-16 from results/results.json
print("done", R["runtime_s"])
