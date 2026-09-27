# weird-11-ai-evolved-biofactories — PRE-REGISTRATION (LOCKED before any data, search, or outcome run)

Locked 2026-09-26 ~16:00 IST, before any dataset download, model build, or outcome inspection. Source spec: user's WhatsApp 3:57:02 PM IST ("AI-Evolved Biological Factories", verbatim spec archived in lane STATE.md).

## Scientific question
What design principles allow engineered cells to maintain high biochemical productivity while remaining metabolically stable? Can a computational evolutionary search, starting from a target output rather than an existing pathway, discover non-obvious biological architectures that match or exceed known engineered pathways under multi-condition robustness criteria?

## Scope (locked)
- IN SCOPE: computational design-search over metabolic architectures (enzyme combinations, pathway structures, regulatory feedback motifs, transport steps, resource-allocation strategies) evaluated inside published genome-scale metabolic models (GSMMs); evolutionary algorithm + reinforcement-learning + constraint-based (FBA/pFBA/FVA) evaluation; simulated mutation/selection across changing environments; validation of evolved designs against (a) known engineered pathways and (b) independent published experimental datasets.
- OUT OF SCOPE: wet-lab construction, DNA synthesis, genetic-manipulation protocols, or anything constituting build-phase engineering guidance. Deliverable is an in-silico candidate architecture library + mechanistic explanations. Designs are published-data analyses and simulation outputs only.

## Hypotheses (locked)
- H1 (performance): For >=2 locked target products, at least one evolved architecture achieves predicted steady-state product flux >= the best published engineered-pathway prediction for the same host GSMM under identical uptake bounds, while satisfying the locked stability criteria. Win requires beating the locked benchmark, or matching it PLUS a named proven plus point (e.g., robustness across conditions where the benchmark design fails).
- H2 (novelty): The evolved library contains architectures using reaction/enzyme combinations absent from the corresponding published engineered pathway (verified against the locked reference pathway definition), AND at least one such non-obvious architecture is mechanistically interpretable (flux-balance explanation of why it works).
- H3 (robustness principle): Architectures selected under multi-condition selection pressure retain >=80% of nominal-condition product flux across the locked condition battery at a significantly higher rate than architectures selected under single-condition pressure (locked comparison, same search budget).
- Honest negatives: any H failing its locked gate is recorded in the repo as an honest negative and the project redirects inside itself (new target, new host, new search operator) per the user's redirect-to-positive standing rule. Nothing is fabricated; no negative is published as the final result.

## Locked benchmarks and baselines
- Benchmark set locked BEFORE any search: for each target, the best published predicted/measured production for the same host organism, drawn from the literature with provenance (DOI + table/figure reference) recorded in data/benchmarks.json at download time.
- Comparator baselines: (i) the known engineered pathway evaluated in the same GSMM with identical bounds; (ii) single-condition evolutionary search (ablation for H3); (iii) random-architecture null (same evaluation budget, random valid reaction sets) for significance calibration.

