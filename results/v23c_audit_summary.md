# pool-v2/v3 corrected-semantics HiGHS re-eval - audit summary (amendment 70a6872, 2026-09-28)
HEADLINE: committed GLPK-era pool-v2/v3 battery numbers RE-STAND essentially completely.
## Pass counts (superseded -> repaired): ALL IDENTICAL
v2: 14BDO 16->16, ISOBUTANOL 18->18, LYCOPENE 18->18. v3: 14BDO 32->32, ISOBUTANOL 60->60, LYCOPENE 22->22.
## Frontier legs: NO differences >5e-3 anywhere (all 6 era-targets, 5 legs each).
## best_R_tiered: identical everywhere (v2 1.0/1.0/1.0; v3 0.9938/0.9997/1.0).
## argmax coincidence: v3 all True (unchanged); v2 14BDO True->False, v2 ISOBUTANOL True->False, v2 LYCOPENE True.
  Flips are tie-level: nominal-best and R-best genomes share the same nominal to full printed precision
  (14BDO 6.4956 both; ISOBUTANOL 6.4975 both); R-best has R_tiered 1.0 vs nominal-best 0.9492/0.9923.
## v3 per-genome: pass SETS identical (symdiff 0 all targets); R_tiered max|diff| 0.0/0.0/0.00010; 0/768 genomes differ >1e-4.
## Validations (amendment-locked):
(a) structural hand check: 54/54 leg values (6 era-targets x 9 conditions, independently written code) match 1e-9.
(b) v2 nominals vs exhaustive_nominal_v2.json: reference file has only 6 rows/target (5 with genomes) - it is a
    sample, not exhaustive; ALL 15 comparable values match EXACTLY (diff 0.0000). Coverage gap disclosed verbatim.
(c) v3 nominals vs committed GLPK-era: 256/256 x3 targets match within 1e-9 - ZERO suspected artifact cells.
(d) HiGHS deterministic by construction (exported LP, scipy linprog, no carried state).
## Downstream re-derivations (amendment reporting set):
- H2 tail-only candidate: corrected R_tiered 0.8023 (committed 0.768). Severe retentions 0.41-0.67 confirmed
  (GLC_LOW 0.427, GLC_MID 0.6745, ANAEROBIC 0.4139, ACETATE 0.5075; GLYCEROL 1.0). Claim "does not survive the
  tiered battery" STANDS; the R_tiered value needs an explicit supersession diff in the paper.
- H2-RMA falsification (10:04 amendment): STANDS. Pass sets identical; committed K_het consistent
  (1 route bit = K_het 5, 2 bits = 6); no battery-passing 14BDO design with K_het <= 4.
- H3 at v3: STANDS (coincide True x3, rank-1 difference 0.0000).
- H3 at v2: CHANGES. Committed text: "best-by-nominal and best-by-R_tiered coincide in all three targets (3/3)".
  Repaired: coincide in 1/3 (lycopene only); at 14BDO/isobutanol the nominal-best genome is NOT battery-optimal
  (R_tiered 0.9492/0.9923 vs 1.0) at tied nominal. This is tie-level evidence FOR the robust-selection principle
  at pool 64 - direction is favorable, but the paper's "degenerate at this pool size / honest negative" sentence
  must be corrected explicitly, not silently.
## Paper touch points: line ~106 v2/v3 paragraph (H3-at-64 sentence; 0.768 -> 0.8023), limitations caveat (8)
  ("not re-evaluated... proposed as follow-up" -> re-evaluated, numbers re-stand, two tie-level coincidence flips).
