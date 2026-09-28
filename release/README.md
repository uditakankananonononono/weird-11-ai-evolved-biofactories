# W11 reproducibility release bundle (queue #20)

Contents per the 16:31 IST locked amendment; MANIFEST.json carries sha256 for every file.

## Reproduce pool-v4 EA
python3 src/search_ea_v4.py <targets> <arms> <seeds>
(targets: 14BDO,ISOBUTANOL,LYCOPENE; arms: A0-A4; seeds: 260927+1000i, i=0..9; resumable, appends results/ea_v4_runs.jsonl)

## Reproduce FBA benchmarks
See src/benchmark_flux.py (builders + BASE medium) and data/condition_battery.json.

## Reproduce the pool-v4 final battery + gate
python3 src/battery_final_v4.py
(re-evaluates the 75 primary best-genomes on the tiered battery, evaluated-set severe frontier, M-W gate + 10k-label permutation sensitivity; per-target caches results/battery_v4_<target>.json make restarts cheap)

## Fault tolerance note
search_ea_v4.py checkpoints every generation to results/ea_v4_ckpt/ and resumes bit-exactly (interrupted vs uninterrupted equivalence verified). If a run appears stuck inside the solver (no checkpoint update for tens of minutes), kill and relaunch with the same arguments: a fresh process resumes from the last generation with a cold solver basis. GLPK presolve was tested and rejected (value mismatches); the solver configuration is part of the locked protocol.
