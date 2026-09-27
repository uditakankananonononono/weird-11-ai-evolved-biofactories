# Monte Carlo FBA uncertainty (queue #15, amendment 13:35 IST)
Data: results/h_mc_fba.json. 200 draws (seed 260927), every battery uptake bound jittered U(0.8,1.2); severe legs vs committed pool-v3 frontiers.
## Results (R_tiered distribution; battery-pass fraction)
- 1,4-BDO: mean 0.9926 (SD 0.028), 5-95% [0.9485, 1.0431], passes in 92.5% of draws.
- Isobutanol: mean 0.9985 (SD 0.028), [0.9548, 1.0487], 98.0%.
- Lycopene: mean 0.9990 (SD 0.021), [0.9652, 1.0369], 100%.
## Reading
Winner robustness is not a knife-edge artifact of the locked bounds: under independent 20% parameter jitter the winners pass the full battery in 92.5-100% of draws, with lycopene again the most stable. The 7.5% failure tail for 1,4-BDO is reported verbatim - its R_tiered 1.0 at the locked point is a point estimate with a small but real sensitivity mass below the pass bar.
