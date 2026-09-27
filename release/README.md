# W11 reproducibility release bundle (queue #20)

Contents per the 16:31 IST locked amendment; MANIFEST.json carries sha256 for every file.

## Reproduce pool-v4 EA
python3 src/search_ea_v4.py <targets> <arms> <seeds>
(targets: 14BDO,ISOBUTANOL,LYCOPENE; arms: A0-A4; seeds: 260927+1000i, i=0..9; resumable, appends results/ea_v4_runs.jsonl)

## Reproduce FBA benchmarks
See src/benchmark_flux.py (builders + BASE medium) and data/condition_battery.json.
