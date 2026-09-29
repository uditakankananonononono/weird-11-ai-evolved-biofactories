#!/usr/bin/env python3
"""W11 pool-v4 A6 robust-fitness arm (amendment 2026-09-29 07:31 IST, commit 5c397ca - locked pre-computation).
SOLE protocol change vs A0 baseline: fitness = 0.5*R_pert + 0.5*mean(v_p,k/F_k) under v23c corrected
HiGHS semantics (unpin biomass, max growth, 0.5x floor, max product; exported matrix, no carried state).
F_k = FROZEN committed pool-v4 primary evaluated-set severe frontier (battery_v6.json, arms A0-A4 x 5 seeds).
EA config identical: MU=24, LAM=48, GENS=60, tournament k=3, bitflip 1/n, (mu+lambda) truncation,
first-encounter tie-break (A0 baseline rule). Seeds 260927-264927. Per-generation checkpoint, bit-exact resume.
Per-genome fitness cache (engineering, not protocol); per-seed cache files merged at chunk boundary."""
import json, random, os, sys, time, pickle, fcntl
import numpy as np
from scipy.optimize import linprog
import cobra.util.array as cua
import importlib.util
_argv = sys.argv
spec = importlib.util.spec_from_file_location('ea', 'src/search_ea_v4.py')
ea = importlib.util.module_from_spec(spec); sys.argv = ['x']
spec.loader.exec_module(ea)
sys.argv = _argv

POOL, HOST14, MU, LAM, GENS = ea.POOL, ea.HOST14, ea.MU, ea.LAM, ea.GENS
BATT, BIOMASS = ea.BATT, ea.BIOMASS
MILD, SEVERE = ea.MILD, ea.SEVERE
CONDS = [dict(id='GLC_AEROBIC', bounds=BATT['base_condition']['bounds'])] + BATT['battery']
SEEDS = [260927, 261927, 262927, 263927, 264927]
CKPT_DIR = 'results/a6_ckpt'

V6 = json.load(open('results/battery_v6.json'))
def frozen_frontier(tid):
    rows = V6[tid]['genome_rows']
    return {c: max(rows[f'{a}_{s}']['row'][c] for a in ['A0','A1','A2','A3','A4'] for s in SEEDS) for c in SEVERE}

class A6Eval:
    def __init__(self, tid):
        self.tid = tid
        self.m, self.prod = ea.get_model(tid)
        self.F = frozen_frontier(tid)
        self.cache_path = f'results/a6_cache_{tid}_{os.getpid()}.json'
        self.cache = json.load(open(self.cache_path)) if os.path.exists(self.cache_path) else {}
        self._dirty = 0
        # preload any sibling caches from earlier/parallel workers of this target (engineering reuse)
        import glob
        for p in sorted(glob.glob(f'results/a6_cache_{tid}_merged.json') + glob.glob(f'results/a6_cache_{tid}_*.json')):
            if p == self.cache_path: continue
            try:
                for k, v in json.load(open(p)).items(): self.cache.setdefault(k, v)
            except Exception: pass
        self.S = None
    def _setup(self):
        m = self.m
        self.S = cua.create_stoichiometric_matrix(m)
        self.rxns = [r.id for r in m.reactions]
        self.b_eq = np.zeros(self.S.shape[0])
        self.i_bio = self.rxns.index(BIOMASS); self.i_prod = self.rxns.index(self.prod)
    def _lp(self, bounds, obj_i):
        c = np.zeros(len(self.rxns)); c[obj_i] = -1.0
        r = linprog(c, A_eq=self.S, b_eq=self.b_eq, bounds=bounds, method='highs')
        return None if r.status != 0 else max(float(-r.fun), 0.0)
    def fitness(self, genome):
        k = ''.join('1' if genome[b] else '0' for b in sorted(genome))
        if k in self.cache: return self.cache[k]['f']
        if self.S is None: self._setup()
        m = self.m
        ea.apply_genome(m, self.tid, genome)
        base = [(r.lower_bound, r.upper_bound) for r in m.reactions]
        ex_idx = {}
        for ex in set(BATT['base_condition']['bounds']) | {kk for c in CONDS for kk in c['bounds']}:
            ex_idx[ex] = self.rxns.index(ex)
        vals = {}
        for cond in CONDS:
            bounds = list(base)
            ov = dict(BATT['base_condition']['bounds']); ov.update(cond['bounds'])
            for ex, b in ov.items():
                lb, ub = bounds[ex_idx[ex]]; bounds[ex_idx[ex]] = (float(b), ub)
            bounds[self.i_bio] = (0.0, 1000.0)
            g = self._lp(bounds, self.i_bio)
            if g is None or g <= 0: vals[cond['id']] = 0.0; continue
            bounds[self.i_bio] = (0.5*g, 0.5*g)
            p = self._lp(bounds, self.i_prod)
            vals[cond['id']] = p if p else 0.0
        nom = vals['GLC_AEROBIC']
        r_pert = float(np.mean([vals[c]/nom if nom > 0 else 0.0 for c in MILD]))
        r_shift = float(np.mean([vals[c]/self.F[c] if self.F[c] > 0 else 0.0 for c in SEVERE]))
        f = 0.5*r_pert + 0.5*r_shift
        self.cache[k] = {'f': f, 'nom': nom, 'legs': {c: round(vals[c], 6) for c in vals}}
        self._dirty += 1
        if self._dirty >= 50:
            tmp = self.cache_path + '.tmp'
            json.dump(self.cache, open(tmp, 'w')); os.replace(tmp, self.cache_path)
            self._dirty = 0
        return f

