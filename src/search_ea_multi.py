#!/usr/bin/env python3
"""W11 H3 multi-condition EA arm (search_design.md locked 21:27 + amendment 22:13).
Fitness = nominal flux x min battery retention (growth per-condition 50% max).
Resumable: appends to results/ea_runs.jsonl, skips completed (target,seed,mode)."""
import cobra, json, random, os, sys
sys.path.insert(0, 'src')
from search_ea_fast import get_model, POOL, SEEDS, MU, LAM, GENS, RESULTS

BATT = json.load(open('data/condition_battery.json'))
BIOMASS = 'BIOMASS_Ec_iML1515_core_75p37M'
CONDS = [('GLC_AEROBIC', BATT['base_condition']['bounds'])] + [(c['id'], c['bounds']) for c in BATT['battery']]

def apply_genome(m, tid, genome):
    if tid == '14BDO':
        m.reactions.get_by_id('BDO1').bounds = (0,1000) if genome.get('routeA_kgd') else (0,0)
        m.reactions.get_by_id('BDO1B').bounds = (0,1000) if genome.get('routeB_sucd') else (0,0)
    elif tid == 'ISOBUTANOL':
        m.reactions.get_by_id('IBUTDH').bounds = (0,1000) if genome.get('adh_nadh') else (0,0)
        m.reactions.get_by_id('IBUTDHP').bounds = (0,1000) if genome.get('adh_nadph') else (0,0)
    elif tid == 'LYCOPENE':
        m.reactions.get_by_id('DXPS').lower_bound = 1.0 if genome.get('dxs_push') else 0.0
        m.reactions.get_by_id('IPDDI').lower_bound = 0.5 if genome.get('idi_push') else 0.0

def prod_flux(m, prod):
    bio = m.reactions.get_by_id(BIOMASS)
    bio.lower_bound, bio.upper_bound = 0.0, 1000.0
    m.objective = bio
    g = m.slim_optimize()
    if g != g or g <= 0: return 0.0
    bio.lower_bound = bio.upper_bound = 0.5 * g
    m.objective = m.reactions.get_by_id(prod)
    p = m.slim_optimize()
    return float(p) if (p == p and p and p > 0) else 0.0

def fitness_multi(tid, genome):
    m, prod = get_model(tid)
    with m:
        apply_genome(m, tid, genome)
        fluxes = {}
        for cid, bounds in CONDS:
            with m:
                for ex, b in bounds.items():
                    m.reactions.get_by_id(ex).lower_bound = b
                fluxes[cid] = prod_flux(m, prod)
    nom = fluxes['GLC_AEROBIC']
    if nom <= 0: return 0.0, 0.0
    minret = min(fluxes[c] / nom for c, _ in CONDS[1:])
    return nom * minret, minret

def run_ea_multi(tid, seed):
    rng = random.Random(seed)
    blocks = list(POOL[tid]['blocks'])
    rand_g = lambda: {b: rng.random() < 0.5 for b in blocks}
    pop = [rand_g() for _ in range(MU)]
    fit = [fitness_multi(tid, g)[0] for g in pop]
    for gen in range(GENS):
        kids = []
        while len(kids) < LAM:
            p1 = max(rng.sample(list(zip(fit, pop)), 3), key=lambda x: x[0])[1]
            kids.append({b: (not v if rng.random() < 1/len(blocks) else v) for b, v in p1.items()})
        kfit = [fitness_multi(tid, g)[0] for g in kids]
        both = sorted(zip(fit + kfit, pop + kids), key=lambda x: -x[0])
        pop = [g for _, g in both[:MU]]; fit = [f for f, _ in both[:MU]]
    f, mr = fitness_multi(tid, pop[0])
    return {'target': tid, 'seed': seed, 'mode': 'multi_condition',
            'best_flux': f, 'min_retention': mr, 'best_genome': pop[0]}

if __name__ == '__main__':
    done = set()
    if os.path.exists(RESULTS):
        for line in open(RESULTS):
            try:
                r = json.loads(line); done.add((r['target'], r['seed'], r['mode']))
            except Exception: pass
    targets = sys.argv[1].split(',') if len(sys.argv) > 1 else ['14BDO','ISOBUTANOL','LYCOPENE']
    seeds = [int(s) for s in sys.argv[2].split(',')] if len(sys.argv) > 2 else SEEDS
    for tid in targets:
        get_model(tid)
        for seed in seeds:
            if (tid, seed, 'multi_condition') in done: continue
            r = run_ea_multi(tid, seed)
            with open(RESULTS, 'a') as f: f.write(json.dumps(r) + '\n')
            print('EA-M', tid, seed, 'fit', round(r['best_flux'],4), 'minret', round(r['min_retention'],3), r['best_genome'], flush=True)
    print('chunk done')
