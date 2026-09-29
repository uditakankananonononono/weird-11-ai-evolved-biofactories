#!/usr/bin/env python3
"""A7 mechanical locked-rule verdict (amendment 2026-09-29 16:45 IST), run ONLY after validation PASS.
Pure arithmetic on validated records - no LPs. Writes results/a7_verdict.json."""
import json

MILD = ['GLC_PERT_MINUS20', 'GLC_PERT_PLUS20', 'O2_PERT_MINUS50']
SEVERE = ['GLC_LOW', 'GLC_MID', 'ANAEROBIC', 'GLYCEROL', 'ACETATE']
TARGETS = ['14BDO', 'ISOBUTANOL', 'LYCOPENE']

def r_tiered_v23c(legs, F):
    nom = legs['GLC_AEROBIC']
    r_pert = sum((legs[c]/nom if nom > 0 else 0.0) for c in MILD)/3
    r_shift = sum((legs[c]/F[c] if F[c] > 0 else 0.0) for c in SEVERE)/5
    return 0.5*r_pert + 0.5*r_shift, r_pert

def main():
    rv = json.load(open('results/rescore_v23c_verdict.json'))
    rd = json.load(open('results/rescore_v23c.json'))
    a7 = {}
    for l in open('results/a7_runs.jsonl'):
        r = json.loads(l); a7.setdefault(r['tid'], {})[str(r['seed'])] = r
    out = {'amendment': '2026-09-29 16:45 IST (commit 42c6ffb)', 'validation': 'handcheck_a7_selections PASS required before this step',
           'frontier_note': 'v23c frontier is zero in all five severe conditions on every target (locked zero-frontier rule): R_shift = 0 for all genomes; R_tiered comparisons reduce to R_pert (locked disclosure).',
           'per_target': {}}
    for tid in TARGETS:
        F = rv['per_target'][tid]['frontier_v23c']
        a6_best = max(rv['per_target'][tid]['a6_R_tiered_per_seed'].values())
        a7_rt = {}
        for s, r in sorted(a7[tid].items()):
            rt, rp = r_tiered_v23c(r['selection_legs'], F)
            a7_rt[s] = {'R_tiered': rt, 'R_pert': rp, 'nom': r['selection_nom'], 'fitness_nominal': r['best_fitness']}
        a7_best = max(v['R_tiered'] for v in a7_rt.values())
        degenerate = (a6_best == 0 or a7_best == 0)
        tol = 1e-9 if degenerate else 1e-9*max(1.0, abs(a6_best))
        if a7_best < a6_best - tol: verdict = 'NECESSITY-WIN'
        elif a7_best > a6_best + tol: verdict = 'SURPRISE'
        else: verdict = 'NULL'
        # A6 selection nominals for side-by-side SECONDARY
        a6_rows = [r for r in rd['per_target'][tid]['rows'] if any(p.startswith('A6_') for p in r['provenance'])]
        out['per_target'][tid] = {
            'a7_selections': a7_rt, 'a6_best_R_tiered': a6_best, 'a7_best_R_tiered': a7_best,
            'a6_selection_nominals': sorted({r['nom'] for r in a6_rows}),
            'degenerate_band_rule_used': degenerate, 'verdict': verdict}
    json.dump(out, open('results/a7_verdict.json', 'w'), indent=1)
    for tid in TARGETS:
        t = out['per_target'][tid]
        print(tid, t['verdict'], '| A7 best', round(t['a7_best_R_tiered'], 6), '| A6 best', round(t['a6_best_R_tiered'], 6),
              '| A7 noms', sorted({round(v['nom'],4) for v in t['a7_selections'].values()}))
if __name__ == '__main__':
    main()
