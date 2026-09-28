# Hand check: v23 HiGHS "repaired" 0.0 legs (2026-09-28 18:40 IST)
Ordered by main 18:34 before any paper fold-in of v2/v3 supersession.

## Verdict: the v23 0.0 legs are an ADAPTATION ARTIFACT, not validated truth.
- Original battery_tiered_v2.py flux_cond UNPINS biomass first: bio.bounds=(0,1000); objective=biomass;
  g = true per-condition max growth; then floor biomass = 0.5*g; then maximize product.
- battery_v23_highs.py flux_cond omits the unpin. get_model() returns the model with BIOMASS pre-pinned at
  0.5*nominal-aerobic-gmax (=0.4385 for ISOBUTANOL). Its "g" solve is therefore only a feasibility check of
  that pin: where the pin is infeasible (GLC_LOW, ANAEROBIC, ACETATE - low/poor carbon cannot sustain
  0.5*aerobic-nominal growth) it returns 0.0; where feasible it re-pins at 0.5*pin = 0.25*nominal,
  which is NOT the original floor (0.5*true per-condition g).
- Independent fresh-process re-derivation (src/handcheck_v23_leg0.py, scipy/HiGHS, genome = v2 ISOBUTANOL
  best_by_R_tiered) reproduced the v23 cache EXACTLY on feasible legs (GLC_MID 4.982247; O2_PERT_MINUS50
  10.283396 = nominal 10.2834) and confirmed GLC_LOW/ANAEROBIC/ACETATE fail only the 0.4385 pin feasibility.
- Consequence: n_pass sup->rep (16/18/18/32/60/22 -> 0) and the "GLPK nonzero legs were artifact" direction
  are WITHDRAWN. Neither committed GLPK numbers nor v23 HiGHS numbers are validated for severe legs.
- Also affected: v23 feasible-leg floors (0.25*nominal instead of 0.5*true-g) => GLC_MID/GLYCEROL/mild-leg
  values in battery_tiered_v23_highs.json are not original-semantics either.
## Open: does cohort battery_v6.py share this flaw? Its 100% validation was nominal-only. CHECK NEXT.
## Next: corrected re-eval requires a NEW locked amendment (superseding dbd0b8c) replicating original
## semantics (unpin -> true g -> 0.5g floor) under HiGHS, pre-registered before computation.
