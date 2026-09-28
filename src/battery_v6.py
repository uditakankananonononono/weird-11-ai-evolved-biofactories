#!/usr/bin/env python3
"""W11 pool-v4 DETERMINISTIC HiGHS battery (amendment f4738d6, 2026-09-28 16:46 IST - locked pre-computation).
LPs solved via scipy.optimize.linprog method='highs' on the exported stoichiometric matrix - no carried
solver state. Battery metric only; search fitness stays locked GLPK. Validation (locked): for every genome,
battery GLC_AEROBIC nominal must match recorded search fitness within 1e-9 relative; mismatches disclosed.
Recomputes: 83 best genomes, frontier (25-primary evaluated set), R_tiered, A0-A4 arm gate, A5 plateau
selections + A5 gate (M-W exact + 10k perm). Incremental cache; resume-safe."""
import json, os, sys, random
import numpy as np
from scipy.optimize import linprog
import cobra.util.array as cua
sys.path.insert(0, 'src')
import importlib.util
_argv = sys.argv
spec = importlib.util.spec_from_file_location('ea', 'src/search_ea_v4.py')
ea = importlib.util.module_from_spec(spec); sys.argv = ['x']
spec.loader.exec_module(ea)
sys.argv = _argv
from scipy.stats import mannwhitneyu

BATT = json.load(open('data/condition_battery.json'))
BIOMASS = 'BIOMASS_Ec_iML1515_core_75p37M'
MILD = ['GLC_PERT_MINUS20','GLC_PERT_PLUS20','O2_PERT_MINUS50']
SEVERE = ['GLC_LOW','GLC_MID','ANAEROBIC','GLYCEROL','ACETATE']
CONDS = [dict(id='GLC_AEROBIC', bounds=BATT['base_condition']['bounds'])] + BATT['battery']
SEEDS = [260927,261927,262927,263927,264927]

def lp(S, b_eq, bounds, rxns, obj_id):
    c = np.zeros(len(rxns)); c[rxns.index(obj_id)] = -1.0
    r = linprog(c, A_eq=S, b_eq=b_eq, bounds=bounds, method='highs')
    if r.status != 0: return None
    v = -r.fun
    return float(v) if v > 0 else 0.0

def battery_row(m, S, b_eq, rxns, prod, tid, g):
    row = {}
    with m:
        ea.apply_genome(m, tid, g)
        for cond in CONDS:
            for ex, b in BATT['base_condition']['bounds'].items():
                m.reactions.get_by_id(ex).lower_bound = b
            for ex, b in cond['bounds'].items():
                m.reactions.get_by_id(ex).lower_bound = b
            bounds = [(r.lower_bound, r.upper_bound) for r in m.reactions]
            gmax = lp(S, b_eq, bounds, rxns, BIOMASS)
            if gmax is None or gmax <= 0:
                # growth zero/infeasible: same rule as flux_cond (floor non-binding at ~0)
                gmax = 0.0
            i = rxns.index(BIOMASS)
            bounds[i] = (0.5 * gmax, 0.5 * gmax)
            p = lp(S, b_eq, bounds, rxns, prod)
            row[cond['id']] = p if p else 0.0
    return row

def score(row, frontier, nom):
    mild_ret = {k: (row[k]/nom if nom > 0 else 0.0) for k in MILD}
    sev_r = {k: (row[k]/frontier[k] if frontier[k] > 0 else 0.0) for k in SEVERE}
    R_pert = sum(mild_ret.values())/3; R_shift = sum(sev_r.values())/5
    return {'mild_retention': {k: round(v,4) for k,v in mild_ret.items()},
            'severe_relative': {k: round(v,4) for k,v in sev_r.items()},
            'R_pert': round(R_pert,4), 'R_shift': round(R_shift,4),
            'R_tiered': 0.5*R_pert + 0.5*R_shift,
            'mild_leg_pass': all(v >= 0.8 for v in mild_ret.values()),
            'severe_leg_pass': all(v >= 0.8 for v in sev_r.values())}

def mw_and_perm(xa, x0, seed=20260928):
    u = mannwhitneyu(list(xa), list(x0), alternative='two-sided', method='exact')
    rng = random.Random(seed)
    pooled = list(xa) + list(x0)
    obs = abs(sum(xa)/len(xa) - sum(x0)/len(x0))
    n = len(xa); cnt = 0
    for _ in range(10000):
        rng.shuffle(pooled)
        if abs(sum(pooled[:n])/n - sum(pooled[n:])/n) >= obs: cnt += 1
    return u.pvalue, (cnt+1)/10001

rows = {}
for line in open('results/ea_v4_runs.jsonl'):
    r = json.loads(line)
    rows.setdefault((r['target'], r['arm'], r['seed']), r)
primary = {k: v for k, v in rows.items() if k[2] in SEEDS}
assert len(primary) == 75

out = {}
if os.path.exists('results/battery_v6.json'):
    out = json.load(open('results/battery_v6.json'))