## Locked evaluation metrics
- Product flux (mmol/gDW/h) at pFBA-optimal growth-constrained solution.
- Stability battery (locked before search): nutrient shifts, uptake-bound perturbations, enzyme-capacity perturbations; pass = flux retention >=80% in all battery conditions.
- Metabolic burden proxy: total heterologous enzyme demand (sum of required enzyme mass fractions under the GSMM's capacity constraints).
- Toxicity constraint: intermediate accumulation caps per the host GSMM's published bounds.
- All thresholds fixed here pre-search; no tuning after outcomes.

## Statistical gates (locked)
- 1000-seed random-architecture null per target: evolved design must exceed the 95th percentile of the null distribution on product flux AND on robustness score.
- H3 comparison: two-proportion test (evolved-multi vs evolved-single pass rate across the battery), alpha 0.05, effect size reported.
- Permutation/seed sensitivity: all searches replicated across >=5 locked random seeds; median and min reported.

## Standing program gates
40+ genuinely-executed external research tool runs (stdlib/pytest/git/latex excluded); 120+ accession-level datasets (GSMMs, reaction DBs, enzyme records, validation datasets — each accession-logged with sha256/provenance); 10+ numbered formulas in the paper; 50+ pages of pure text body (headings, diagrams, appendix, references excluded); pre-registration locked before outcome inspection (this file); honest negatives preserved; ChatGPT judge rounds FROZEN per user order 13:52 until her explicit resume.

## Panel of targets and hosts (locked BEFORE search)
To be filled by amendment BEFORE any download: 2-4 target products spanning distinct chemistry classes + 1-2 host organisms with published, validated GSMMs. Amendment will name accessions/DOIs and will itself be locked before any target-specific outcome inspection.

## Novelty lead
The primary claim is non-obvious architecture discovery (H2), not prediction accuracy. Search operators, condition batteries, and acceptance criteria are fixed here so that any discovered motif is a genuine output of the locked search, not a post-hoc rationalization.

---

# AMENDMENT A1 — Target/host panel (locked 2026-09-26 20:15 IST, BEFORE any download, model build, or target-specific outcome inspection)

## Hosts (locked)
- PRIMARY: Escherichia coli K-12 MG1655 — GSMM iML1515 (Monk et al. 2017, Nature Biotechnology 35:904-908, DOI 10.1038/nbt.3956; BiGG model id iML1515). Accession + sha256 to be ledgered at download.
- SECONDARY (H3 cross-host robustness arm only): Saccharomyces cerevisiae S288c — GSMM Yeast8 (Lu et al. 2019, Nature Communications 10:1786, DOI 10.1038/s41467-019-11581-3; SysBioChalmers/yeast-GEM repository). No literature benchmark on the yeast arm; comparative robustness only (multi- vs single-condition selection, per H3).

## Targets (locked; 3 spanning distinct chemistry classes, H1 requires >=2)
1. 1,4-butanediol (non-natural industrial diol) in E. coli. Benchmark: Yim et al. 2011, Nature Chemical Biology 7:445-452, DOI 10.1038/nchembio.580 — the Genomatica engineered pathway, re-evaluated in iML1515 under identical uptake bounds as primary quantitative comparator; published titer as provenance anchor.
2. Isobutanol (branched-chain higher alcohol) in E. coli. Benchmark: Atsumi, Hanai & Liao 2008, Nature 451:86-89, DOI 10.1038/nature06450 — keto-acid (Ehrlich-2-ketoacid) engineered pathway, same re-evaluation rule.
3. Lycopene (isoprenoid/tetraterpene) in E. coli. Benchmark: Alper, Miyaoku & Stephanopoulos 2005, Nature Biotechnology 23:612-616, DOI 10.1038/nbt1083 — systematic-knockout overproducer, same re-evaluation rule.

## Rules fixed here
- Benchmark pathway definitions (reaction lists per the cited papers) are locked in data/benchmarks.json at download time with DOI + accession provenance; any later correction is a new dated amendment.
- Uptake bounds per condition battery are locked in code BEFORE first search run and recorded with hashes.
- Random-architecture null and single-condition ablation per the main pre-registration.

# PROCESS NOTE (not a gate change): ChatGPT judge rounds resumed per user WhatsApp 2026-09-26 16:11 IST; minimum 10 rounds/project with the novelty-producing-round rule of 17:00 IST applies. The 13:52 freeze line above is historical.

## AMENDMENT 2026-09-27 09:01 IST (battery metric redesign - judge verdict foldback, locked BEFORE battery re-evaluation)
Source: battery-metric redirect consult (Gemini supplementary surface, thread https://gemini.google.com/app/dcfb44d8d7350891; verdict archived judge/round1_battery_redirect_verdict_gemini.txt). Replaces the absolute-retention battery rule (min over 9 conditions of condition/nominal >= 0.8), which is physically unsatisfiable on severe shifts (substrate-limited max yield drops), so the battery gave no selection gradient and H3 was untestable.

CONDITION CLASSIFICATION (locked; verdict examples + mechanical fill recorded): nominal = GLC_AEROBIC (denominator only). MILD perturbations = {GLC_PERT_MINUS20, GLC_PERT_PLUS20, O2_PERT_MINUS50} (verdict's "glucose +/-20%, O2 -50%" examples verbatim). SEVERE regime shifts = {GLC_LOW, GLC_MID, ANAEROBIC, GLYCEROL, ACETATE} (verdict names GLC_LOW/ANAEROBIC/GLYCEROL/ACETATE; GLC_MID filled into severe as a carbon-input regime change beyond the mild +/-20% band - fill recorded here).

TIERED METRIC (exact, locked):
- Mild leg: retention_k = v_p,k / v_p,nominal per mild condition k, with v_p at the condition-specific 50%-max-growth constraint (existing battery rule). Hard pass leg: retention_k >= 0.8 for EVERY mild k. R_pert = mean over mild retention_k.
- Severe leg: condition-relative retention r_k = v_p,k(mu_k) / v_p,k^max(mu_k), mu_k = 50% of the condition-specific FBA max growth; v_p,k^max = max over the 64 pool-v2 genomes of the SAME target under condition k (frontier-relative reading of the verdict's "maximum achievable in that condition"; fill recorded). Hard pass leg: r_k >= 0.8 for EVERY severe k. R_shift = mean over severe r_k.
- R_tiered = 0.5*R_pert + 0.5*R_shift (weights filled 50/50; verdict gave none - fill recorded).
- BATTERY PASS = both hard legs. H3's locked battery-fitness/pass uses this metric; its two-proportion test (alpha 0.05) is unchanged. Locked fallback: if both search modes pass at rate 0 (degenerate two-proportion), H3 compares mean R_tiered between selection modes by Mann-Whitney at alpha 0.05.

FALSIFICATION BRANCH: if zero of the 192 pool-v2 architectures pass both hard legs, report the pass rate and the R_tiered ranking as the outcome; do NOT loosen thresholds post hoc. The verdict's pool-expansion levers (adhE knockout; cofactor pntAB/sthA + NAD/NADP-variant dehydrogenases; anaplerotic ppc/pck/maeB) are staged as pool v3 under their own amendment if the gradient is still insufficient.

# PROCESS NOTE (supersedes): the "minimum 10 ChatGPT judge rounds" process line above is RETIRED per user WhatsApp 2026-09-27 10:00:07 ("NOT 10 ROUNDS OF CHATGPT CHECK JUST ONE WHICH I PROVIDE OK?") and settled 10:01:47 ("EACH PROJECTS NEED ONE FROM ME TO PASS"). Counted judge gate = ONE verdict she personally provides via courier. Agent-initiated rounds preserved as history, never counted. Historical text kept intact.

## AMENDMENT 2026-09-27 10:04 IST (H3 resolution 3A/3B + H2 redirect RMA + E^cofeed lock; judge verdict foldback from round_supp1, thread https://gemini.google.com/app/031d790b7ab04c00, verdict judge/round_supp1_h3_redirect_verdict_gemini.txt; locked BEFORE any pool-v3 computation, 3-HP model construction, RMA scoring, or E^cofeed evaluation)

3A POOL V3 EXPANSION (H3 rank-resolution): two new binary host levers - ko_adhE (reaction ALCD2x bounds (0,0); ethanol-overflow knockout) and ko_tpiA (reaction TPI bounds (0,0); triose-phosphate isomerase knockout). Judge suggested adhE among others and phosphate-transport blocks; PIt2r/PIt7 do not exist in iML1515 (verified) - ko_tpiA substituted as the second lever and the substitution is recorded here. Pool v3 = 8 binary levers (6 host: ko_ackApta, ko_pflB, ko_ldhA, cofeed_glycerol, ko_adhE, ko_tpiA; + 2 target-specific) = 256 genomes/target, exhaustive enumeration. Same model, conditions, tiered battery metric (09:01 lock), seed 260927.
- NULL H0,3A: at N=256, argmax(v_nominal) == argmax(R_tiered) in ALL three targets.
- WIN 3A: H0,3A rejected if in >=2 of 3 targets argmax(R_tiered) != argmax(v_nominal) AND R_tiered(argmax R_tiered) - R_tiered(argmax v_nominal) >= 0.10.
- FALSIFICATION: 0 or 1 targets diverge -> H3 search-advantage reported not earned at N=256; no post-hoc re-pooling or threshold changes.

3B HELD-OUT TARGET 3-HP (design-principle generalization): new target 3-hydroxypropionate via heterologous malonyl-CoA reductase route - MCR1 (malonyl-CoA + NADPH -> malonate semialdehyde + CoA + NADP+ + H+) and MCR2 (malonate semialdehyde + NADPH + H+ -> 3-hydroxypropionate + NADP+), plus transport + EX_3hp_e; constructed in the same iML1515 base, same 50%-max-growth battery rule. 3-HP pool = the 6 host levers only (64 genomes, no target-specific levers). Tiered battery identical; severe-leg frontier computed WITHIN the 3-HP pool.
- MOTIF M = {cofeed_glycerol ON, ko_pflB ON} (the shared architecture of the three primary targets' battery winners).
- NULL H0,3B: proportion of battery-passing 3-HP designs carrying M <= proportion among failing designs.
- WIN 3B: one-tailed Fisher exact test p < 0.05 for M enrichment among battery-passers.
- FALSIFICATION: p >= 0.05 OR zero passers (report pass count; no loosening).

H2-RMA (Robust Minimal Architecture): K_het = count of heterologous (non-native E. coli) pathway reactions ACTIVE in the design; host knockouts and uptake-bound changes (co-feed) are not enzymes and do not count. Published anchor K_het,Yim = 5 (kgd + 4hbD + CoA-transferase + aldehyde dehydrogenase + alcohol dehydrogenase per the locked data/benchmarks.json reaction list).
- NULL H0,H2: min K_het among battery-passing pool-v3 14BDO designs >= 5.
- WIN H2-RMA: exists a pool-v3 14BDO design with battery PASS (both hard legs), K_het <= 4, and nominal flux >= 0.90 x published-route nominal under identical bounds.
- FALSIFICATION: no such design; the tail-only nominal-only result stands as already reported.

E^COFEED + RANDOM NULL (descriptive, no gate): E_a^cofeed = F_a^cofeed(0.5)/F_benchmark^cofeed(0.5) computed for each target's best pool-v2 genome vs its locked benchmark route, BOTH with the cofeed_glycerol block enabled under identical bounds; reported descriptively. Random-architecture null: 1000 uniform-random pool-v2 genomes (seed 260927), compare best-of-random nominal + R_tiered against the exhaustive best; reported descriptively. Neither is a win/fail gate.

## AMENDMENT 2026-09-27 10:31 IST — D1 DESCRIPTIVE PACK (provided-verdict weaknesses #2, #14, #5; locked BEFORE any aggregation)
Source: judge/AMENDMENTS_PROVIDED1.md items 2/5/14. DESCRIPTIVE ONLY - no win/fail gates, no new hypotheses; metrics locked here before computation.
- D1-a (search-space quantification): (i) total architecture count = 2^6 host levers x 2^2 route levers = 256 per target, 768 total (constants from src/battery_tiered_v3.py HOST_BLOCKS + POOL blocks). (ii) Explored fraction: the pool-v3 tiered battery is EXHAUSTIVE (all 256 genomes/target) -> fraction 1.0 by construction; the stochastic EA runs (results/ea_runs.jsonl) logged only best genome + last-10 history, so per-run explored sets are NOT recoverable - recorded as an instrumentation limitation, with trajectory logging mandated for all future search runs. (iii) Diversity among battery-passing designs per target: mean/min/max pairwise Hamming distance over the 8 binary levers, plus lever-usage frequency (fixed vs variable levers among passers).
- D1-b (runtime/convergence): per EA run in ea_runs.jsonl: final best_flux and whether hist_last10 is flat within 1e-9 (converged before the last 10 generations) vs still improving. CPU hours were not logged - honest gap; wall-clock logging mandated for future runs. Population/generation constants (mu=24, lambda=48, 60 gen, 5 locked seeds) cited from search_design.md.
- D1-c (robustness definition consolidation, documentation only): canonical R_tiered = 0.5*R_pert + 0.5*R_shift; R_pert = mean retention over 3 mild conditions vs nominal flux; R_shift = mean ratio over 5 severe conditions vs the pool frontier (max over the 256 genomes, same target); PASS = every mild retention >= 0.8 AND every severe ratio >= 0.8; nominal = GLC_AEROBIC with biomass at 50% of the condition-specific FBA maximum. The pool v1/v2-era 9-condition min-retention rule is preserved for lineage comparisons. NO metric changed.
Output: results/amendment_d1_descriptive.json + a short results/amendment_d1_descriptive.md summary for the paper's Methods/Results update.

## AMENDMENT 2026-09-27 10:32 IST — D2 RANDOM-SEARCH NULL AT POOL V3 (provided-verdict #13 extension; locked BEFORE computation)
At pool v3 the tiered battery is exhaustive (256/256 genomes per target), so the EA is unnecessary; the judge's question becomes: how hard is the space to search by luck? Locked design: per target, evaluation budgets B in {12, 24, 48, 96} genomes; 100 uniform-random subsets (without replacement, seed 260927) of the 256; per subset record (i) whether it contains >=1 battery-passing design, (ii) the subset's best R_tiered vs the pool optimum R_tiered. Report per (target, B): hit rate over 100 subsets, and median/min of (best R_tiered / pool optimum). DESCRIPTIVE - no win gate; expected honestly to show the space is easy at this pool size (pass fractions 32/256, 60/256, 22/256), which is itself the reported finding.

## AMENDMENT 2026-09-27 12:32 IST (provided-verdict queue #6: biological realism filters - locked BEFORE filter application)
QUESTION: do the top evolved designs survive biological realism screening? Locked filters, applied to the committed all_scored pool-v3 tiered-battery results (256 designs x 3 targets), definitions grounded in project artifacts:
- F1 ENZYME BURDEN: heterologous reaction count (locked burden proxy from search_design.md) must not exceed the locked benchmark pathway's heterologous count for that target (data/benchmarks.json) by more than +1. Grounding: the benchmark is the literature-demonstrated route; needing materially more engineering than a demonstrated pathway is the burden failure the judge named. Disclosed heuristic.
- F3 COFACTOR-CONDITION CONSISTENCY: designs whose active route blocks carry NADPH-dependent steps (pool annotations, data/reaction_pool.json) AND whose ANAEROBIC severe retention is exactly 0 are flagged cofactor-fragile (no NADPH regeneration claim under anaerobiosis); flag, do not reject, because the tiered battery already scores retention.
- F2 ATP-COST SCREEN: DEFERRED - requires per-design FBA solution vectors (ATPM/ATPS fluxes) not stored in the committed results; computing them is new FBA compute queued behind this amendment; disclosed here so the deferral is not silent.
PASS RULE (report-only): per target, report how many of the top-10 (by R_tiered) survive F1, whether best_by_R_tiered and best_by_nominal survive, and the F3 flag count in the top 10. No re-ranking, no re-selection; survivals and rejections reported verbatim in Results.

## AMENDMENT 2026-09-27 12:37 IST (provided-verdict queue #8: ablation - locked BEFORE computation)
CONTEXT LOCK: at pool v3 the design space is exhaustively evaluated (256/256 per target), so EA-operator ablation measures nothing at this pool size; the operative ablation is over the SCORING components, computed by re-ranking the committed all_scored results (no new FBA). Locked arms: (A0) full R_tiered = 0.5*R_pert + 0.5*R_shift (committed); (A1) nominal-flux only (robustness objective REMOVED); (A2) R_pert only (mild-perturbation robustness); (A3) R_shift only (condition-shift robustness). Per arm per target: the winning design, and its performance measured under the FULL locked battery. PERFORMANCE LOSS (locked definition): A1-winner's worst severe-condition retention vs A0-winner's, per target; plus winner-overlap matrix across arms. Diversity/constraint-penalty ablation: DEFERRED with disclosure - these are EA-search components, inapplicable to exhaustive evaluation (search-side ablation report stands for pool v1/v2 era results already committed). PASS RULE (report-only): all numbers verbatim; if A1-winner == A0-winner on a target, "robustness objective non-binding at this pool" is the recorded outcome.

## AMENDMENT 2026-09-27 12:38 IST (provided-verdict queue #18: unrestricted vs biologically constrained search - locked BEFORE computation)
QUESTION: what does the biological constraint buy? Locked arms over the SAME pool-v3 genome space (256/target), GLC_AEROBIC nominal condition only, no new pool, no gate changes:
- CONSTRAINED (committed): growth fixed at 50% of condition FBA max, maximize product (the committed flux_cond).
- UNRESTRICTED: biomass bounds (0,1000) - no growth requirement - maximize product (biologically non-viable solutions admitted).
MEASURES (locked): per target, (i) unrestricted-best genome + its product flux; (ii) its implied growth rate (fix product at the unrestricted max, maximize biomass - zero growth = non-viable design, disclosed); (iii) whether the unrestricted winner passes the #6 F1 burden filter; (iv) its worst severe-condition retention under the committed battery. REALISM GAIN (locked definition): constrained-best nominal flux / unrestricted-best flux, plus the count of unrestricted-top-10 designs that are zero-growth or battery-failing. PASS RULE (report-only): numbers verbatim; if the constrained best equals the unrestricted best, "constraint non-binding at nominal" is the recorded outcome.

## AMENDMENT 2026-09-27 13:19 IST (provided-verdict queue #16: terminology definitions - documentation-only, locked BEFORE drafting)
DOCUMENTATION-ONLY: add a locked definitions subsection: representation, search policy, objective, learning component. The learning component is NONE (no trained or adaptive model anywhere in the pipeline) - this is stated explicitly. No compute; no claim changes; the word "AI" is not used in-body to describe the method. Title question ("AI-evolved") escalated to the user level, not edited unilaterally.

## AMENDMENT 2026-09-27 13:23 IST (provided-verdict queue #9 extension: per-architecture rationale - documentation-only, locked BEFORE drafting)
DOCUMENTATION-ONLY: per-architecture rationale subsection for the three committed battery-winning genomes (results/battery_tiered_v3.json, best_by_R_tiered per target). Every rationale traces the genome's blocks to its committed retention/flux numbers; interpretation stays at the level of the block definitions (knockout = removed overflow route; co-feed = added carbon supply; route/adi choices = committed alternative blocks). No new compute; no mechanistic claim beyond what the block definitions and committed numbers support.

## ERRATUM 2026-09-27 13:24 IST
The per-architecture rationale subsection as first committed (03b5707) stated "no single-lever genome passes both hard legs". Verification against committed results/battery_tiered_v3.json found 2+2+3 co-feed-only passers. The claim was wrong and has been corrected in-paper to the verified statement: every passer carries the glycerol co-feed (32/32, 60/60, 22/22); knockouts are optional refinements. Cause: an over-strict ad-hoc filter checked before commit; the corrected text was verified against the committed JSON before re-commit.

## AMENDMENT 2026-09-27 13:33 IST (provided-verdict queue #4: FBA sensitivity - locked BEFORE computation)
QUESTION: do the three committed battery winners survive perturbation of the locked FBA assumptions? Locked design: for each target's best_by_R_tiered genome (committed in results/battery_tiered_v3.json), re-evaluate nominal flux and R_tiered under a locked 3x2x2 grid: biomass fraction {0.4, 0.5, 0.6} x glycerol co-feed uptake {-2, -4} (only where cofeed ON) x glucose base {-8, -10}. SURVIVAL RULE (locked): a winner survives a grid cell if it still passes both hard legs in that cell; report survival fraction per target verbatim. No re-optimization of genomes; no pool changes; perturbations of the locked constants only.
