#!/usr/bin/env python3
"""W11 EA with cached models (search_design.md locked 21:27 IST).
One all-blocks model per target; per-genome evaluation = context-block bound toggles.
Resumable: appends per-(target,seed) results to results/ea_runs.jsonl; skips completed."""
import cobra, json, random, os, sys
sys.path.insert(0, 'src')
from benchmark_flux import BUILDERS, BASE, rxn

POOL = json.load(open('data/reaction_pool.json'))['pools']
BIOMASS = 'BIOMASS_Ec_iML1515_core_75p37M'
SEEDS = [260926, 260927, 260928, 260929, 260930]
MU, LAM, GENS = 24, 48, 60
RESULTS = 'results/ea_runs.jsonl'

_models = {}
def get_model(tid):
    if tid in _models: return _models[tid]
    m = cobra.io.read_sbml_model('data/models/iML1515.xml.gz')
    for ex, b in BASE.items(): m.reactions.get_by_id(ex).lower_bound = b
    prod = BUILDERS[tid](m)
    g = lambda i: m.metabolites.get_by_id(i)
    if tid == '14BDO':
        r = rxn(m,'BDO1B','succinyl-CoA reductase (sucD)',{g('succoa_c'):-1,g('nadh_c'):-1,g('h_c'):-1,g('sucsal_c'):1,g('coa_c'):1,g('nad_c'):1}); r.bounds=(0,0)
    if tid == 'ISOBUTANOL':
        r = rxn(m,'IBUTDHP','isobutanol dehydrogenase (NADPH)',{g('ibutyr_c'):-1,g('nadph_c'):-1,g('h_c'):-1,g('ibut_c'):1,g('nadp_c'):1}); r.bounds=(0,0)
    gmax = m.slim_optimize()
    bio = m.reactions.get_by_id(BIOMASS)
    bio.lower_bound = bio.upper_bound = 0.5 * gmax
    m.objective = m.reactions.get_by_id(prod)
    _models[tid] = (m, prod)
    return m, prod

def fitness(tid, genome):
    m, prod = get_model(tid)
    with m:
        if tid == '14BDO':
            m.reactions.get_by_id('BDO1').bounds = (0,1000) if genome.get('routeA_kgd') else (0,0)
            m.reactions.get_by_id('BDO1B').bounds = (0,1000) if genome.get('routeB_sucd') else (0,0)
        elif tid == 'ISOBUTANOL':
            m.reactions.get_by_id('IBUTDH').bounds = (0,1000) if genome.get('adh_nadh') else (0,0)
            m.reactions.get_by_id('IBUTDHP').bounds = (0,1000) if genome.get('adh_nadph') else (0,0)
        elif tid == 'LYCOPENE':
            m.reactions.get_by_id('DXPS').lower_bound = 1.0 if genome.get('dxs_push') else 0.0
            m.reactions.get_by_id('IPDDI').lower_bound = 0.5 if genome.get('idi_push') else 0.0
        # FBA product max used for SEARCH fitness (envelope verified pfba==fba, unique
        # optima, 2026-09-26); final evaluation of evolved architectures uses full pFBA
        # per the locked metric. pFBA per fitness call costs ~8s - infeasible at EA scale.
        p = m.slim_optimize()
        return float(p) if p and p > 0 else 0.0

def run_ea(tid, seed):
    rng = random.Random(seed)
    blocks = list(POOL[tid]['blocks'])
    rand_g = lambda: {b: rng.random() < 0.5 for b in blocks}
    pop = [rand_g() for _ in range(MU)]
    fit = [fitness(tid, g) for g in pop]
    hist = [max(fit)]
    for gen in range(GENS):
        kids = []
        while len(kids) < LAM:
            p1 = max(rng.sample(list(zip(fit, pop)), 3), key=lambda x: x[0])[1]
            kids.append({b: (not v if rng.random() < 1/len(blocks) else v) for b, v in p1.items()})
        kfit = [fitness(tid, g) for g in kids]
        both = sorted(zip(fit + kfit, pop + kids), key=lambda x: -x[0])
        pop = [g for _, g in both[:MU]]; fit = [f for f, _ in both[:MU]]
        hist.append(fit[0])
    return {'target': tid, 'seed': seed, 'mode': 'single_condition',
            'best_flux': fit[0], 'best_genome': pop[0], 'hist_last10': hist[-10:]}

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
            if (tid, seed, 'single_condition') in done: continue
            r = run_ea(tid, seed)
            with open(RESULTS, 'a') as f: f.write(json.dumps(r) + '\n')
            print('EA', tid, seed, 'best', round(r['best_flux'], 4), r['best_genome'], flush=True)
    print('chunk done')

