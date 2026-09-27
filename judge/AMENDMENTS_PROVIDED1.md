# W11 AMENDMENT QUEUE - PROVIDED ROUND 1 (locked 2026-09-27 10:29 IST, pre-execution)
Source: judge/round_provided1_verdict_whatsapp.txt (her 10:27:30 paste, wamid...QzY1NwA=). All 20 weaknesses mapped. Nothing below executed before this lock. Status: QUEUED (not started) / PARTIAL (some evidence exists, extension needed) / LANDED (already in paper). Judge dissents that conflict with her verified directives are NOT adopted (standing rule).

| # | Weakness | Planned change | Status |
|---|----------|----------------|--------|
| 1 | Search novelty unclear | Add unique algorithmic component: constraint-aware mutation operators + diversity-preserving (novelty) search; pre-register before compute | QUEUED |
| 2 | Toy search space | Quantify: total architecture count, explored fraction, solution diversity at pool v3 (N=256) | LANDED (D1-a, results/amendment_d1_descriptive.json/.md; co-feed-carrying disclosed) |
| 3 | Simulation != validation | Tier 1-4 confidence framework (math feasibility / enzyme availability / known precedent / validation candidate) | PARTIAL - tiered survival battery exists; extend to prediction-confidence tiers |
| 4 | FBA assumptions | Sensitivity analysis: uptake rates, O2, biomass constraints, maintenance energy; solutions must survive | QUEUED |
| 5 | Robustness definition | Single locked definition: environment count, min retention threshold, penalty function | LANDED (D1-c canonical R_tiered definition, documentation-only) |
| 6 | Optimize model not organism | Biological realism filters: reject impossible enzyme burdens, unrealistic ATP costs, unavailable cofactors | QUEUED |
| 7 | No benchmark vs existing methods | Benchmark vs OptKnock/OptGene/OptFlux + random + greedy, same targets/constraints/runtime | PARTIAL - random-search null DONE (E^cofeed: random recovers optimum at pool 64, reported honestly); external tools subject to availability |
| 8 | No ablation | Remove robustness objective / diversity / constraint penalties; measure performance loss | QUEUED |
| 9 | Architectures need interpretation | Per-architecture rationale: why reactions, metabolic logic, trade-offs | PARTIAL - motif analysis in paper; extend per-architecture |
| 10 | Only three products | Add 4th chemical class (amino acid / organic acid / pharma precursor) | QUEUED |
| 11 | No cross-organism generalization | Test principle transfer on E. coli + yeast models | QUEUED |
| 12 | Overfit targets | Hold-out target: search on 2 products, test principles on 3rd | QUEUED |
| 13 | No random-search significance | 100 random searches: best fitness, robustness, diversity | LANDED (D2, results/amendment_d2_randomnull.json: random subsets hit passers at rate 0.69-1.0 at B=12, ~1.0 at B>=48; space easy at pool v3 - search-triviality disclosed) |
| 14 | Runtime not evaluated | Report CPU hours, generations, population size, convergence curves | PARTIAL+ - D1-b: all 15 runs converged before final 10 gens; CPU-hour logging gap recorded + mandated |
| 15 | No uncertainty estimation | Monte Carlo FBA / ensemble / parameter sampling | QUEUED |
| 16 | "AI" overstated | Define representation, search policy, objective, learning component; remove vague AI language | QUEUED (paper text pass) |
| 17 | No wet-lab connection | Prioritized experimental shortlist (candidates only, no experiments) | QUEUED |
| 18 | Constraints may bias | Compare unrestricted vs biologically constrained search; show realism gain | QUEUED |
| 19 | Strongest contribution hidden | FOLDBACK: reframe headline as "a computational evolutionary framework discovers robust metabolic design principles under conflicting biological objectives" in next paper revision | NOTED for next revision |
| 20 | Reproducibility package | Release bundle: model files, seeds, reaction libraries, benchmark definitions, generated architectures | PARTIAL - repo structured; formal bundle queued |

Execution order (next heartbeats): cheap analyses first (#2, #13-ext, #14, #5), then filters/ablation (#6, #8, #18), then new compute (#1, #4, #10-12, #15), paper passes (#16, #19, #3, #9, #17, #20). Each compute item gets its own pre-registered amendment before evaluation.

## PROVIDED CRITIQUE #2 MERGE (locked 2026-09-27 10:32 IST, pre-execution)
Source: judge/round_provided2_verdict_whatsapp.txt (10:31:07, wamid...MUMzRQA=). 18 weaknesses deduped against round 1: 9 merge into existing items, 9 NEW below. Gate stays MET 1 of 1 provided; these extend the same queue.

Merged (no new item): R2#3->#7 (+convergence speed/cost metrics), R2#4->#4 (+reaction-bound and biomass-equation perturbations), R2#5->#13 (+shuffled-fitness null), R2#8->#5 (+justify the 8 battery conditions), R2#9->#9, R2#11->#10, R2#13->#8 (+no-adaptive-mutation arm), R2#14->#2 (+exploration efficiency), R2#16->#15.

| # | Weakness (R2) | Planned change | Status |
|---|---------------|----------------|--------|
| 21 | "AI" overstated, option B | Add a learning component: RL search policy OR GNN/surrogate model OR learned mutation prioritization (option A reframe already covered by #16/#19) | QUEUED |
| 22 | Novel search operators | Topology-aware mutations, enzyme-cost-aware evolution, thermodynamics-guided evolution, adaptive mutation rates (extends #1) | QUEUED |
| 23 | Statistical confidence | 50-100 independent seeds: mean, variance, CIs, convergence curves (extends #14) | QUEUED |
| 24 | Objectives incomplete | Multi-objective optimization: enzyme burden, ATP cost, toxicity, redox balance, genetic stability (extends #6) | QUEUED |
| 25 | No comparison with known engineered strains | Benchmark vs published engineered strains/designs: predicted yield, pathway complexity, robustness | QUEUED |
| 26 | Host generalization beyond E. coli/yeast | Add cyanobacteria / Corynebacterium / another microbial chassis (extends #11) | QUEUED |
| 27 | Premature convergence | Population-diversity tracking + multi-run convergence analysis (extends #14) | QUEUED |
| 28 | No interpretability framework | Design explanation report per architecture: pathway diagram, flux changes, rationale, predicted bottlenecks (extends #9) | QUEUED |
| 29 | Novelty not quantified | Novelty score: reaction edit distance, pathway topology distance, KEGG similarity, literature overlap | QUEUED |
