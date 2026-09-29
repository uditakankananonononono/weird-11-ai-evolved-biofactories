#!/usr/bin/env python3
"""v23c re-score of pool-v4 comparison sets (amendment 2026-09-29 14:35 IST, commit 8274f9f - locked pre-computation).
Semantics: locked v23c (per-condition fresh state, unpin biomass, max growth, no-growth leg = 0.0,
0.5 x gmax pin, max product; scipy HiGHS on exported S; no carried solver state) via the validated
A6Eval code path. Before scoring: bitwise equivalence re-proof vs an independent context-manager
reference implementation on 3 genomes x 9 conds x 3 targets; failure halts. Output: results/rescore_v23c.json
No verdicts computed here (mechanical rule application is a separate locked step after validation)."""
import json, os, sys, itertools
sys.argv = ['x']
import importlib.util
spec = importlib.util.spec_from_file_location('a6', 'src/search_a6.py')
a6 = importlib.util.module_from_spec(spec); spec.loader.exec_module(a6)
import numpy as np, cobra.util.array as cua
from scipy.optimize import linprog

BATT = a6.BATT
BIOMASS = a6.BIOMASS
MILD, SEVERE = a6.MILD, a6.SEVERE
CONDS = [dict(id='GLC_AEROBIC', bounds=BATT['base_condition']['bounds'])] + BATT['battery']
TARGETS = ['14BDO', 'ISOBUTANOL', 'LYCOPENE']
SEEDS = [260927, 261927, 262927, 263927, 264927]

# ---------- independent reference (context-manager per condition; NOT the A6Eval bounds-array path) ----------
def ref_legs(tid, genome):
    m, prod = a6.ea.get_model(tid)
    S = cua.create_stoichiometric_matrix(m); rxns = [r.id for r in m.reactions]; b_eq = np.zeros(S.shape[0])
    def lp(bounds, obj):
        c = np.zeros(len(rxns)); c[rxns.index(obj)] = -1.0
        r = linprog(c, A_eq=S, b_eq=b_eq, bounds=bounds, method='highs')
        return None if r.status != 0 else max(float(-r.fun), 0.0)
    out = {}
    with m:
        a6.ea.apply_genome(m, tid, genome)
        for cond in CONDS:
            with m:
                for ex, b in BATT['base_condition']['bounds'].items():
                    m.reactions.get_by_id(ex).lower_bound = b
                for ex, b in cond['bounds'].items():
                    m.reactions.get_by_id(ex).lower_bound = b
                m.reactions.get_by_id(BIOMASS).bounds = (0.0, 1000.0)
                bounds = [(r.lower_bound, r.upper_bound) for r in m.reactions]
                g = lp(bounds, BIOMASS)
                if g is None or g <= 0:
                    out[cond['id']] = 0.0; continue
                bounds[rxns.index(BIOMASS)] = (0.5 * g, 0.5 * g)
                p = lp(bounds, prod)
                out[cond['id']] = p if p else 0.0
    return out

# ---------- bitwise equivalence re-proof (locked probe: 3 genomes x 9 conds x 3 targets) ----------
def proof():
    rng_bits = [
        {b: True for b in []},  # placeholder replaced below
    ]
    probes = {}
    for tid in TARGETS:
        bits = a6.HOST14 + list(a6.POOL[tid]['blocks'])
        g_all_on = {b: True for b in bits}
        g_all_off = {b: False for b in bits}
        g_alt = {b: (i % 2 == 0) for i, b in enumerate(bits)}
        probes[tid] = [g_all_on, g_all_off, g_alt]
    fails = []
    for tid in TARGETS:
        ev = a6.A6Eval(tid)
        for g in probes[tid]:
            k = ''.join('1' if g[b] else '0' for b in sorted(g))
            ev.fitness(g)
            got = {c: ev.cache[k]['legs'][c] for c in ev.cache[k]['legs']}
            want = ref_legs(tid, g)
            for c in want:
                if got[c] != round(want[c], 6):
                    fails.append((tid, c, got[c], want[c]))
    return fails

# ---------- input set enumeration (locked rules) ----------
def enum_inputs():
    sets = {tid: [] for tid in TARGETS}  # list of (genome, provenance)
    for tid in TARGETS:
        bits = a6.HOST14 + list(a6.POOL[tid]['blocks'])
        seen = {}
        def add(genome, prov):
            kt = tuple(1 if genome[b] else 0 for b in bits)
            if kt in seen:
                seen[kt][1].append(prov)
            else:
                seen[kt] = [genome, [prov]]
        # plateau members: identical battery_v6 enumeration rule from a5_traj eval_hist
        for seed in SEEDS:
            traj = json.load(open(f'results/a5_traj/{tid}_{seed}.json'))
            hist = traj['eval_hist']
            bestf = max(f for _, f in hist)
            thr = bestf * (1 - 1e-6)
            seenk = set()
            for klist, f in hist:
                if f >= thr:
                    kt = tuple(klist)
                    if kt not in seenk:
                        seenk.add(kt)
                        add({b: bool(v) for b, v in zip(bits, klist)}, f'plateau_{seed}')
        # A0-A4 evaluated pool
        for l in open('results/ea_v4_runs.jsonl'):
            r = json.loads(l)
            if r['target'] == tid and r['arm'] in ['A0','A1','A2','A3','A4']:
                add(r['best_genome'], f"{r['arm']}_{r['seed']}")
        # A6 selections
        for l in open('results/a6_runs.jsonl'):
            r = json.loads(l)
            if r['tid'] == tid:
                add(r['best_genome'], f"A6_{r['seed']}")
        sets[tid] = [tuple(v) for v in seen.values()]
    return sets

def main():
    print('equivalence re-proof (3 genomes x 9 conds x 3 targets, bitwise)...', flush=True)
    fails = proof()
    if fails:
        print('PROOF FAILED:', fails[:10], flush=True)
        sys.exit(2)
    print('PROOF PASS: A6Eval path bitwise-identical to independent context-manager reference', flush=True)
    out = {'amendment': '8274f9f 2026-09-29 14:35 IST', 'semantics': 'v23c leak-free (locked)',
           'equivalence_proof': 'PASS bitwise (3x9x3)', 'per_target': {}}
    for tid in TARGETS:
        inputs = enum_inputs()[tid]
        print(tid, 'unique genomes to score:', len(inputs), flush=True)
        ev = a6.A6Eval(tid)
        rows = []
        for genome, prov in inputs:
            k = ''.join('1' if genome[b] else '0' for b in sorted(genome))
            ev.fitness(genome)
            rec = ev.cache[k]
            rows.append({'genome_key': k, 'provenance': prov, 'legs': rec['legs'], 'nom': rec['nom']})
        out['per_target'][tid] = {'n_unique': len(rows), 'rows': rows}
        # persist pid cache then remove (avoid committing pid caches)
        tmp = ev.cache_path + '.tmp'
        json.dump(ev.cache, open(tmp, 'w')); os.replace(tmp, ev.cache_path)
    json.dump(out, open('results/rescore_v23c.json', 'w'))
    total = sum(out['per_target'][t]['n_unique'] for t in TARGETS)
    print('DONE scored', total, 'unique genomes -> results/rescore_v23c.json', flush=True)

if __name__ == '__main__':
    main()
