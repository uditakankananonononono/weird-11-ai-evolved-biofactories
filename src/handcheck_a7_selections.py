#!/usr/bin/env python3
"""Locked validation for A7 selections (amendment 2026-09-29 16:45 IST): fresh-process, independently
written. Recomputes every A7 selection's 9 legs with its own implementation (cobra + per-condition
context managers; no import of search_a7/rescore scoring code) and compares against the recorded
selection_legs at stored precision (bitwise at 6dp - the maximal meaningful check at record precision,
disclosed). Mismatches disclosed verbatim, exit 2."""
import json, sys
sys.argv = ['x']
import importlib.util
spec = importlib.util.spec_from_file_location('ea', 'src/search_ea_v4.py')
ea = importlib.util.module_from_spec(spec); spec.loader.exec_module(ea)
import numpy as np, cobra.util.array as cua
from scipy.optimize import linprog

BATT = json.load(open('data/condition_battery.json'))
BIOMASS = 'BIOMASS_Ec_iML1515_core_75p37M'
CONDS = [dict(id='GLC_AEROBIC', bounds=BATT['base_condition']['bounds'])] + BATT['battery']

def legs_of(tid, genome):
    m, prod = ea.get_model(tid)
    S = cua.create_stoichiometric_matrix(m)
    rxns = [r.id for r in m.reactions]
    b_eq = np.zeros(S.shape[0])
    i_bio, i_prod = rxns.index(BIOMASS), rxns.index(prod)
    def solve(bounds, obj_i):
        c = np.zeros(len(rxns)); c[obj_i] = -1.0
        r = linprog(c, A_eq=S, b_eq=b_eq, bounds=bounds, method='highs')
        if r.status != 0: return None
        v = -r.fun
        return float(v) if v > 0 else 0.0
    out = {}
    with m:
        ea.apply_genome(m, tid, genome)
        for cond in CONDS:
            with m:
                for ex, b in BATT['base_condition']['bounds'].items():
                    m.reactions.get_by_id(ex).lower_bound = b
                for ex, b in cond['bounds'].items():
                    m.reactions.get_by_id(ex).lower_bound = b
                m.reactions.get_by_id(BIOMASS).bounds = (0.0, 1000.0)
                bounds = [(r.lower_bound, r.upper_bound) for r in m.reactions]
                g = solve(bounds, i_bio)
                if g is None or g <= 0:
                    out[cond['id']] = 0.0
                    continue
                bounds[i_bio] = (0.5 * g, 0.5 * g)
                p = solve(bounds, i_prod)
                out[cond['id']] = p if p else 0.0
    return out

checks = fails = 0
bad = []
for l in open('results/a7_runs.jsonl'):
    r = json.loads(l)
    tid = r['tid']
    got = legs_of(tid, r['best_genome'])
    for c, want in r['selection_legs'].items():
        checks += 1
        if round(got[c], 6) != want:
            fails += 1
            bad.append((tid, r['seed'], c, got[c], want))
    checks += 1
    if abs(got['GLC_AEROBIC'] - r['selection_nom']) > 1e-9 * max(1.0, abs(r['selection_nom'])):
        fails += 1
        bad.append((tid, r['seed'], 'NOMINAL', got['GLC_AEROBIC'], r['selection_nom']))
print('CHECKS', checks, 'FAILS', fails)
for b in bad[:20]: print('MISMATCH', b)
print('VALIDATION', 'PASS' if fails == 0 else 'FAIL')
sys.exit(2 if fails else 0)
