#!/usr/bin/env python3
import cobra, json, itertools, sys
sys.path.insert(0,'src')
from search_ea_fast import get_model, POOL
from battery_tiered_v3 import apply, BATT, BIOMASS, HOST_BLOCKS
D=json.load(open('results/battery_tiered_v3.json'))['results']
def flux_unrestricted(m, prod, genome, tid):
    with m:
        for ex,b in BATT['base_condition']['bounds'].items(): m.reactions.get_by_id(ex).lower_bound=b
        apply(m,tid,genome)
        m.objective=m.reactions.get_by_id(prod)
        p=m.slim_optimize()
        p=float(p) if (p==p and p and p>0) else 0.0
        g=0.0
        if p>0:
            r=m.reactions.get_by_id(prod); r.lower_bound=r.upper_bound=p
            m.objective=m.reactions.get_by_id(BIOMASS)
            g=m.slim_optimize(); g=float(g) if g==g and g>0 else 0.0
        return p,g
out={}
for tid in ['14BDO','ISOBUTANOL','LYCOPENE']:
    m,prod=get_model(tid)
    blocks=list(POOL[tid]['blocks'])
    genomes=[dict(zip(HOST_BLOCKS,hb))|dict(zip(blocks,tb)) for hb in itertools.product([False,True],repeat=len(HOST_BLOCKS)) for tb in itertools.product([False,True],repeat=len(blocks))]
    scored=[]
    for g_ in genomes:
        p,gr=flux_unrestricted(m,prod,g_,tid)
        scored.append({"genome":g_,"unrestricted_flux":round(p,4),"implied_growth":round(gr,4)})
    top10=sorted(scored,key=lambda e:-e['unrestricted_flux'])[:10]
    best=top10[0]
    # battery worst-severe of unrestricted winner from committed all_scored (match genome)
    match=[e for e in D[tid]['all_scored'] if e['genome']==best['genome']]
    worst_sev=min(match[0]['severe_relative'].values()) if match else None
    constr_best=max(D[tid]['all_scored'],key=lambda e:e['R_tiered'])
    out[tid]={"unrestricted_best":best,"zero_growth_in_top10":sum(1 for e in top10 if e['implied_growth']<=1e-6),
      "unrestricted_best_worst_severe":worst_sev,
      "realism_gain_ratio":round(constr_best['nominal']/best['unrestricted_flux'],4) if best['unrestricted_flux']>0 else None,
      "constrained_best_nominal":constr_best['nominal']}
    print(tid,"unrestricted best:",best['unrestricted_flux'],"growth:",best['implied_growth'],"| zero-growth in top10:",out[tid]['zero_growth_in_top10'],"| gain ratio:",out[tid]['realism_gain_ratio'])
json.dump({"amendment":"2026-09-27 12:38 IST #18 unrestricted vs constrained","results":out},open('results/h_unrestricted_vs_constrained.json','w'),indent=1)
