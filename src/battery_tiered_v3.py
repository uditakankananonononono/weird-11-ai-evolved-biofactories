#!/usr/bin/env python3
"""W11 pool-v3 TIERED battery evaluation (amendment 2026-09-27 10:04 IST 3A, locked pre-evaluation).
Mild {GLC_PERT_MINUS20, GLC_PERT_PLUS20, O2_PERT_MINUS50}: retention vs nominal, hard leg >=0.8 each.
Severe {GLC_LOW, GLC_MID, ANAEROBIC, GLYCEROL, ACETATE}: r_k = v_p,k / v_p,k^max (pool frontier,
max over 64 genomes, same target), hard leg >=0.8 each. R_tiered = 0.5*R_pert + 0.5*R_shift.
H3: best-by-nominal vs best-by-R_tiered per target; locked fallback Mann-Whitney if 0-vs-0 pass."""
import cobra, json, itertools, sys
sys.path.insert(0, 'src')
from search_ea_fast import get_model, POOL

BATT = json.load(open('data/condition_battery.json'))
BIOMASS = 'BIOMASS_Ec_iML1515_core_75p37M'
HOST_BLOCKS = ['ko_ackApta', 'ko_pflB', 'ko_ldhA', 'cofeed_glycerol', 'ko_adhE', 'ko_tpiA']
MILD = ['GLC_PERT_MINUS20', 'GLC_PERT_PLUS20', 'O2_PERT_MINUS50']
SEVERE = ['GLC_LOW', 'GLC_MID', 'ANAEROBIC', 'GLYCEROL', 'ACETATE']
CONDS = [dict(id='GLC_AEROBIC', bounds=BATT['base_condition']['bounds'])] + BATT['battery']

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
    m.reactions.get_by_id('LDH_D').bounds = (0,0) if genome.get('ko_ldhA') else (0,1000)
    m.reactions.get_by_id('EX_glyc_e').lower_bound = -4.0 if genome.get('cofeed_glycerol') else 0.0
    m.reactions.get_by_id('ALCD2x').bounds = (0,0) if genome.get('ko_adhE') else (-1000,1000)
    m.reactions.get_by_id('TPI').bounds = (0,0) if genome.get('ko_tpiA') else (-1000,1000)

def flux_cond(m, prod, cond):
    with m:
        for ex, b in BATT['base_condition']['bounds'].items():
            m.reactions.get_by_id(ex).lower_bound = b
        for ex, b in cond['bounds'].items():
            m.reactions.get_by_id(ex).lower_bound = b
        bio = m.reactions.get_by_id(BIOMASS)
        bio.lower_bound, bio.upper_bound = 0.0, 1000.0
        m.objective = bio
        g = m.slim_optimize()
        if g != g or g <= 0: return 0.0
        bio.lower_bound = bio.upper_bound = 0.5 * g
        m.objective = m.reactions.get_by_id(prod)
        p = m.slim_optimize()
        return float(p) if (p == p and p and p > 0) else 0.0

out = {}
for tid in ['14BDO','ISOBUTANOL','LYCOPENE']:
    m, prod = get_model(tid)
    blocks = list(POOL[tid]['blocks'])
    genomes = [dict(zip(HOST_BLOCKS, hb)) | dict(zip(blocks, tb))
               for hb in itertools.product([False,True], repeat=len(HOST_BLOCKS))
               for tb in itertools.product([False,True], repeat=len(blocks))]
    # per-genome condition fluxes
    F = []  # F[i][cond] = flux
    for gi, g in enumerate(genomes):
        with m:
            apply(m, tid, g)
            row = {}
            for cond in CONDS:
                row[cond['id']] = flux_cond(m, prod, cond)
        F.append(row)
        if gi % 16 == 0: print(tid, gi, 'genomes done', flush=True)
    frontier = {c: max(F[i][c] for i in range(len(genomes))) for c in SEVERE}
    scored = []
    for i, g in enumerate(genomes):
        nom = F[i]['GLC_AEROBIC']
        mild_ret = {k: (F[i][k]/nom if nom > 0 else 0.0) for k in MILD}
        sev_r = {k: (F[i][k]/frontier[k] if frontier[k] > 0 else 0.0) for k in SEVERE}
        R_pert = sum(mild_ret.values())/len(MILD)
        R_shift = sum(sev_r.values())/len(SEVERE)
        mild_pass = all(v >= 0.8 for v in mild_ret.values())
        sev_pass = all(v >= 0.8 for v in sev_r.values())
        scored.append({'genome': g, 'nominal': round(nom,4),
                       'mild_retention': {k: round(v,4) for k,v in mild_ret.items()},
                       'severe_relative': {k: round(v,4) for k,v in sev_r.items()},
                       'R_pert': round(R_pert,4), 'R_shift': round(R_shift,4),
                       'R_tiered': round(0.5*R_pert + 0.5*R_shift,4),
                       'mild_leg_pass': mild_pass, 'severe_leg_pass': sev_pass,
                       'battery_pass': mild_pass and sev_pass})
    scored.sort(key=lambda r: -r['R_tiered'])
    best_tiered = scored[0]
    best_nominal = max(scored, key=lambda r: r['nominal'])
    for s in scored:
        g = s['genome']
        s['K_het'] = (4 + int(bool(g.get('routeA_kgd'))) + int(bool(g.get('routeB_sucd')))) if tid=='14BDO' else None
    bt, bn = best_tiered, best_nominal
    diverge = (bt['genome'] != bn['genome']) and (bt['R_tiered'] - bn['R_tiered'] >= 0.10)
    out[tid] = {'frontier_severe': {k: round(v,4) for k,v in frontier.items()},
                'n_pass': sum(1 for s in scored if s['battery_pass']),
                'best_by_R_tiered': bt, 'best_by_nominal': bn,
                'diverge_3A': diverge,
                'rma_winner': next((s for s in scored if s['battery_pass'] and s['K_het'] is not None and s['K_het'] <= 4), None) if tid=='14BDO' else None,
                'top5': scored[:5], 'all_scored': scored}
    print(tid, 'pass:', out[tid]['n_pass'], 'best R_tiered:', best_tiered['R_tiered'], flush=True)

json.dump({'amendment':'2026-09-27 10:04 IST 3A pool-v3 tiered battery (locked pre-evaluation)',
           'mild': MILD, 'severe': SEVERE, 'results': out},
          open('results/battery_tiered_v3.json','w'), indent=1)
print('written results/battery_tiered_v3.json')
