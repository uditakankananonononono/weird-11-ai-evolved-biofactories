# H3 honest negative on pool v1 + battery-design finding (2026-09-26 22:17 IST)

Exhaustive multi-condition evaluation (results/exhaustive_multi.json; enumeration
strictly dominates the locked EA on the 4-genome pool v1): NO genome passes the
locked 80%-retention battery. Best min-retention: 14BDO 0.175 (all genomes
identical - blocks irrelevant under GLC_LOW limitation), ISOBUTANOL 0.176,
LYCOPENE 0.27 (dxs_push only).

FINDING: the 80% bar is unsatisfiable BY CONSTRUCTION on severe nutrient shifts.
GLC_LOW supplies 2 mmol/gDW/h glucose vs 10 nominal; carbon balance caps a C4
product at ~1-2 mmol/gDW/h vs nominal 5.27 (retention ceiling ~0.2-0.3 < 0.8).
The benchmark engineered routes fail identically. The battery therefore gives no
selection gradient and H3 (multi-condition selection > single-condition) is
untestable as locked. Same flaw class as W02's unwinnable-by-construction
benchmark, caught at first evaluation.

H2 positive preserved: 14BDO tail-only architecture (native GABA-shunt feed, no
heterologous upstream route) matches the full Genomatica route's nominal flux
(5.267 mmol/gDW/h) - a non-obvious minimal architecture absent from Yim 2011.

REDIRECT (user rule: ask ChatGPT on problems): battery-redesign consult staged
(judge/battery_redirect_staged.md) for the post-midnight browser window; its
output locks as a dated amendment BEFORE any re-evaluation. Candidate levers for
pool v2 (to be grounded by the consult): knockout blocks (ackA-pta, pflB),
co-utilization feeds, ATP-maintenance reduction, transporter variants.
