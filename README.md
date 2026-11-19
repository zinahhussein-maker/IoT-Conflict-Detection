# FAR-IoT Supplementary Code (version 2)

This package regenerates every number, table and figure of Section VIII (and the experimental
numbers quoted in the Abstract, Sections I, IX and X) of the revised manuscript. No external
dataset is required: the rule corpus is semi-synthetic and generated from documented seeds.

```bash
pip install numpy scipy matplotlib
python run_all.py        # ~5 minutes; writes results/results.json and results/fig14-16.png
python plots.py          # redraws Figs. 14-16 from results/results.json only
```

## Contents
- `far_iot/rules.py` — rule/conflict data structures and the pairwise conflict predicate.
- `far_iot/environment.py` — corpus generator (60 rules per seed, 4 owners, 10 devices, 9 events),
  including two randomized multi-step traps (door-lock/away-mode and ac/humidity), the four
  invariants, the exogenous environment transitions and the event stream.
- `far_iot/policy.py` — LinUCB (per-rule arms, 9-dimensional context, alpha = 0.8).
- `far_iot/shield.py` — ShieldGate (single-step) and VerifyGate (bounded lookahead over the four
  environment transitions; horizon H = 5 in the experiments).
- `far_iot/baselines.py` — static, AHP, random, and `static_shield` (static priority + Shield).
- `far_iot/metrics.py` — SVR (all ticks and per invariant), regret, gate-intervention and deferral
  rates, fairness (maximum share of overridden decisions borne by one owner).
- `far_iot/experiment.py` — simulation loop.
- `run_all.py`, `plots.py` — the exact experiment protocol of Section VIII.

## Changes in version 2 (alignment with the Event-B model)
1. Non-conflicting triggered rules are executed and, for gated methods, pass through the same gate
   as resolutions (Event-B `ApplyRule` / `DropRule`). Option `gate_nonconflicting=False` reproduces
   the ungated variant reported in Section VIII-A.
2. `farid_verify` executes the policy's choice if it passes the Verify check, otherwise the other
   candidate if it passes, otherwise defers the conflict (Event-B `ResolveByPolicy` /
   `FallbackResolve` / `DeferConflict`). Version 1 always preferred the highest-priority safe
   candidate, overriding a safe policy choice.
3. Per-invariant SVR, gate-intervention and deferral rates are logged.
4. Statistics use exact paired Wilcoxon signed-rank tests (zero differences discarded) with
   Holm–Bonferroni correction over the two scenario-level tests.

Option `apply_nonconflicting=False` reproduces the narrower setting (only conflict winners
applied) reported for comparison in Section VIII-A. Note that the numbers of the previous
submission were produced by an earlier code version and are superseded by those of this package.

## Seeds
Main comparisons: seeds 0–19, T = 800. Ablations: seeds 0–4. No seed selection or filtering.
