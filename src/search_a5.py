#!/usr/bin/env python3
"""W11 pool-v4 A5 STAGE 1 (amendment 2026-09-28 16:02 IST, locked pre-computation).
A0-baseline EA with FULL trajectory logging (eval_hist dumped per run). Bit-deterministic
replica of the committed A0 runs; per-run equivalence check: stage-1 best_flux must equal
the committed A0 best_flux for the same (target, seed) - mismatches are disclosed, not patched.
Checkpointed per generation (bit-exact resume, same fault-tolerance pattern as search_ea_v4)."""
import json, random, os, sys, time, pickle
sys.path.insert(0, 'src')
import importlib.util
_argv = sys.argv
spec = importlib.util.spec_from_file_location('ea', 'src/search_ea_v4.py')
ea = importlib.util.module_from_spec(spec); sys.argv = ['x']
spec.loader.exec_module(ea)
sys.argv = _argv

POOL, HOST14, MU, LAM, GENS = ea.POOL, ea.HOST14, ea.MU, ea.LAM, ea.GENS
fitness, key = ea.fitness, ea.key
CKPT_DIR = 'results/a5_ckpt'
TRAJ_DIR = 'results/a5_traj'

def run_a5(tid, seed):
    bits = HOST14 + list(POOL[tid]['blocks'])
    nb = len(bits)
    os.makedirs(CKPT_DIR, exist_ok=True)
    os.makedirs(TRAJ_DIR, exist_ok=True)
    ckpt_path = os.path.join(CKPT_DIR, f'{tid}_A5_{seed}.pkl')
    rng = random.Random(seed)
    rand_g = lambda: {b: rng.random() < 0.5 for b in bits}
    seen = set()
    eval_hist = []
    def evalg(g):
        k = key(g, bits)
        seen.add(k)
        f = fitness(tid, g)
        eval_hist.append((list(k), f))
        return f
    if os.path.exists(ckpt_path):
        with open(ckpt_path, 'rb') as fh:
            st = pickle.load(fh)
        rng.setstate(st['rng'])
        pop, fit, hist = st['pop'], st['fit'], st['hist']
        seen = set(map(tuple, st['seen']))
        eval_hist = [(list(x), f) for x, f in st['eval_hist']]
        gen0 = st['gen']
    else:
        pop = [rand_g() for _ in range(MU)]
        fit = [evalg(g) for g in pop]
        hist = [max(fit)]
        gen0 = 0
    for gen in range(gen0, GENS):
        kids = []
        while len(kids) < LAM:
            cand = rng.sample(list(zip(fit, pop)), 3)
            topf = max(x[0] for x in cand)
            tied = [x for x in cand if x[0] == topf]
            p1 = tied[0][1]  # A0 baseline: no tie-break, single mutation attempt
            kid = {b: (not v if rng.random() < (1/nb) else v) for b, v in p1.items()}
            kids.append(kid)
        kfit = [evalg(k) for k in kids]
        both = sorted(zip(fit + kfit, pop + kids), key=lambda x: -x[0])
        pop = [g for _, g in both[:MU]]; fit = [f for f, _ in both[:MU]]
        hist.append(fit[0])
        with open(ckpt_path, 'wb') as fh:
            pickle.dump({'rng': rng.getstate(), 'pop': pop, 'fit': fit, 'hist': hist,
                         'seen': [list(k) for k in seen], 'eval_hist': eval_hist,
                         'gen': gen + 1}, fh)
    os.remove(ckpt_path)
    return {'target': tid, 'seed': seed, 'arm': 'A5',
            'best_flux': fit[0], 'best_genome': pop[0],
            'n_evals': len(seen), 'eval_hist': eval_hist}

if __name__ == '__main__':
    # committed A0 best_flux for equivalence verification
    committed = {}
    for line in open('results/ea_v4_runs.jsonl'):
        r = json.loads(line)
        if r['arm'] == 'A0' and (r['target'], r['seed']) not in committed:
            committed[(r['target'], r['seed'])] = r['best_flux']
    done = set()
    done_rows = 'results/a5_runs.jsonl'
    if os.path.exists(done_rows):
        for line in open(done_rows):
            r = json.loads(line); done.add((r['target'], r['seed']))
    targets = sys.argv[1].split(',')
    seeds = [int(s) for s in sys.argv[2].split(',')]
    for tid in targets:
        ea.get_model(tid)
        for seed in seeds:
            if (tid, seed) in done: continue
            t0 = time.time()
            r = run_a5(tid, seed)
            ref = committed.get((tid, seed))
            match = (ref == r['best_flux'])
            traj = r.pop('eval_hist')
            r['wall_s'] = round(time.time() - t0, 2)
            r['equiv_committed_A0'] = {'ref_best_flux': ref, 'match': match}
            json.dump({'target': tid, 'seed': seed, 'eval_hist': traj},
                      open(os.path.join(TRAJ_DIR, f'{tid}_{seed}.json'), 'w'))
            with open(done_rows, 'a') as f: f.write(json.dumps(r) + '\n')
            print('A5', tid, seed, 'best', round(r['best_flux'], 4),
                  'equiv', match, f"{r['wall_s']}s", flush=True)
    print('a5 stage1 chunk done')
