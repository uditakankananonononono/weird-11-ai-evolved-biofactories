import sys, json, random
sys.path.insert(0,'src')
exec(open('src/battery_tiered_v2.py').read().split('out = {}')[0])
random.seed(260927)
targets = {
 '14BDO': ({'ko_ackApta':False,'ko_pflB':True,'ko_ldhA':False,'cofeed_glycerol':True,'routeA_kgd':False,'routeB_sucd':True},
           {'routeA_kgd':True,'routeB_sucd':False}),
 'ISOBUTANOL': ({'ko_ackApta':False,'ko_pflB':True,'ko_ldhA':False,'cofeed_glycerol':True,'adh_nadh':True,'adh_nadph':False},
                {'adh_nadh':True,'adh_nadph':False}),
 'LYCOPENE': ({'ko_ackApta':False,'ko_pflB':False,'ko_ldhA':False,'cofeed_glycerol':True,'dxs_push':False,'idi_push':True},
              {'dxs_push':True,'idi_push':True}),
}
out = {}
for tid,(best, bench_extra) in targets.items():
    m, prod = get_model(tid)
    with m:
        apply(m, tid, best)
        nom_best = flux_cond(m, prod, CONDS[0])
    bench = {k: False for k in HOST_BLOCKS}; bench.update(bench_extra); bench['cofeed_glycerol'] = True
    with m:
        apply(m, tid, bench)
        nom_bench = flux_cond(m, prod, CONDS[0])
    # random null (nominal, pool-v2 space, 1000 genomes seed 260927)
    keys = list(best.keys())
    rmax = 0.0
    for _ in range(1000):
        g = {k: random.random()<0.5 for k in keys}
        with m:
            apply(m, tid, g)
            rmax = max(rmax, flux_cond(m, prod, CONDS[0]))
    out[tid] = {'best_poolv2_nominal_cofeed': round(nom_best,4), 'benchmark_route_nominal_cofeed': round(nom_bench,4),
                'E_cofeed': round(nom_best/nom_bench,4) if nom_bench>0 else None,
                'random_null_best_nominal_1000': round(rmax,4), 'exhaustive_best_nominal': round(nom_best,4),
                'exhaustive_ge_random': nom_best >= rmax}
    print(tid, out[tid], flush=True)
json.dump({'amendment':'2026-09-27 10:04 IST (descriptive, no gate)','seed':260927,'results':out}, open('results/ecofeed_rebaseline_null.json','w'), indent=1)
