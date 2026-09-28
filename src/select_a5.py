#!/usr/bin/env python3
"""W11 pool-v4 A5 STAGE 2 (amendments 16:02/16:08/16:10 IST 2026-09-28 - locked pre-computation).
Per (target, seed): plateau = explored genomes with fitness >= best*(1-1e-6); dedup keep-first-explored;
full tiered battery on each plateau genome vs COMMITTED severe frontier (battery_v4_<target>.json);
selection = argmax R_tiered (ties -> first-explored). Gate: M-W exact two-sided, A5-selected R_tiered vs
committed A0 R_tiered (5v5 per target); sensitivity: 10,000-label permutation. All values verbatim."""
import json, os, sys, random
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

def flux_cond(m, prod, cond):  # identical to battery_final_v4.py
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

selections = []
gate = {}
for tid in ['14BDO','ISOBUTANOL','LYCOPENE']:
    m, prod = ea.get_model(tid)
    committed = json.load(open(f'results/battery_v4_{tid}.json'))
    frontier = {k: committed['frontier_severe_evaluated_set'][k] for k in SEVERE}
    a0_r = [s['R_tiered'] for s in committed['scored'] if s['arm'] == 'A0']
    assert len(a0_r) == 5
    a5_r = []
    for seed in SEEDS:
        traj = json.load(open(f'results/a5_traj/{tid}_{seed}.json'))
        hist = traj['eval_hist']
        best = max(f for _, f in hist)
        thr = best * (1 - 1e-6)
        plateau, seenk = [], set()
        for klist, f in hist:
            if f >= thr:
                kt = tuple(klist)
                if kt not in seenk:
                    seenk.add(kt)
                    plateau.append((klist, f))
        scored = []
        for klist, f in plateau:
            g = dict(zip(ea.HOST14 + list(ea.POOL[tid]['blocks']), klist))
            with m:
                ea.apply_genome(m, tid, g)
                row = {}
                for cond in CONDS:
                    row[cond['id']] = flux_cond(m, prod, cond)
            nom = row['GLC_AEROBIC']
            mild_ret = {k: (row[k]/nom if nom > 0 else 0.0) for k in MILD}
            sev_r = {k: (row[k]/frontier[k] if frontier[k] > 0 else 0.0) for k in SEVERE}
            R_pert = sum(mild_ret.values())/3; R_shift = sum(sev_r.values())/5
            scored.append({'key': klist, 'search_fitness': f,
                           'R_pert': round(R_pert,4), 'R_shift': round(R_shift,4),
                           'R_tiered': 0.5*R_pert + 0.5*R_shift,
                           'mild_leg_pass': all(v >= 0.8 for v in mild_ret.values()),
                           'severe_leg_pass': all(v >= 0.8 for v in sev_r.values())})
        top = max(s['R_tiered'] for s in scored)
        sel = next(s for s in scored if s['R_tiered'] == top)  # first-explored on ties
        sel.update({'target': tid, 'seed': seed, 'best_nominal': best,
                    'plateau_size': len(plateau), 'battery_pass': sel['mild_leg_pass'] and sel['severe_leg_pass']})
        a5_r.append(sel['R_tiered'])
        selections.append(sel)
        print(tid, seed, 'plateau', len(plateau), 'selected R_tiered', round(top,4), flush=True)
    u = mannwhitneyu(a5_r, a0_r, alternative='two-sided', method='exact')
    # 10,000-label permutation sensitivity
    rng = random.Random(20260928)
    pooled = a5_r + a0_r
    obs = abs(sum(a5_r)/5 - sum(a0_r)/5)
    cnt = 0
    for _ in range(10000):
        rng.shuffle(pooled)
        if abs(sum(pooled[:5])/5 - sum(pooled[5:])/5) >= obs: cnt += 1
    gate[tid] = {'a5_R_tiered': a5_r, 'a0_committed_R_tiered': a0_r,
                 'mw_exact_p_two_sided': u.pvalue, 'perm10k_p': (cnt+1)/10001}
    print(tid, 'M-W exact p', u.pvalue, 'perm p', (cnt+1)/10001, flush=True)

json.dump({'selections': selections, 'gate': gate}, open('results/a5_selection.json','w'), indent=1)
print('a5 stage2 done')
