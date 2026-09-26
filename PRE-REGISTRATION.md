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
