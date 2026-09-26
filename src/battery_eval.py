#!/usr/bin/env python3
"""W11 battery evaluation of evolved architectures (locked battery: data/condition_battery.json;
pass = >=80% flux retention in ALL 9 conditions; growth fixed 50% max per search_design).
Evaluates: best-per-target genomes from ea_runs.jsonl + the 14BDO tail-only H2 candidate
(both route blocks OFF - native GABA-shunt feed)."""
import cobra, json, sys
sys.path.insert(0, 'src')
from search_ea_fast import get_model

BATT = json.load(open('data/condition_battery.json'))
BIOMASS = 'BIOMASS_Ec_iML1515_core_75p37M'
GMAX = 0.876997

def eval_genome(tid, genome):
    m, prod = get_model(tid)
    out = {}
    for cond in [dict(id='GLC_AEROBIC', bounds=BATT['base_condition']['bounds'])] + BATT['battery']:
        with m:
            # reset condition bounds: apply condition bounds on top of base defaults
            for ex, b in BATT['base_condition']['bounds'].items():
                m.reactions.get_by_id(ex).lower_bound = b
            for ex, b in cond['bounds'].items():
                m.reactions.get_by_id(ex).lower_bound = b
            # carbon shifts: zero glucose when specified
            if cond['bounds'].get('EX_glc__D_e') == 0.0:
                m.reactions.get_by_id('EX_glc__D_e').lower_bound = 0.0
            if tid == '14BDO':
                m.reactions.get_by_id('BDO1').bounds = (0,1000) if genome.get('routeA_kgd') else (0,0)
                m.reactions.get_by_id('BDO1B').bounds = (0,1000) if genome.get('routeB_sucd') else (0,0)
            elif tid == 'ISOBUTANOL':
                m.reactions.get_by_id('IBUTDH').bounds = (0,1000) if genome.get('adh_nadh') else (0,0)
                m.reactions.get_by_id('IBUTDHP').bounds = (0,1000) if genome.get('adh_nadph') else (0,0)
            elif tid == 'LYCOPENE':
                m.reactions.get_by_id('DXPS').lower_bound = 1.0 if genome.get('dxs_push') else 0.0
                m.reactions.get_by_id('IPDDI').lower_bound = 0.5 if genome.get('idi_push') else 0.0
            bio = m.reactions.get_by_id(BIOMASS)
            bio.lower_bound, bio.upper_bound = 0.0, 1000.0
            m.objective = bio
            # amendment 22:13 IST: growth = 50% of CONDITION-SPECIFIC max
            g = m.slim_optimize()
            if g != g or g <= 0:  # nan = infeasible
                out[cond['id']] = {'flux': 0.0, 'note': 'no growth under condition'}
                continue
            bio.lower_bound = bio.upper_bound = 0.5 * g
            m.objective = m.reactions.get_by_id(prod)
            p = m.slim_optimize()
            out[cond['id']] = {'flux': round(float(p), 4) if (p == p and p and p > 0) else 0.0}
    nom = out['GLC_AEROBIC']['flux']
    ret = {k: (round(v['flux']/nom, 3) if nom > 0 else None) for k, v in out.items() if k != 'GLC_AEROBIC'}
    passed = nom > 0 and all(r is not None and r >= 0.8 for r in ret.values())
    return {'genome': genome, 'nominal': nom, 'conditions': out, 'retention': ret, 'battery_pass': passed}

best = {}
for line in open('results/ea_runs.jsonl'):
    r = json.loads(line)
    if r['mode'] != 'single_condition': continue
    t = r['target']
    if t not in best or r['best_flux'] > best[t]['best_flux']: best[t] = r

res = {}
for t, r in best.items():
    res[f"{t}__EA_best"] = eval_genome(t, r['best_genome'])
    print(t, 'EA best battery_pass:', res[f"{t}__EA_best"]['battery_pass'],
          'min retention:', min(res[f"{t}__EA_best"]['retention'].values()), flush=True)
res['14BDO__tail_only'] = eval_genome('14BDO', {'routeA_kgd': False, 'routeB_sucd': False})
print('14BDO tail-only nominal:', res['14BDO__tail_only']['nominal'],
      'battery_pass:', res['14BDO__tail_only']['battery_pass'])
json.dump(res, open('results/battery_eval.json','w'), indent=1)
print('written results/battery_eval.json')