def run(tid, seed):
    bits = HOST14 + list(POOL[tid]['blocks'])
    nb = len(bits)
    os.makedirs(CKPT_DIR, exist_ok=True)
    ckpt_path = os.path.join(CKPT_DIR, f'{tid}_A6_{seed}.pkl')
    ev = A6Eval(tid)
    rng = random.Random(seed)
    rand_g = lambda: {b: rng.random() < 0.5 for b in bits}
    if os.path.exists(ckpt_path):
        st = pickle.load(open(ckpt_path, 'rb'))
        rng.setstate(st['rng']); pop, fit, hist, gen0 = st['pop'], st['fit'], st['hist'], st['gen']
    else:
        pop = [rand_g() for _ in range(MU)]
        fit = [ev.fitness(g) for g in pop]
        hist = [max(fit)]; gen0 = 0
    for gen in range(gen0, GENS):
        kids = []
        while len(kids) < LAM:
            cand = rng.sample(list(zip(fit, pop)), 3)
            topf = max(x[0] for x in cand)
            tied = [x for x in cand if x[0] == topf]
            p1 = tied[0][1]  # A0 baseline: first-encounter tie-break
            kid = {b: (not v if rng.random() < (1/nb) else v) for b, v in p1.items()}
            kids.append(kid)
        kfit = [ev.fitness(k) for k in kids]
        both = sorted(zip(fit + kfit, pop + kids), key=lambda x: -x[0])
        pop = [g for _, g in both[:MU]]; fit = [f for f, _ in both[:MU]]
        hist.append(max(fit))
        pickle.dump({'rng': rng.getstate(), 'pop': pop, 'fit': fit, 'hist': hist, 'gen': gen+1},
                    open(ckpt_path, 'wb'))
    best = pop[0]
    rec = {'tid': tid, 'seed': seed, 'arm': 'A6', 'best_fitness': fit[0],
           'best_genome': best, 'hist': hist, 'n_evals': MU + LAM*GENS,
           'cache_size': len(ev.cache), 'finished': time.strftime('%Y-%m-%d %H:%M:%S')}
    with open('results/a6_runs.jsonl', 'a') as fh:
        fh.write(json.dumps(rec) + '\n')
    tmp = ev.cache_path + '.tmp'
    json.dump(ev.cache, open(tmp, 'w')); os.replace(tmp, ev.cache_path)
    os.remove(ckpt_path)
    print('DONE', tid, seed, 'f=', round(fit[0], 6), 'cache', len(ev.cache), flush=True)

if __name__ == '__main__':
    t0 = time.time()
    run(sys.argv[1], int(sys.argv[2]))
    print('wall_s', round(time.time()-t0), flush=True)
