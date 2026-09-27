# W11 #18: unrestricted vs biologically constrained search (amendment 12:38 IST, locked before computation)
Per target, nominal condition, same pool-v3 space (256/target):
- 14BDO: unrestricted best flux 7.750 vs constrained best nominal 6.496 (constrained/unrestricted ratio 0.838). The unrestricted winner is growth-viable (0.4385/h) but FAILS the committed battery: worst severe-condition retention 0.4616 (<0.8). The realism gain is concrete: the unconstrained optimum overpromises 16% at nominal and collapses under condition shifts; the constrained objective trades nominal flux for a design that survives.
- ISOBUTANOL: unrestricted best 7.756 vs constrained 6.500 (ratio 0.838); unrestricted winner is battery-robust (worst severe 0.9147) - constraint non-binding on this target.
- LYCOPENE: ratio 1.0107 (constrained nominal 0.730 vs unrestricted 0.722) - difference at solver-tolerance scale; recorded as constraint non-binding at nominal, disclosed not smoothed.
- Zero-growth designs in unrestricted top-10: 0 on all targets.
Note: h_unrestricted_vs_constrained.py imports battery_tiered_v3.py, which re-executes and rewrites results/battery_tiered_v3.json; verified byte-identical to the committed file (deterministic) before this commit.
