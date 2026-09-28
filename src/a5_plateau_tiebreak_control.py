#!/usr/bin/env python3
"""A5 plateau tie-break control (amendment 2026-09-28 20:10 IST, 10faf32 - locked before outcome inspection).
Endpoints per run: f_tie (fraction of plateau at A5-selected R_tiered within 1e-9), gap (A5 - plateau mean),
percentile (mid-rank). WIN: median f_tie <= 0.2 over 15 runs. Full enumeration, no RNG."""
import json, statistics
d=json.load(open('results/battery_v6.json'))
rows=[]; per_target={}
for tid in ['14BDO','ISOBUTANOL','LYCOPENE']:
    t=d[tid]
    plats={}
    for k,v in t['plateau_rows'].items():
        seed=k.split('_')[0]; plats.setdefault(seed,[]).append(v['R_tiered'])
    for sel in t['a5_selections']:
        seed=str(sel['seed']); a5=sel['R_tiered']; dist=plats[seed]
        n=len(dist); n_tie=sum(1 for x in dist if abs(x-a5)<=1e-9)
        f=n_tie/n
        gap=a5-statistics.mean(dist)
        below=sum(1 for x in dist if x<a5-1e-9); ties=n_tie
        pct=(below+0.5*ties)/n*100
        a0=t['genome_rows'][f'A0_{seed}']['row'] if f'A0_{seed}' in t['genome_rows'] else None
        rows.append(dict(target=tid,seed=seed,plateau=n,a5=round(a5,4),f_tie=round(f,4),gap=round(gap,4),percentile=round(pct,1)))
        per_target.setdefault(tid,[]).append((f,gap))
med=statistics.median(r['f_tie'] for r in rows)
verdict='WIN' if med<=0.2 else 'NULL'
out={'amendment':'10faf32 2026-09-28 20:10 IST','rule':'WIN if median f_tie <= 0.2 over 15 runs',
     'per_run':rows,'median_f_tie':round(med,4),'verdict':verdict,
     'per_target':{t:{'median_f_tie':round(statistics.median(x[0] for x in v),4),
                      'median_gap':round(statistics.median(x[1] for x in v),4)} for t,v in per_target.items()}}
json.dump(out,open('results/a5_plateau_tiebreak_control.json','w'),indent=1)
for r in rows: print(r)
print('median f_tie', round(med,4), '=> VERDICT', verdict)
for t,v in out['per_target'].items(): print(t,v)
