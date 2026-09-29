#!/usr/bin/env python3
"""W11 F2 ATP-cost screen (amendment 2026-09-29 07:26 IST, dd14bdf - locked pre-computation).
Report-only realism screen: per-design FBA solution vectors (ATPM, ATPS4rpp) for top-ten
R_tiered genomes per target at pool v3 + winners, under v23c corrected LP semantics (HiGHS,
no carried state). Reference: locked literature benchmark pathways under identical semantics."""
import json, sys
import cobra
import numpy as np
from scipy.optimize import linprog
import cobra.util.array as cua
sys.path.insert(0, 'src')
from search_ea_fast import get_model
from battery_v23c_highs import CONDS, apply_genome, BIOMASS
import benchmark_flux as bf

ATPM, ATPS = 'ATPM', 'ATPS4rpp'
BATT = json.load(open('data/condition_battery.json'))

def lp_full(S, b_eq, bounds, rxns, obj_id):
    c = np.zeros(len(rxns)); c[rxns.index(obj_id)] = -1.0
    r = linprog(c, A_eq=S, b_eq=b_eq, bounds=bounds, method='highs')
    if r.status != 0: return None, None
    return float(-r.fun), r.x

def vector_at_product_max(m, S, b_eq, rxns, prod, cond_bounds):
    with m:
        for ex, b in BATT['base_condition']['bounds'].items():
            m.reactions.get_by_id(ex).lower_bound = b
        for ex, b in cond_bounds.items():
            m.reactions.get_by_id(ex).lower_bound = b
        m.reactions.get_by_id(BIOMASS).bounds = (0.0, 1000.0)
        bounds = [(r.lower_bound, r.upper_bound) for r in m.reactions]
        g, _ = lp_full(S, b_eq, bounds, rxns, BIOMASS)
        if g is None or g <= 0: return None
        bounds[rxns.index(BIOMASS)] = (0.5*g, 0.5*g)
        p, x = lp_full(S, b_eq, bounds, rxns, prod)
        if p is None: return None
        i_atpm, i_atps = rxns.index(ATPM), rxns.index(ATPS)
        return {'v_product': p, 'v_growth_floor': 0.5*g,
                'v_ATPM': float(x[i_atpm]), 'v_ATPS4rpp': float(x[i_atps])}

# benchmark references (locked pathways, identical battery LP semantics, nominal condition)
refs = {}
for tid, build in bf.BUILDERS.items():
    m = cobra.io.read_sbml_model(bf.MODEL)
    prod = build(m)
    S = cua.create_stoichiometric_matrix(m)
    rxns = [r.id for r in m.reactions]
    b_eq = np.zeros(S.shape[0])
    res = vector_at_product_max(m, S, b_eq, rxns, prod, {})
    refs[tid] = res
    print('REF', tid, {k: round(v,6) for k,v in res.items()})

v3 = json.load(open('results/battery_tiered_v23c_highs.json'))['v3']
out = {'amendment': 'dd14bdf', 'references': refs, 'targets': {}}
for tid in ['14BDO','ISOBUTANOL','LYCOPENE']:
    rows = v3[tid]['all_scored']
    ranked = sorted(rows, key=lambda r: -r['R_tiered'])
    cutoff = ranked[9]['R_tiered']
    top = [r for r in ranked if r['R_tiered'] >= cutoff - 1e-12]
    m, prod = get_model(tid)
    S = cua.create_stoichiometric_matrix(m)
    rxns = [r.id for r in m.reactions]
    b_eq = np.zeros(S.shape[0])
    designs = []
    for r in top:
        apply_genome(m, tid, r['genome'])
        per_cond, flag_parts = {}, []
        for cond in CONDS:
            res = vector_at_product_max(m, S, b_eq, rxns, prod, cond['bounds'])
            if res is None: per_cond[cond['id']] = None; continue
            per_cond[cond['id']] = res
        nom = per_cond.get('GLC_AEROBIC')
        flag = False
        if nom and nom['v_product'] > 1e-9 and refs[tid]['v_product'] > 1e-9:
            atpm_at_lb = nom['v_ATPM'] <= 6.86 + 1e-9
            ratio = nom['v_ATPS4rpp'] / nom['v_product']
            ref_ratio = refs[tid]['v_ATPS4rpp'] / refs[tid]['v_product']
            flag = atpm_at_lb and ratio > 1.5 * ref_ratio
            nom['atps_per_product'] = ratio; nom['ref_ratio'] = ref_ratio; nom['atpm_at_lb'] = atpm_at_lb
        designs.append({'genome': r['genome'], 'R_tiered': r['R_tiered'], 'nominal': r['nominal'],
                        'flag_F2': flag, 'conditions': per_cond})
    out['targets'][tid] = {'n_designs': len(designs), 'n_flagged': sum(d['flag_F2'] for d in designs),
                           'designs': designs}
    print(tid, 'designs:', len(designs), 'flagged:', out['targets'][tid]['n_flagged'])
json.dump(out, open('results/f2_atp_screen.json','w'), indent=1)
print('written results/f2_atp_screen.json')
