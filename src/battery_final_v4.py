#!/usr/bin/env python3
"""W11 pool-v4 FINAL battery + gate (amendments 4a71551, eede3fd, 2026-09-28 15:52 IST - locked pre-evaluation).
Per primary run's best_genome: full tiered battery. Severe frontier = EVALUATED SET (25 primary
best-genomes per target), disclosed. Gate: M-W U arm vs A0 on best_flux (5v5, two-sided exact).
Sensitivity: 10,000-label permutation pooling primary+extension. Dedup: keep-first (target,arm,seed)."""
import cobra, json, os, sys, itertools, random
sys.path.insert(0, 'src')
import importlib.util
spec = importlib.util.spec_from_file_location('ea', 'src/search_ea_v4.py')
ea = importlib.util.module_from_spec(spec); sys.argv=['x']
spec.loader.exec_module(ea)
from scipy.stats import mannwhitneyu

BATT = json.load(open('data/condition_battery.json'))
BIOMASS = 'BIOMASS_Ec_iML1515_core_75p37M'
MILD = ['GLC_PERT_MINUS20','GLC_PERT_PLUS20','O2_PERT_MINUS50']
SEVERE = ['GLC_LOW','GLC_MID','ANAEROBIC','GLYCEROL','ACETATE']
CONDS = [dict(id='GLC_AEROBIC', bounds=BATT['base_condition']['bounds'])] + BATT['battery']
SEEDS = [260927,261927,262927,263927,264927]

# dedup keep-first
rows = {}
for line in open('results/ea_v4_runs.jsonl'):
    r = json.loads(line)
    rows.setdefault((r['target'], r['arm'], r['seed']), r)
primary = {k: v for k, v in rows.items() if k[2] in SEEDS}
extension = {k: v for k, v in rows.items() if k[2] not in SEEDS}
assert len(primary) == 75, f"primary {len(primary)} != 75"

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
    cache = f'results/battery_v4_{tid}.json'
    if os.path.exists(cache):
        out[tid] = json.load(open(cache)); print(tid, 'cached', flush=True); continue
    m, prod = ea.get_model(tid)
    runs = [primary[(tid, a, s)] for a in ['A0','A1','A2','A3','A4'] for s in SEEDS]
    F = []
    for i, r in enumerate(runs):
        g = r['best_genome']
        with m:
            ea.apply_genome(m, tid, g)
            row = {}
            for cond in CONDS:
                row[cond['id']] = flux_cond(m, prod, cond)
        F.append(row)
        print(tid, i+1, '/25 battery genomes done', flush=True)
    frontier = {c: max(F[i][c] for i in range(25)) for c in SEVERE}
    scored = []
    for i, r in enumerate(runs):
        nom = F[i]['GLC_AEROBIC']
        mild_ret = {k: (F[i][k]/nom if nom > 0 else 0.0) for k in MILD}
        sev_r = {k: (F[i][k]/frontier[k] if frontier[k] > 0 else 0.0) for k in SEVERE}
        R_pert = sum(mild_ret.values())/3; R_shift = sum(sev_r.values())/5
        mild_pass = all(v >= 0.8 for v in mild_ret.values())
        sev_pass = all(v >= 0.8 for v in sev_r.values())
        scored.append({'target': tid, 'arm': r['arm'], 'seed': r['seed'],
                       'best_flux_search': r['best_flux'], 'nominal_battery': round(nom,4),
                       'mild_retention': {k: round(v,4) for k,v in mild_ret.items()},
                       'severe_relative': {k: round(v,4) for k,v in sev_r.items()},
                       'R_pert': round(R_pert,4), 'R_shift': round(R_shift,4),
                       'R_tiered': round(0.5*R_pert + 0.5*R_shift,4),
                       'mild_leg_pass': mild_pass, 'severe_leg_pass': sev_pass,
                       'battery_pass': mild_pass and sev_pass})
    out[tid] = {'frontier_severe_evaluated_set': {k: round(v,4) for k,v in frontier.items()},
                'n_pass': sum(1 for s in scored if s['battery_pass']), 'scored': scored}
    json.dump(out[tid], open(cache,'w'), indent=1)
    print(tid, 'pass:', out[tid]['n_pass'], flush=True)

# GATE: M-W arm vs A0 on best_flux across 5 primary seeds, per target (exact two-sided)
gate = {}
for tid in ['14BDO','ISOBUTANOL','LYCOPENE']:
    gate[tid] = {}
    a0 = [primary[(tid,'A0',s)]['best_flux'] for s in SEEDS]
    for a in ['A1','A2','A3','A4']:
        x = [primary[(tid,a,s)]['best_flux'] for s in SEEDS]
        U, p = mannwhitneyu(x, a0, alternative='two-sided', method='exact')
        gate[tid][a] = {'A0': a0, 'arm': x, 'U': float(U), 'p_exact': float(p), 'pass': bool(p < 0.05)}

# SENSITIVITY: 10,000-label permutation pooling primary+extension, diff-of-means arm vs A0
rng = random.Random(260927)
sens = {}
for tid in ['14BDO','ISOBUTANOL','LYCOPENE']:
    sens[tid] = {}
    a0p = [rows[(tid,'A0',s)]['best_flux'] for s in sorted(set(k[2] for k in rows if k[0]==tid and k[1]=='A0'))]
    for a in ['A1','A2','A3','A4']:
        seeds_a = sorted(set(k[2] for k in rows if k[0]==tid and k[1]==a))
        xp = [rows[(tid,a,s)]['best_flux'] for s in seeds_a]
        obs = abs(sum(xp)/len(xp) - sum(a0p)/len(a0p))
        pool = xp + a0p; n = len(xp); ge = 0
        for _ in range(10000):
            rng.shuffle(pool)
            d = abs(sum(pool[:n])/n - sum(pool[n:])/(len(pool)-n))
            if d >= obs - 1e-15: ge += 1
        sens[tid][a] = {'obs_absdiff': obs, 'p_perm': (ge+1)/10001, 'n_arm': n, 'n_A0': len(a0p)}
    print(tid, 'gate+sens done', flush=True)

json.dump({'amendments': ['4a71551','eede3fd','2026-09-28 15:52 IST'],
           'frontier': 'evaluated-set (25 primary best-genomes per target) - disclosed',
           'battery': out, 'gate_MW_exact': gate, 'sensitivity_perm10k': sens},
          open('results/battery_final_v4.json','w'), indent=1)
print('written results/battery_final_v4.json', flush=True)
