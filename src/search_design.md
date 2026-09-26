# W11 evolutionary search protocol (locked 2026-09-26 21:27 IST, BEFORE first search run)
Within PRE-REGISTRATION framework (metrics, battery, gates already locked). This file locks the SEARCH-side choices so they cannot be tuned post-outcome.

## Search space
- Genome per target = (a) subset of alternative-route reaction blocks from the locked reaction pool, (b) one enzyme-cap level from the locked battery's 2 levels.
- Reaction pool v1 (per target): the locked benchmark pathway (data/benchmarks.json) + literature-documented alternative route blocks with DOI provenance, recorded in data/reaction_pool.json BEFORE first run. 14BDO: route A (akg->SSA, locked) + route B (succinyl-CoA->SSA via sucD, noted in benchmarks.json step 1). ISOBUTANOL: locked keto-acid route + alternative aldehyde reduction cofactor choice (NADH vs NADPH adh variants). LYCOPENE: locked crtEBI + dxs-push on/off + idi-push on/off.
- Random-architecture null (locked gate): same pool, uniformly random valid subsets, 1000 seeds, same evaluation budget.

## Evaluation (all locked pre-search)
- Growth constraint for search fitness: biomass fixed at 50% of FBA max (envelope midpoint, chosen once here; benchmarks exist at all fractions so H1 comparisons use MATCHED fractions).
- Fitness = product flux (mmol/gDW/h) at pFBA-optimal solution under GLC_AEROBIC, growth fixed at 50% max.
- Robustness score = min over the 9-condition battery of (condition product flux / nominal product flux); pass = >=0.8 everywhere (locked battery rule).
- Burden proxy: number of heterologous reactions (count version of the locked enzyme-demand proxy for pool v1; mass-fraction version requires enzyme MW data, queued as accession work).

## Algorithm (locked)
- (mu+lambda) EA: mu=24, lambda=48, tournament k=3, uniform-ish mutation: per-gene flip p=1/pool_size; max 60 generations; 5 locked seeds {260926, 260927, 260928, 260929, 260930}; median and min reported (locked gate).
- H3 arm: identical search with fitness evaluated on GLC_AEROBIC ONLY (single-condition) vs full-battery fitness (multi = min retention * nominal flux); same budget; two-proportion test on battery pass rate, alpha 0.05.
- H1 arm: best evolved architecture per target vs locked envelope at matched growth fraction; win = exceed, or match + named proven plus point.

## Termination honesty
- If no architecture beats the envelope: honest negative, redirect in-project (new operator/pool expansion) per standing rule.
