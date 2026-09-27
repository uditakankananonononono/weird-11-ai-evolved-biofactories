# FBA sensitivity of the three battery winners (queue #4, amendment 13:33 IST)
Data: results/h_fba_sensitivity.json. Grid: biomass fraction {0.4,0.5,0.6} x glycerol uptake {-2,-4} x glucose base {-8,-10} (12 cells/target). Survival = still passes both hard legs (severe legs vs committed pool-v3 frontiers - see PRE-REGISTRATION note 13:34).
## Results
- 1,4-BDO winner: survives 6/12 cells. Isobutanol: 8/12. Lycopene: 10/12.
- The mild leg NEVER fails (min mild retention 1.0 in all 36 cells): moderate glucose/oxygen perturbations scale flux proportionally and the winners are insensitive to the locked constants there.
- All failures concentrate in the harshest combined cell (biomass 0.6 + reduced feeds) on the SEVERE leg vs the committed frontier (worst: 14BDO sev_min 0.646).
## Reading
The winners are robust to the FBA assumptions one at a time and degrade gracefully; the simultaneous worst-case (high forced growth + throttled feeds) erodes severe-shift standing, and lycopene's co-feed+idi design is the most assumption-stable (10/12). This bounds the robustness claims: battery survival holds across single-parameter perturbations, not under the stacked worst case.
