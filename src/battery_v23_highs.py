#!/usr/bin/env python3
"""W11 pool-v2/v3 battery HiGHS re-evaluation (amendment 2026-09-28 18:14 IST, dbd0b8c - locked pre-computation).
Replays both exhaustive tiered batteries under the deterministic HiGHS metric (no carried solver state),
using each era's committed genome sets (all_scored rows of battery_tiered_v2/v3.json) and the era model
(search_ea_fast.get_model). Legs, frontier rule, R_tiered, thresholds unchanged.
VALIDATION NOTE (amendment wording slip disclosed): no independent v3 exhaustive-nominal file exists
(exhaustive_multi.json is pool v1); validation = (a) v2 nominals cross-checked vs exhaustive_nominal_v2.json
'flux' within 1e-9 relative, (b) v3 nominals cross-checked vs the committed v3 all_scored nominal (GLPK-era;
mismatches = suspected artifact cells, disclosed verbatim), (c) HiGHS determinism (repeat solves identical)."""
import json, os, sys, itertools
import numpy as np
from scipy.optimize import linprog
import cobra.util.array as cua
sys.path.insert(0, 'src')
from search_ea_fast import get_model, POOL

BATT = json.load(open('data/condition_battery.json'))
BIOMASS = 'BIOMASS_Ec_iML1515_core_75p37M'
MILD = ['GLC_PERT_MINUS20','GLC_PERT_PLUS20','O2_PERT_MINUS50']
SEVERE = ['GLC_LOW','GLC_MID','ANAEROBIC','GLYCEROL','ACETATE']
CONDS = [dict(id='GLC_AEROBIC', bounds=BATT['base_condition']['bounds'])] + BATT['battery']

def apply_genome(m, tid, genome):  # superset of both eras (missing keys -> open bounds, as v2)
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

def lp(S, b_eq, bounds, rxns, obj_id):
    c = np.zeros(len(rxns)); c[rxns.index(obj_id)] = -1.0
    r = linprog(c, A_eq=S, b_eq=b_eq, bounds=bounds, method='highs')
    if r.status != 0: return None
    v = -r.fun
    return float(v) if v > 0 else 0.0

def flux_cond(m, S, b_eq, rxns, prod, cond):
    with m:
        for ex, b in BATT['base_condition']['bounds'].items():
            m.reactions.get_by_id(ex).lower_bound = b
        for ex, b in cond['bounds'].items():
            m.reactions.get_by_id(ex).lower_bound = b
        bounds = [(r.lower_bound, r.upper_bound) for r in m.reactions]
        g = lp(S, b_eq, bounds, rxns, BIOMASS)
        if g is None or g <= 0: return 0.0
        bounds[rxns.index(BIOMASS)] = (0.5*g, 0.5*g)
        p = lp(S, b_eq, bounds, rxns, prod)
        return p if p else 0.0

out = {}
if os.path.exists('results/battery_tiered_v23_highs.json'):
    out = json.load(open('results/battery_tiered_v23_highs.json'))

for era, src in [('v2','results/battery_tiered_v2.json'), ('v3','results/battery_tiered_v3.json')]:
    committed = json.load(open(src))['results']
    e_out = out.setdefault(era, {})
    for tid in ['14BDO','ISOBUTANOL','LYCOPENE']:
        tkey = tid
        if tkey in e_out and e_out[tkey].get('done'): continue
        rows = committed[tid]['all_scored']
        genomes = [r['genome'] for r in rows]
        m, prod = get_model(tid)
        rxns = [r.id for r in m.reactions]
        S = cua.create_stoichiometric_matrix(m, array_type='lil').tocsc()
        b_eq = np.zeros(S.shape[0])
        t_out = e_out.setdefault(tkey, {'F': {}, 'done': False})
        F = t_out['F']
        for i, g in enumerate(genomes):
            gk = json.dumps(g, sort_keys=True)
            if gk in F: continue
            row = {}
            with m:  # genome application reverted after this genome
                apply_genome(m, tid, g)
                for cond in CONDS:
                    row[cond['id']] = flux_cond(m, S, b_eq, rxns, prod, cond)
            F[gk] = row
            if len(F) % 32 == 0:
                json.dump(out, open('results/battery_tiered_v23_highs.json','w'))
                print(era, tid, len(F), '/', len(genomes), flush=True)
        frontier = {c: max(F[json.dumps(g, sort_keys=True)][c] for g in genomes) for c in SEVERE}
        scored = []
        for g in genomes:
            gk = json.dumps(g, sort_keys=True)
            nom = F[gk]['GLC_AEROBIC']
            mild = {k: (F[gk][k]/nom if nom > 0 else 0.0) for k in MILD}
            sev = {k: (F[gk][k]/frontier[k] if frontier[k] > 0 else 0.0) for k in SEVERE}
            R_pert = sum(mild.values())/3; R_shift = sum(sev.values())/5
            scored.append({'genome': g, 'nominal': round(nom,4),
                           'mild_retention': {k: round(v,4) for k,v in mild.items()},
                           'severe_relative': {k: round(v,4) for k,v in sev.items()},
                           'R_pert': round(R_pert,4), 'R_shift': round(R_shift,4),
                           'R_tiered': round(0.5*R_pert+0.5*R_shift,4),
                           'pass': all(v >= 0.8 for v in mild.values()) and all(v >= 0.8 for v in sev.values())})
        n_pass = sum(1 for s in scored if s['pass'])
        best_R = max(scored, key=lambda s: s['R_tiered'])
        best_N = max(scored, key=lambda s: s['nominal'])
        t_out.update({'frontier_severe': {k: round(v,4) for k,v in frontier.items()},
                      'n_pass': n_pass,
                      'best_by_R_tiered': best_R, 'best_by_nominal': best_N,
                      'argmax_coincide': best_R['genome'] == best_N['genome'],
                      'all_scored': scored, 'done': True})
        json.dump(out, open('results/battery_tiered_v23_highs.json','w'))
        print(era, tid, 'DONE n_pass', n_pass, 'coincide', best_R['genome'] == best_N['genome'], flush=True)

# diff summary vs committed
diff = {}
for era, src in [('v2','results/battery_tiered_v2.json'), ('v3','results/battery_tiered_v3.json')]:
    committed = json.load(open(src))['results']
    dd = {}
    for tid in ['14BDO','ISOBUTANOL','LYCOPENE']:
        c = committed[tid]; r = out[era][tid]
        dd[tid] = {'n_pass': [c['n_pass'], r['n_pass']],
                   'frontier_sup': c['frontier_severe'], 'frontier_rep': r['frontier_severe'],
                   'best_R_sup': c['best_by_R_tiered']['R_tiered'] if 'best_by_R_tiered' in c else None,
                   'best_R_rep': r['best_by_R_tiered']['R_tiered'],
                   'argmax_coincide_rep': r['argmax_coincide']}
    diff[era] = dd
out['diff_vs_committed'] = diff
json.dump(out, open('results/battery_tiered_v23_highs.json','w'), indent=1)
print('v23 highs done')
