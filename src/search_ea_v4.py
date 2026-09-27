#!/usr/bin/env python3
"""W11 pool-v4 SEARCH arms (amendment commit 4a71551, locked pre-computation).
Pool v4 = 14 host + 2 target levers (65,536 genomes/target). EA config identical to
pool-v3 (MU=24, LAM=48, GENS=60, tournament k=3, bitflip 1/n, (mu+lambda) truncation).
Arms A0 baseline / A1 constraint-aware mutation / A2 diversity tie-break /
A3 adaptive mutation rate / A4 surrogate-assisted (RF 50 trees, sklearn defaults).
Search fitness = nominal GLC_AEROBIC product-max FBA (locked precedent).
Final eval of each run's best = full tiered battery; severe frontier = evaluated-set
(disclosed per amendment). Resumable: appends to results/ea_v4_runs.jsonl."""
import cobra, json, random, os, sys, time
sys.path.insert(0, 'src')
from benchmark_flux import BUILDERS, BASE, rxn

POOL = json.load(open('data/reaction_pool.json'))['pools']
BATT = json.load(open('data/condition_battery.json'))
BIOMASS = 'BIOMASS_Ec_iML1515_core_75p37M'
HOST14 = ['ko_ackApta','ko_pflB','ko_ldhA','cofeed_glycerol','ko_adhE','ko_tpiA',
          'ko_ppc','ko_gnd','ko_pgi','ko_me1','ko_acs','ko_icdhyr']
MU, LAM, GENS = 24, 48, 60
MILD = ['GLC_PERT_MINUS20','GLC_PERT_PLUS20','O2_PERT_MINUS50']
SEVERE = ['GLC_LOW','GLC_MID','ANAEROBIC','GLYCEROL','ACETATE']
RESULTS = 'results/ea_v4_runs.jsonl'

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
    _models[tid] = (m, prod)
    return m, prod

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
    m.reactions.get_by_id('ACKr').bounds = (0,0) if genome.get('ko_ackApta') else (-1000,1000)
    m.reactions.get_by_id('PTAr').bounds = (0,0) if genome.get('ko_ackApta') else (-1000,1000)
    m.reactions.get_by_id('PFL').bounds = (0,0) if genome.get('ko_pflB') else (0,1000)
    m.reactions.get_by_id('LDH_D').bounds = (0,0) if genome.get('ko_ldhA') else (0,1000)
    m.reactions.get_by_id('EX_glyc_e').lower_bound = -4.0 if genome.get('cofeed_glycerol') else 0.0
    m.reactions.get_by_id('ALCD2x').bounds = (0,0) if genome.get('ko_adhE') else (-1000,1000)
    m.reactions.get_by_id('TPI').bounds = (0,0) if genome.get('ko_tpiA') else (-1000,1000)
    m.reactions.get_by_id('PPC').bounds = (0,0) if genome.get('ko_ppc') else (-1000,1000)
    m.reactions.get_by_id('GND').bounds = (0,0) if genome.get('ko_gnd') else (-1000,1000)
    m.reactions.get_by_id('PGI').bounds = (0,0) if genome.get('ko_pgi') else (-1000,1000)
    m.reactions.get_by_id('ME1').bounds = (0,0) if genome.get('ko_me1') else (-1000,1000)
    m.reactions.get_by_id('ACS').bounds = (0,0) if genome.get('ko_acs') else (-1000,1000)
    m.reactions.get_by_id('ICDHyr').bounds = (0,0) if genome.get('ko_icdhyr') else (-1000,1000)

def fitness(tid, genome):
    m, prod = get_model(tid)
    with m:
        apply_genome(m, tid, genome)
        gmax_bio = m.reactions.get_by_id(BIOMASS)
        # nominal: growth-coupled product max (locked: 0.5*gmax floor, same as pool v3 get_model)
        m.objective = gmax_bio
        gmax = m.slim_optimize()
        if gmax != gmax or gmax <= 0: return 0.0
        gmax_bio.lower_bound = gmax_bio.upper_bound = 0.5 * gmax
        m.objective = m.reactions.get_by_id(prod)
        p = m.slim_optimize()
        return float(p) if (p == p and p and p > 0) else 0.0

