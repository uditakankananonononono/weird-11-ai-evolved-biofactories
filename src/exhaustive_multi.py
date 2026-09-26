#!/usr/bin/env python3
"""W11 exhaustive multi-condition evaluation of pool v1 (design note: pool v1 has
2 blocks/target = 4 genomes; exhaustive enumeration strictly dominates the locked
(mu=24,60-gen) EA on this pool - the EA scaffold is retained for pool v2+.
Recorded before inspection in results, per honest-method rule.)"""
import json, sys, itertools
sys.path.insert(0, 'src')
from search_ea_multi import fitness_multi, CONDS, get_model, POOL

out = {'note': 'exhaustive over pool v1 (4 genomes/target); fitness = nominal x min battery retention',
       'targets': {}}
for tid in ['14BDO','ISOBUTANOL','LYCOPENE']:
    get_model(tid)
    blocks = list(POOL[tid]['blocks'])
    rows = []
    for bits in itertools.product([False,True], repeat=len(blocks)):
        g = dict(zip(blocks, bits))
        f, mr = fitness_multi(tid, g)
        rows.append({'genome': g, 'fitness': round(f,4), 'min_retention': round(mr,3),
                     'battery_pass_80': mr >= 0.8})
        print(tid, g, 'fit', round(f,4), 'minret', round(mr,3), flush=True)
    out['targets'][tid] = rows
json.dump(out, open('results/exhaustive_multi.json','w'), indent=1)
print('written results/exhaustive_multi.json')
