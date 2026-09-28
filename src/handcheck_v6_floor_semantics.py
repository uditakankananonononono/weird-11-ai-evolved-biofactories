import json, sys
import numpy as np
from scipy.optimize import linprog
import cobra.util.array as cua
sys.path.insert(0,'src')
import importlib.util
spec = importlib.util.spec_from_file_location('ea','src/search_ea_v4.py')
ea = importlib.util.module_from_spec(spec); sys.argv=['x']; spec.loader.exec_module(ea)
BATT = json.load(open('data/condition_battery.json'))
BIOMASS='BIOMASS_Ec_iML1515_core_75p37M'
CONDS=[dict(id='GLC_AEROBIC',bounds=BATT['base_condition']['bounds'])]+BATT['battery']
def lp(S,b_eq,bounds,rxns,obj):
    c=np.zeros(len(rxns)); c[rxns.index(obj)]=-1.0
    r=linprog(c,A_eq=S,b_eq=b_eq,bounds=bounds,method='highs')
    if r.status!=0: return None
    return max(-r.fun,0.0)
# default biomass bounds check
m0, _ = ea.get_model('ISOBUTANOL')
print('default BIOMASS bounds:', m0.reactions.get_by_id(BIOMASS).bounds)
# sample: 2 genomes per target from committed v6 rows
v6=json.load(open('results/battery_v6.json'))
runs={}
for line in open('results/ea_v4_runs.jsonl'):
    r=json.loads(line); runs[(r['target'],r['arm'],r['seed'])]=r
fails=0; n=0
for tid in ['14BDO','ISOBUTANOL','LYCOPENE']:
    m,prod=ea.get_model(tid)
    rxns=[r.id for r in m.reactions]
    S=cua.create_stoichiometric_matrix(m,array_type='lil').tocsc()
    b_eq=np.zeros(S.shape[0])
    keys=sorted(k for k in v6[tid]['genome_rows'])[:2]
    for gk in keys:
        arm,seed=gk.rsplit('_',1); genome=runs[(tid,arm,int(seed))]['best_genome']
        committed=v6[tid]['genome_rows'][gk]['row']
        with m:
            ea.apply_genome(m,tid,genome)
            for cond in CONDS:
                for ex,b in BATT['base_condition']['bounds'].items(): m.reactions.get_by_id(ex).lower_bound=b
                for ex,b in cond['bounds'].items(): m.reactions.get_by_id(ex).lower_bound=b
                # INDEPENDENT: explicitly unpin biomass before growth solve
                m.reactions.get_by_id(BIOMASS).bounds=(0.0,1000.0)
                bounds=[(r.lower_bound,r.upper_bound) for r in m.reactions]
                g=lp(S,b_eq,bounds,rxns,BIOMASS) or 0.0
                bounds[rxns.index(BIOMASS)]=(0.5*g,0.5*g)
                p=lp(S,b_eq,bounds,rxns,prod) or 0.0
                cval=committed[cond['id']]
                ok=abs(p-cval)<=1e-9*max(1.0,abs(cval))
                n+=1
                if not ok:
                    fails+=1
                    print(f'MISMATCH {tid} {gk} {cond["id"]}: fresh={p:.6f} committed={cval:.6f}')
print(f'{n} leg values re-derived, {fails} mismatches (1e-9 rel tolerance)')
