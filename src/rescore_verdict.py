#!/usr/bin/env python3
"""Mechanical locked-rule application for the v23c re-score (amendment 8274f9f), run ONLY after
handcheck_rescore.py PASS. Pure arithmetic on validated rows - no LPs. Writes results/rescore_v23c_verdict.json."""
import json, sys

MILD = ['GLC_PERT_MINUS20', 'GLC_PERT_PLUS20', 'O2_PERT_MINUS50']
SEVERE = ['GLC_LOW', 'GLC_MID', 'ANAEROBIC', 'GLYCEROL', 'ACETATE']
SEEDS = ['260927', '261927', '262927', '263927', '264927']
TARGETS = ['14BDO', 'ISOBUTANOL', 'LYCOPENE']

def main():
    d = json.load(open('results/rescore_v23c.json'))
    out = {'amendment': '8274f9f 2026-09-29 14:35 IST', 'validation': 'handcheck_rescore.py PASS required before this step',
           'per_target': {}}
    for tid in TARGETS:
        rows = d['per_target'][tid]['rows']
        by_prov = {}
        for r in rows:
            for p in r['provenance']:
                by_prov.setdefault(p, r)
        a0a4 = [r for r in rows if any(p.split('_')[0] in ['A0','A1','A2','A3','A4'] for p in r['provenance'])]
        F = {c: max((r['legs'][c] for r in a0a4), default=0.0) for c in SEVERE}
        zeroF = [c for c in SEVERE if F[c] <= 0]
        def rt(r):
            nom = r['nom']
            r_pert = sum((r['legs'][c]/nom if nom > 0 else 0.0) for c in MILD)/3
            r_shift = sum((r['legs'][c]/F[c] if F[c] > 0 else 0.0) for c in SEVERE)/5
            return 0.5*r_pert + 0.5*r_shift, r_pert, r_shift
        for r in rows:
            r['R_tiered'], r['R_pert'], r['R_shift'] = rt(r)
        plat = [r for r in rows if any(p.startswith('plateau_') for p in r['provenance'])]
        pmax = max(r['R_tiered'] for r in plat)
        pnom_max = max(r['nom'] for r in plat)
        degenerate = pmax == 0
        def exceeds(a, b):
            return (a - b) > (1e-9 if degenerate else 1e-9*max(1.0, abs(b)))
        a6 = {p: by_prov[p] for p in by_prov if p.startswith('A6_')}
        a6_rt = {s.split('_')[1]: r['R_tiered'] for s, r in ((p, r) for p, r in a6.items())}
        win = any(exceeds(v, pmax) for v in a6_rt.values())
        a0_rt = {s.split('_')[1]: by_prov[f'A0_{s.split("_")[1]}']['R_tiered']
                 for s, r in ((p, r) for p, r in a6.items()) if f'A0_{s.split("_")[1]}' in by_prov}
        tie_level = (not win) and any(exceeds(a6_rt[s], a0_rt.get(s, 0.0)) and not exceeds(a6_rt[s], pmax) for s in a6_rt)
        null = (not win) and all(abs(v - pmax) <= (1e-9 if degenerate else 1e-9*max(1.0, abs(pmax))) for v in a6_rt.values())
        verdict = 'WIN' if win else ('TIE-BREAK-LEVEL' if tie_level else ('NULL' if null else 'BELOW-PLATEAU'))
        out['per_target'][tid] = {
            'frontier_v23c': F, 'zero_frontier_conditions': zeroF,
            'plateau_n': len(plat), 'plateau_max_R_tiered': pmax, 'plateau_max_nominal': pnom_max,
            'a6_R_tiered_per_seed': a6_rt, 'a0_realized_R_tiered_per_seed': a0_rt,
            'degenerate_frontier_rule_used': degenerate,
            'a6_nominal_retention_vs_plateau': {s: (by_prov[f'A6_{s}']['nom']/pnom_max if pnom_max > 0 else None) for s in SEEDS if f'A6_{s}' in by_prov},
            'verdict': verdict}
        # persist enriched rows back for the record
    json.dump(out, open('results/rescore_v23c_verdict.json', 'w'), indent=1)
    json.dump(d, open('results/rescore_v23c.json', 'w'), indent=1)
    for tid in TARGETS:
        t = out['per_target'][tid]
        print(tid, t['verdict'], '| plateau max', round(t['plateau_max_R_tiered'], 6),
              '| A6', {s: round(v, 6) for s, v in t['a6_R_tiered_per_seed'].items()},
              '| zeroF', t['zero_frontier_conditions'])
if __name__ == '__main__':
    main()
