# 3B held-out target: 3-hydroxypropionate (locked amendment 2026-09-27 10:04 IST 3B)
Data: results/h_3hp_holdout.json. Script: src/battery_3hp.py (MCR1/MCR2 per locked formulas; 64 host-lever genomes, exhaustive; tiered battery identical; severe frontier within the 3-HP pool).
## Result: WIN_3B = FALSE - falsified per the locked rule, no loosening
- 6/64 genomes pass both hard legs. Nominal max 10.911 mmol/gDW/h.
- Motif M = {cofeed_glycerol, ko_pflB}: pass-with-M 0, pass-without-M 6, fail-with-M 16, fail-without-M 42. One-tailed Fisher p = 1.0. H0,3B NOT rejected: the specific M architecture of the three primary targets' winners does NOT generalize to 3-HP.
## The informative split (positive content)
The motif decomposes: ALL 6 passers carry cofeed_glycerol (supply lever - replicates the primary targets' necessity pattern on a held-out target with a different chemistry class and cofactor demand), while ZERO carry ko_pflB (the conservation pairing is target-specific; PFL carries anaerobic pyruvate flux the NADPH-hungry MCR route cannot spare - frontier ANAEROBIC 4.28 vs GLYCEROL 5.07). So the generalizable principle is "unlock carbon supply first"; the specific knockout pairing is not portable. Reported verbatim; H3's live arm closes as a falsification with a sharpened transferable core.
