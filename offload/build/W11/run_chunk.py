#!/usr/bin/env python3
"""W11 A6 chunk runner - one command per target chunk, Windows/Linux/macOS.
Usage:  python run_chunk.py 14BDO [workers]
Runs the 5 locked seeds in waves of <workers> (default: CPU count), then writes
a6_done_<TARGET>.zip with run records + caches + logs. Bit-exact resume: re-run
the same command after any interruption; finished seeds are skipped automatically."""
import os, sys, subprocess, zipfile, glob, time

SEEDS = [260927, 261927, 262927, 263927, 264927]

def done_seeds(tid):
    done = set()
    if os.path.exists('results/a6_runs.jsonl'):
        for line in open('results/a6_runs.jsonl'):
            try:
                import json; r = json.loads(line)
                if r.get('tid') == tid: done.add(r['seed'])
            except Exception: pass
    return done

def main():
    tid = sys.argv[1]
    assert tid in ('14BDO','ISOBUTANOL','LYCOPENE'), 'target must be 14BDO, ISOBUTANOL or LYCOPENE'
    workers = int(sys.argv[2]) if len(sys.argv) > 2 else (os.cpu_count() or 2)
    os.makedirs('results', exist_ok=True)
    queue = [s for s in SEEDS if s not in done_seeds(tid)]
    print(f'{tid}: {len(queue)} seeds to run on {workers} workers', flush=True)
    while queue:
        wave, queue = queue[:workers], queue[workers:]
        procs = []
        for s in wave:
            log = open(f'results/a6_log_{tid}_{s}.txt', 'w')
            kw = {}
            if os.name == 'posix': kw['preexec_fn'] = lambda: os.nice(10)
            procs.append((s, subprocess.Popen([sys.executable, 'src/search_a6.py', tid, str(s)],
                                              stdout=log, stderr=subprocess.STDOUT, **kw)))
            print(f'  seed {s} launched', flush=True)
        for s, p in procs:
            p.wait()
            print(f'  seed {s} exit={p.returncode}', flush=True)
    z = f'a6_done_{tid}.zip'
    with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED) as zh:
        for pat in ['results/a6_runs.jsonl'] + glob.glob('results/a6_cache_*.json') + glob.glob(f'results/a6_log_{tid}_*.txt'):
            if os.path.exists(pat): zh.write(pat)
    print(f'DONE - send back {z}', flush=True)

if __name__ == '__main__':
    main()
