# W11 AMENDMENT QUEUE - PROVIDED ROUND 1 (locked 2026-09-27 10:29 IST, pre-execution)
Source: judge/round_provided1_verdict_whatsapp.txt (her 10:27:30 paste, wamid...QzY1NwA=). All 20 weaknesses mapped. Nothing below executed before this lock. Status: QUEUED (not started) / PARTIAL (some evidence exists, extension needed) / LANDED (already in paper). Judge dissents that conflict with her verified directives are NOT adopted (standing rule).

| # | Weakness | Planned change | Status |
|---|----------|----------------|--------|
| 1 | Search novelty unclear | Add unique algorithmic component: constraint-aware mutation operators + diversity-preserving (novelty) search; pre-register before compute | QUEUED |
| 2 | Toy search space | Quantify: total architecture count, explored fraction, solution diversity at pool v3 (N=256) | QUEUED (cheap analysis) |
| 3 | Simulation != validation | Tier 1-4 confidence framework (math feasibility / enzyme availability / known precedent / validation candidate) | PARTIAL - tiered survival battery exists; extend to prediction-confidence tiers |
| 4 | FBA assumptions | Sensitivity analysis: uptake rates, O2, biomass constraints, maintenance energy; solutions must survive | QUEUED |
| 5 | Robustness definition | Single locked definition: environment count, min retention threshold, penalty function | PARTIAL - battery pre-registered in 3A amendment; formalize |
| 6 | Optimize model not organism | Biological realism filters: reject impossible enzyme burdens, unrealistic ATP costs, unavailable cofactors | QUEUED |
| 7 | No benchmark vs existing methods | Benchmark vs OptKnock/OptGene/OptFlux + random + greedy, same targets/constraints/runtime | PARTIAL - random-search null DONE (E^cofeed: random recovers optimum at pool 64, reported honestly); external tools subject to availability |
| 8 | No ablation | Remove robustness objective / diversity / constraint penalties; measure performance loss | QUEUED |
| 9 | Architectures need interpretation | Per-architecture rationale: why reactions, metabolic logic, trade-offs | PARTIAL - motif analysis in paper; extend per-architecture |
| 10 | Only three products | Add 4th chemical class (amino acid / organic acid / pharma precursor) | QUEUED |
| 11 | No cross-organism generalization | Test principle transfer on E. coli + yeast models | QUEUED |
| 12 | Overfit targets | Hold-out target: search on 2 products, test principles on 3rd | QUEUED |
| 13 | No random-search significance | 100 random searches: best fitness, robustness, diversity | PARTIAL - random null done at pool 64 (trivial); extend to 100 runs at pool v3 |
| 14 | Runtime not evaluated | Report CPU hours, generations, population size, convergence curves | PARTIAL - ea_runs.jsonl logs exist; formal curves queued |
| 15 | No uncertainty estimation | Monte Carlo FBA / ensemble / parameter sampling | QUEUED |
| 16 | "AI" overstated | Define representation, search policy, objective, learning component; remove vague AI language | QUEUED (paper text pass) |
| 17 | No wet-lab connection | Prioritized experimental shortlist (candidates only, no experiments) | QUEUED |
| 18 | Constraints may bias | Compare unrestricted vs biologically constrained search; show realism gain | QUEUED |
| 19 | Strongest contribution hidden | FOLDBACK: reframe headline as "a computational evolutionary framework discovers robust metabolic design principles under conflicting biological objectives" in next paper revision | NOTED for next revision |
| 20 | Reproducibility package | Release bundle: model files, seeds, reaction libraries, benchmark definitions, generated architectures | PARTIAL - repo structured; formal bundle queued |

Execution order (next heartbeats): cheap analyses first (#2, #13-ext, #14, #5), then filters/ablation (#6, #8, #18), then new compute (#1, #4, #10-12, #15), paper passes (#16, #19, #3, #9, #17, #20). Each compute item gets its own pre-registered amendment before evaluation.