def key(g, bits): return tuple(1 if g[b] else 0 for b in bits)

def run_ea(tid, seed, arm):
    rng = random.Random(seed)
    bits = HOST14 + list(POOL[tid]['blocks'])
    nb = len(bits)
    rand_g = lambda: {b: rng.random() < 0.5 for b in bits}
    seen = set()
    eval_hist = []  # (bit list, fitness) for surrogate training
    def evalg(g):
        k = key(g, bits)
        seen.add(k)
        f = fitness(tid, g)
        eval_hist.append((list(k), f))
        return f
    pop = [rand_g() for _ in range(MU)]
    fit = [evalg(g) for g in pop]
    hist = [max(fit)]
    mut = 1/nb
    stall = 0
    best = fit[0]
    for gen in range(GENS):
        kids = []
        while len(kids) < LAM:
            cand = rng.sample(list(zip(fit, pop)), 3)
            topf = max(x[0] for x in cand)
            tied = [x for x in cand if x[0] == topf]
            if arm == 'A2' and len(tied) > 1:
                p1 = max(tied, key=lambda x: max(sum(1 for b in bits if x[1][b] != q[b]) for q in pop))[1]
            else:
                p1 = tied[0][1]
            for _ in range(10 if arm == 'A1' else 1):
                kid = {b: (not v if rng.random() < mut else v) for b, v in p1.items()}
                if arm != 'A1' or key(kid, bits) not in seen: break
            else:
                kid = rand_g()
            kids.append(kid)
        if arm == 'A4':
            from sklearn.ensemble import RandomForestRegressor
            rf = RandomForestRegressor(n_estimators=50, random_state=seed)
            rf.fit([x[0] for x in eval_hist], [x[1] for x in eval_hist])
            cands = [c for c in (rand_g() for _ in range(512)) if key(c, bits) not in seen]
            if len(cands) >= 2:
                preds = rf.predict([[1 if c[b] else 0 for b in bits] for c in cands])
                order = sorted(range(len(cands)), key=lambda i: -preds[i])
                kids[-2:] = [cands[order[0]], cands[order[1]]]
        kfit = [evalg(k) for k in kids]
        both = sorted(zip(fit + kfit, pop + kids), key=lambda x: -x[0])
        pop = [g for _, g in both[:MU]]; fit = [f for f, _ in both[:MU]]
        hist.append(fit[0])
        if arm == 'A3':
            if fit[0] > best: best = fit[0]; stall = 0; mut = 1/nb
            else:
                stall += 1
                if stall >= 10: mut = min(mut*2, 8/nb); stall = 0
    return {'target': tid, 'seed': seed, 'arm': arm, 'mode': 'pool_v4_nominal',
            'amendment_commit': '4a71551', 'n_evals': len(seen),
            'best_flux': fit[0], 'best_genome': pop[0], 'hist_last10': hist[-10:]}

if __name__ == '__main__':
    done = set()
    if os.path.exists(RESULTS):
        for line in open(RESULTS):
            try:
                r = json.loads(line); done.add((r['target'], r['seed'], r['arm']))
            except Exception: pass
    targets = sys.argv[1].split(',')
    arms = sys.argv[2].split(',')
    seeds = [int(s) for s in sys.argv[3].split(',')]
    for tid in targets:
        get_model(tid)
        for arm in arms:
            for seed in seeds:
                if (tid, seed, arm) in done: continue
                t0 = time.time()
                r = run_ea(tid, seed, arm)
                r['wall_s'] = round(time.time()-t0, 2)
                with open(RESULTS, 'a') as f: f.write(json.dumps(r) + '\n')
                print('V4', tid, arm, seed, 'best', round(r['best_flux'],4), f"{r['wall_s']}s", flush=True)
    print('chunk done')
