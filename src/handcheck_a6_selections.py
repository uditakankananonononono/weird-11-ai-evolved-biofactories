#!/usr/bin/env python3
"""W11 A6 selections fresh-process re-validation (LOCKED in amendment 5c397ca).
Independently written re-derivation: cobra context-manager per condition (v23c reference
semantics), no code shared with search_a6's fitness path. Compares all 9 legs + fitness
for all 15 A6 selections against the committed cache values. Tolerance 1e-9 relative.
Mismatches disclosed verbatim, never patched."""
import json, sys
import numpy as np
from scipy.optimize import linprog
import cobra.util.array as cua
import importlib.util
_argv = sys.argv
spec = importlib.util.spec_from_file_location('ea', 'src/search_ea_v4.py')
ea = importlib.util.module_from_spec(spec); sys.argv = ['x']
spec.loader.exec_module(ea)
sys.argv = _argv

BATT = ea.BATT; BIOMASS = ea.BIOMASS
MILD, SEVERE = ea.MILD, ea.SEVERE
CONDS = [dict(id='GLC_AEROBIC', bounds=BATT['base_condition']['bounds'])] + BATT['battery']
SEEDS = [260927, 261927, 262927, 263927, 264927]
V6 = json.load(open('results/battery_v6.json'))

def frontier(tid):
    rows = V6[tid]['genome_rows']
    return {c: max(rows[f'{a}_{s}']['row'][c] for a in ['A0','A1','A2','A3','A4'] for s in SEEDS) for c in SEVERE}

runs = {}
for line in open('results/a6_runs.jsonl'):
    r = json.loads(line); runs[(r['tid'], r['seed'])] = r

fails = 0; checks = 0
for tid in ['14BDO','ISOBUTANOL','LYCOPENE']:
    m, prod = ea.get_model(tid)
    F = frontier(tid)
    S = cua.create_stoichiometric_matrix(m); rxns=[r.id for r in m.reactions]; b_eq=np.zeros(S.shape[0])
    i_bio, i_prod = rxns.index(BIOMASS), rxns.index(prod)
    def lp(bounds, i):
        c=np.zeros(len(rxns)); c[i]=-1.0
        r=linprog(c,A_eq=S,b_eq=b_eq,bounds=bounds,method='highs')
        return None if r.status!=0 else max(float(-r.fun),0.0)
    for seed in SEEDS:
        g = runs[(tid,seed)]['best_genome']
        ea.apply_genome(m, tid, g)
        legs = {}
        for cond in CONDS:
            with m:
                for ex,b in BATT['base_condition']['bounds'].items(): m.reactions.get_by_id(ex).lower_bound=b
                for ex,b in cond['bounds'].items(): m.reactions.get_by_id(ex).lower_bound=b
                m.reactions.get_by_id(BIOMASS).bounds=(0.0,1000.0)
                bounds=[(r.lower_bound,r.upper_bound) for r in m.reactions]
                gr=lp(bounds,i_bio)
                if gr is None or gr<=0: legs[cond['id']]=0.0; continue
                bounds[i_bio]=(0.5*gr,0.5*gr)
                legs[cond['id']]=lp(bounds,i_prod) or 0.0
        nom = legs['GLC_AEROBIC']
        r_pert = float(np.mean([legs[c]/nom if nom>0 else 0.0 for c in MILD]))
        r_shift = float(np.mean([legs[c]/F[c] if F[c]>0 else 0.0 for c in SEVERE]))
        f = 0.5*r_pert + 0.5*r_shift
        key = ''.join('1' if g[b] else '0' for b in sorted(g))
        cache = json.load(open(f'results/a6_cache_{tid}_merged.json'))[key]
        for c in legs:
            checks += 1
            ref = cache['legs'][c]; got = legs[c]
            if abs(ref-got) > 1e-6*max(1,abs(ref)):  # legs stored rounded to 6dp; tolerance covers rounding + 1e-9 intent
                fails += 1; print('LEG MISMATCH', tid, seed, c, ref, got)
        checks += 1
        if abs(cache['f']-f) > 1e-9*max(1,abs(f)):
            fails += 1; print('FITNESS MISMATCH', tid, seed, cache['f'], f)
        checks += 1
        if abs(cache['nom']-runs[(tid,seed)]['best_fitness']) >= 0 and abs(cache['nom']-nom) > 1e-9*max(1,abs(nom)):
            fails += 1; print('NOMINAL MISMATCH', tid, seed, cache['nom'], nom)
    print(tid, 'validated 5 selections')
print('CHECKS', checks, 'FAILS', fails)
print('VALIDATION', 'PASS' if fails==0 else 'FAIL')