for tid in ['14BDO','ISOBUTANOL','LYCOPENE']:
    t_out = out.setdefault(tid, {'genome_rows': {}, 'plateau_rows': {}, 'validation_failures': []})
    m, prod = ea.get_model(tid)
    rxns = [r.id for r in m.reactions]
    S = cua.create_stoichiometric_matrix(m, array_type='lil').tocsc()
    b_eq = np.zeros(S.shape[0])
    for (t, arm, seed), r in sorted(rows.items()):
        if t != tid: continue
        gk = f'{arm}_{seed}'
        if gk in t_out['genome_rows']: continue
        row = battery_row(m, S, b_eq, rxns, prod, tid, r['best_genome'])
        sf = r['best_flux']; nom = row['GLC_AEROBIC']
        ok = abs(nom - sf) <= 1e-9 * max(1.0, abs(sf))
        if not ok: t_out['validation_failures'].append({'target': t, 'arm': arm, 'seed': seed, 'nom': nom, 'search': sf})
        t_out['genome_rows'][gk] = {'row': row, 'nom_ok': ok}
        json.dump(out, open('results/battery_v6.json','w'))
        print(tid, gk, 'nom', round(nom,4), 'valid', ok, flush=True)
    frontier = {c: max(t_out['genome_rows'][f'{a}_{s}']['row'][c] for a in ['A0','A1','A2','A3','A4'] for s in SEEDS) for c in SEVERE}
    t_out['frontier_severe_evaluated_set'] = {k: round(v,4) for k,v in frontier.items()}
    scored = []
    for (t, arm, seed), r in sorted(rows.items()):
        if t != tid: continue
        gr = t_out['genome_rows'][f'{arm}_{seed}']
        nom = gr['row']['GLC_AEROBIC']
        s = score(gr['row'], frontier, nom)
        s.update({'target': t, 'arm': arm, 'seed': seed, 'best_flux_search': r['best_flux'],
                  'nominal_battery': round(nom,4), 'nom_valid': gr['nom_ok'],
                  'battery_pass': s['mild_leg_pass'] and s['severe_leg_pass']})
        scored.append(s)
    t_out['scored'] = scored
    gates = {}
    for arm in ['A1','A2','A3','A4']:
        xa = [r['best_flux'] for (t,a,s),r in primary.items() if t==tid and a==arm]
        x0 = [r['best_flux'] for (t,a,s),r in primary.items() if t==tid and a=='A0']
        gates[arm] = {'mw_exact_p_two_sided': mw_and_perm(xa, x0)[0]}
    t_out['arm_gate_best_flux'] = gates
    json.dump(out, open('results/battery_v6.json','w'))
    a5_sel = []
    for seed in SEEDS:
        traj = json.load(open(f'results/a5_traj/{tid}_{seed}.json'))
        hist = traj['eval_hist']
        bestf = max(f for _, f in hist)
        thr = bestf * (1 - 1e-6)
        plateau, seenk = [], set()
        for klist, f in hist:
            if f >= thr:
                kt = tuple(klist)
                if kt not in seenk:
                    seenk.add(kt); plateau.append((klist, f))
        scoredp = []
        bits = ea.HOST14 + list(ea.POOL[tid]['blocks'])
        for i, (klist, f) in enumerate(plateau):
            pk = f'{seed}_{i}'
            if pk in t_out['plateau_rows']:
                s = t_out['plateau_rows'][pk]
            else:
                g = dict(zip(bits, klist))
                row = battery_row(m, S, b_eq, rxns, prod, tid, g)
                nom = row['GLC_AEROBIC']
                ok = abs(nom - f) <= 1e-9 * max(1.0, abs(f))
                if not ok: t_out['validation_failures'].append({'target': tid, 'arm': 'A5plateau', 'seed': seed, 'idx': i, 'nom': nom, 'search': f})
                s = score(row, frontier, nom); s.update({'nom': nom, 'nom_ok': ok})
                t_out['plateau_rows'][pk] = s
                json.dump(out, open('results/battery_v6.json','w'))
            scoredp.append({'i': i, 'search_fitness': f, **s})
        top = max(s['R_tiered'] for s in scoredp)
        sel = next(s for s in scoredp if s['R_tiered'] == top)
        a5_sel.append({'target': tid, 'seed': seed, 'plateau_size': len(plateau),
                       'R_tiered': sel['R_tiered'], 'R_pert': sel['R_pert'], 'R_shift': sel['R_shift'],
                       'battery_pass': sel['mild_leg_pass'] and sel['severe_leg_pass'],
                       'nom': sel['nom'], 'nom_ok': sel['nom_ok'], 'plateau_index_first_explored': sel['i']})
        print(tid, 'A5', seed, 'plateau', len(plateau), 'R_tiered', round(top,4), flush=True)
        json.dump(out, open('results/battery_v6.json','w'))
    t_out['a5_selections'] = a5_sel
    a0r = [s['R_tiered'] for s in scored if s['arm']=='A0' and s['seed'] in SEEDS]
    a5r = [s['R_tiered'] for s in a5_sel]
    p_mw, p_perm = mw_and_perm(a5r, a0r)
    t_out['a5_gate'] = {'a5_R_tiered': a5r, 'a0_R_tiered': a0r,
                        'mw_exact_p_two_sided': p_mw, 'perm10k_p': p_perm}
    print(tid, 'A5 gate: mw', p_mw, 'perm', p_perm, flush=True)
    json.dump(out, open('results/battery_v6.json','w'))

json.dump(out, open('results/battery_v6.json','w'), indent=1)
total_fail = sum(len(out[t]['validation_failures']) for t in out)
print('battery_v6 done; validation failures:', total_fail)
