# W11 A6 offload runbook (Kaggle / Colab / local Ryzen box)

WHAT THIS IS: pool-v4 A6 robust-fitness EA search, locked amendment 2026-09-29 07:31 IST (commit 5c397ca).
CPU-only scipy HiGHS LPs, no network at runtime, ~500MB RAM/worker. Deterministic: same env + same seeds = bit-comparable outputs, verified back on the home box by the locked fresh-process re-validation.

## Setup (5 min)
    pip install -r requirements.txt   # pinned: cobra 0.32.1, scipy 1.15.3, numpy 2.2.6, optlang 1.9.1, swiglpk 5.0.13
    tar xzf w11_a6_offload.tar.gz && cd W11

## Run (per target chunk; N workers = N cores)
    for s in 260927 261927 262927 263927 264927; do
      nice -n 10 python3 src/search_a6.py <TARGET> $s > results/a6_log_<TARGET>_$s.txt 2>&1 &
    done
<TARGET> in {14BDO, ISOBUTANOL, LYCOPENE}. Each run: 60 gens, checkpoint per generation
(results/a6_ckpt/) -> kill/resume is bit-exact. Caches (results/a6_cache_<TARGET>_*.json)
persist and are preloaded by later workers.

## Sync back (when a target's 5 seeds are done)
    results/a6_runs.jsonl            # append-only run records
    results/a6_cache_<TARGET>_*.json # per-worker caches (merged on home box)
Return via download/tarball; the home box merges, runs the locked outcome-blind
comparison + fresh-process re-validation BEFORE any paper fold-in.

## Hard rules
- Do NOT edit src/, data/, or seeds. The protocol is frozen; any change invalidates the run.
- If a number looks wrong, report it; never patch values.
- Partial chunks sync fine (checkpoints resume anywhere, including back on the home box).
