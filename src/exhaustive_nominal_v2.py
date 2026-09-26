#!/usr/bin/env python3
"""W11 pool-v2 exhaustive NOMINAL evaluation (amendment 23:09 IST; battery deferred
pending metric-redesign amendment). Fitness = product flux at g=0.5, GLC_AEROBIC."""
import cobra, json, itertools, sys
sys.path.insert(0, 'src')
from search_ea_fast import get_model, POOL

BIOMASS = 'BIOMASS_Ec_iML1515_core_75p37M'
HOST_BLOCKS = ['ko_ackApta', 'ko_pflB', 'ko_ldhA', 'cofeed_glycerol']

def apply(m, tid, genome):
    if tid == '14BDO':
        m.reactions.get_by_id('BDO1').bounds = (0,1000) if genome.get('routeA_kgd') else (0,0)
        m.reactions.get_by_id('BDO1B').bounds = (0,1000) if genome.get('routeB_sucd') else (0,0)
    elif tid == 'ISOBUTANOL':
        m.reactions.get_by_id('IBUTDH').bounds = (0,1000) if genome.get('adh_nadh') else (0,0)
        m.reactions.get_by_id('IBUTDHP').bounds = (0,1000) if genome.get('adh_nadph') else (0,0)
    elif tid == 'LYCOPENE':
        m.reactions.get_by_id('DXPS').lower_bound = 1.0 if genome.get('dxs_push') else 0.0
        m.reactions.get_by_id('IPDDI').lower_bound = 0.5 if genome.get('idi_push') else 0.0
    m.reactions.get_by_id('ACKr').bounds = (0,0) if genome.get('ko_ackApta') else (-1000,1000)
    m.reactions.get_by_id('PTAr').bounds = (0,0) if genome.get('ko_ackApta') else (-1000,1000)
    m.reactions.get_by_id('PFL').bounds = (0,0) if genome.get('ko_pflB') else (0,1000)
    m.reactions.get_by_id('LDH_D').bounds = (0,0) if genome.get('ko_ldhA') else (-1000,1000)
    m.reactions.get_by_id('EX_glyc_e').lower_bound = -4.0 if genome.get('cofeed_glycerol') else 0.0

def flux(tid, genome):
    m, prod = get_model(tid)
    with m:
        apply(m, tid, genome)
        bio = m.reactions.get_by_id(BIOMASS)
        bio.lower_bound, bio.upper_bound = 0.0, 1000.0
        m.objective = bio
        g = m.slim_optimize()
        if g != g or g <= 0: return 0.0, 0.0
        bio.lower_bound = bio.upper_bound = 0.5 * g
        m.objective = m.reactions.get_by_id(prod)
        p = m.slim_optimize()
        return (float(p) if (p == p and p and p > 0) else 0.0), float(g)

out = {}
for tid in ['14BDO','ISOBUTANOL','LYCOPENE']:
    get_model(tid)
    blocks = list(POOL[tid]['blocks'])
    rows = []
    for host_bits in itertools.product([False,True], repeat=len(HOST_BLOCKS)):
        for tgt_bits in itertools.product([False,True], repeat=len(blocks)):
            g = dict(zip(HOST_BLOCKS, host_bits)) | dict(zip(blocks, tgt_bits))
            f, gm = flux(tid, g)
            rows.append({'genome': g, 'flux': round(f,4), 'growth_max': round(gm,4)})
    rows.sort(key=lambda r: -r['flux'])
    out[tid] = rows[:5] + [{'...': f"total {len(rows)} genomes"}]
    print(tid, 'best:', rows[0]['flux'], rows[0]['genome'], flush=True)
    print(tid, 'worst:', rows[-2]['flux'], flush=True)
json.dump({'amendment':'23:09 IST pool v2','metric':'nominal g=0.5 pFBA-equal FBA','results':out},
          open('results/exhaustive_nominal_v2.json','w'), indent=1)
print('written results/exhaustive_nominal_v2.json')
