import json, sys
import numpy as np
from scipy.optimize import linprog
import cobra.util.array as cua
sys.path.insert(0,'src')
from search_ea_fast import get_model
BATT = json.load(open('data/condition_battery.json'))
BIOMASS='BIOMASS_Ec_iML1515_core_75p37M'
gen={"ko_ackApta": False, "ko_pflB": False, "ko_ldhA": False, "cofeed_glycerol": True, "adh_nadh": True, "adh_nadph": False}
m, PROD = get_model('ISOBUTANOL')
# apply genome exactly as battery_v23_highs.apply_genome
m.reactions.get_by_id('IBUTDH').bounds=(0,1000) if gen.get('adh_nadh') else (0,0)
m.reactions.get_by_id('IBUTDHP').bounds=(0,1000) if gen.get('adh_nadph') else (0,0)
for r,k in [('ACKr','ko_ackApta'),('PTAr','ko_ackApta')]:
    m.reactions.get_by_id(r).bounds=(0,0) if gen.get(k) else (-1000,1000)
m.reactions.get_by_id('PFL').bounds=(0,0) if gen.get('ko_pflB') else (0,1000)
m.reactions.get_by_id('LDH_D').bounds=(0,0) if gen.get('ko_ldhA') else (0,1000)
m.reactions.get_by_id('EX_glyc_e').lower_bound=-4.0 if gen.get('cofeed_glycerol') else 0.0
S=cua.create_stoichiometric_matrix(m)
rxns=[r.id for r in m.reactions]
b_eq=np.zeros(S.shape[0])
def lp(bounds,obj):
    c=np.zeros(len(rxns)); c[rxns.index(obj)]=-1.0
    r=linprog(c,A_eq=S,b_eq=b_eq,bounds=bounds,method='highs')
    if r.status!=0: return None,r
    return max(-r.fun,0.0),r

if PROD is None:
    PROD=[r for r in rxns if 'ibut' in r.lower() and r.startswith('EX')]
    print('prod candidates',PROD); PROD=PROD[0]
print('PROD rxn:',PROD)
for cond in BATT['battery']:
    with m:
        for ex,b in BATT['base_condition']['bounds'].items(): m.reactions.get_by_id(ex).lower_bound=b
        for ex,b in cond['bounds'].items(): m.reactions.get_by_id(ex).lower_bound=b
        bounds=[(r.lower_bound,r.upper_bound) for r in m.reactions]
        g,gr=lp(bounds,BIOMASS)
        if not g or g<=0: print(cond['id'],'infeasible growth'); continue
        bounds2=list(bounds); bounds2[rxns.index(BIOMASS)]=(0.5*g,0.5*g)
        p,pr=lp(bounds2,PROD)
        # carbon accounting: glucose consumed at the product-optimal point
        i_glc=rxns.index('EX_glc__D_e'); v_glc=pr.x[i_glc] if p is not None else None
        print(f"{cond['id']:10s} gmax={g:.6f} prod={p:.6f} glc_flux_at_prod_opt={v_glc:.4f} glc_lb={bounds[rxns.index('EX_glc__D_e')][0]}")
