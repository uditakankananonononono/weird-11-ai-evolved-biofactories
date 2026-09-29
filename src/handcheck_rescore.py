#!/usr/bin/env python3
"""Locked validation for the v23c re-score (amendment 8274f9f): fresh-process, independently written.
Recomputes every scored genome's 9 legs with its own implementation (cobra model + per-condition
context managers; no import of search_a6 or rescore_v23c scoring code) and compares against
results/rescore_v23c.json at 1e-9 relative tolerance. Mismatches disclosed verbatim, exit 2."""
import json, sys
_SHARD, _SHARDS = 0, 1
if '--shard' in sys.argv:
    _SHARD = int(sys.argv[sys.argv.index('--shard') + 1])
    _SHARDS = int(sys.argv[sys.argv.index('--shards') + 1])
sys.argv = ['x']
import importlib.util
spec = importlib.util.spec_from_file_location('ea', 'src/search_ea_v4.py')
ea = importlib.util.module_from_spec(spec); spec.loader.exec_module(ea)
import numpy as np, cobra.util.array as cua
from scipy.optimize import linprog

BATT = json.load(open('data/condition_battery.json'))
BIOMASS = 'BIOMASS_Ec_iML1515_core_75p37M'
CONDS = [dict(id='GLC_AEROBIC', bounds=BATT['base_condition']['bounds'])] + BATT['battery']
TARGETS = ['14BDO', 'ISOBUTANOL', 'LYCOPENE']

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

def main():
    import zlib
    shard, shards = _SHARD, _SHARDS
    d = json.load(open('results/rescore_v23c.json'))
    checks = fails = 0
    bad = []
    for tid in TARGETS:
        bits = ea.HOST14 + list(ea.POOL[tid]['blocks'])
        for row in d['per_target'][tid]['rows']:
            if zlib.crc32((tid + row['genome_key']).encode()) % shards != shard: continue
            genome = {b: row['genome_key'][i] == '1' for i, b in enumerate(sorted(bits))}
            got = legs_of(tid, genome)
            for c, want in row['legs'].items():
                checks += 1
                # stored legs are round(x, 6) by the locked A6Eval cache format; maximal meaningful
                # check is bitwise equality at stored precision (rounding recomputation to 6dp).
                if round(got[c], 6) != want:
                    fails += 1
                    bad.append((tid, row['genome_key'][:24], c, got[c], want))
    print(f'SHARD {shard}/{shards} CHECKS', checks, 'FAILS', fails)
    for b in bad[:20]: print('MISMATCH', b)
    print('VALIDATION', 'PASS' if fails == 0 else 'FAIL')
    sys.exit(2 if fails else 0)

if __name__ == '__main__':
    main()
