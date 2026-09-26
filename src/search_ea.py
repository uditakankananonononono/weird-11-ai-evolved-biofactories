#!/usr/bin/env python3
"""W11 EA scaffold (search_design.md locked 21:27 IST). Genome = on/off per pool
block + core always-on. Fitness = product flux at pFBA, growth fixed at 50% max,
GLC_AEROBIC. Smoke-test mode: 2 generations, small mu/lambda, proves the loop."""
import cobra, json, random, sys
sys.path.insert(0, 'src')
from benchmark_flux import BUILDERS, BASE, met, rxn

POOL = json.load(open('data/reaction_pool.json'))['pools']
BIOMASS = 'BIOMASS_Ec_iML1515_core_75p37M'

def build_model(tid, genome):
    m = cobra.io.read_sbml_model('data/models/iML1515.xml.gz')
    for ex, b in BASE.items(): m.reactions.get_by_id(ex).lower_bound = b
    prod = BUILDERS[tid](m)  # adds ALL benchmark reactions incl. block members
    pool = POOL[tid]
    # alternative/extra reactions from block definitions
    g = lambda i: m.metabolites.get_by_id(i)
    if tid == '14BDO' and genome.get('routeB_sucd'):
        rxn(m,'BDO1B','succinyl-CoA reductase (sucD)',{g('succoa_c'):-1,g('nadh_c'):-1,g('h_c'):-1,g('sucsal_c'):1,g('coa_c'):1,g('nad_c'):1})
    if tid == 'ISOBUTANOL' and genome.get('adh_nadph'):
        rxn(m,'IBUTDHP','isobutanol dehydrogenase (NADPH)',{g('ibutyr_c'):-1,g('nadph_c'):-1,g('h_c'):-1,g('ibut_c'):1,g('nadp_c'):1})
    # turn OFF benchmark reactions not selected
    for bname, blk in pool['blocks'].items():
        if not genome.get(bname):
            for rid in blk['reactions']:
                if rid in m.reactions: m.reactions.get_by_id(rid).bounds = (0,0)
    if tid == '14BDO' and not genome.get('routeA_kgd'): m.reactions.get_by_id('BDO1').bounds=(0,0)
    if tid == 'ISOBUTANOL' and not genome.get('adh_nadh'): m.reactions.get_by_id('IBUTDH').bounds=(0,0)
    # pushes
    if tid == 'LYCOPENE':
        if genome.get('dxs_push'): m.reactions.get_by_id('DXPS').lower_bound = 1.0
        if genome.get('idi_push'): m.reactions.get_by_id('IPDDI').lower_bound = 0.5
    return m, prod

def fitness(tid, genome, gmax_cache={}):
    try:
        m, prod = build_model(tid, genome)
        if tid not in gmax_cache:
            gmax_cache[tid] = m.slim_optimize()
        bio = m.reactions.get_by_id(BIOMASS)
        bio.lower_bound = bio.upper_bound = 0.5 * gmax_cache[tid]
        m.objective = m.reactions.get_by_id(prod)
        p = m.slim_optimize()
        m.reactions.get_by_id(prod).lower_bound = 0.999 * p
        sol = cobra.flux_analysis.pfba(m)
        return float(sol.fluxes[prod])
    except Exception:
        return 0.0

def random_genome(tid, rng):
    return {b: rng.random() < 0.5 for b in POOL[tid]['blocks']}

def run(tid, seed, gens=2, mu=6, lam=12):
    rng = random.Random(seed)
    pop = [random_genome(tid, rng) for _ in range(mu)]
    fit = [fitness(tid, g) for g in pop]
    for gen in range(gens):
        kids = []
        while len(kids) < lam:
            p1 = max(rng.sample(list(zip(fit, pop)), 3), key=lambda x: x[0])[1]
            kid = {b: (not v if rng.random() < 1/len(pop[0]) else v) for b, v in p1.items()}
            kids.append(kid)
        kfit = [fitness(tid, g) for g in kids]
        both = sorted(zip(fit + kfit, pop + kids), key=lambda x: -x[0])
        pop = [g for _, g in both[:mu]]; fit = [f for f, _ in both[:mu]]
        print(tid, 'gen', gen, 'best', round(fit[0], 4), pop[0], flush=True)
    return {'target': tid, 'seed': seed, 'best_flux': fit[0], 'best_genome': pop[0]}

if __name__ == '__main__':
    out = [run(t, 260926) for t in ['14BDO','ISOBUTANOL','LYCOPENE']]
    json.dump({'mode':'SMOKE TEST (2 gen, mu=6) - not a search result', 'runs': out},
              open('results/search_smoke.json','w'), indent=1)
    print('smoke ok')
