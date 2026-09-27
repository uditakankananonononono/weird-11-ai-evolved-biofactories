#!/usr/bin/env python3
"""W11 MC FBA uncertainty (amendment 13:35 IST, locked pre-compute). One target per invocation."""
import cobra, json, sys, random, statistics as st
sys.path.insert(0,'src')
from search_ea_fast import get_model
BATT=json.load(open('data/condition_battery.json'))
BIOMASS='BIOMASS_Ec_iML1515_core_75p37M'
MILD=['GLC_PERT_MINUS20','GLC_PERT_PLUS20','O2_PERT_MINUS50']
SEVERE=['GLC_LOW','GLC_MID','ANAEROBIC','GLYCEROL','ACETATE']
CONDS=[dict(id='GLC_AEROBIC',bounds=BATT['base_condition']['bounds'])]+BATT['battery']
tid=sys.argv[1]
v3=json.load(open('results/battery_tiered_v3.json'))['results']
g=v3[tid]['best_by_R_tiered']['genome']
fr=v3[tid]['frontier_severe']
def apply(m,tid,g):
    if tid=='14BDO':
        m.reactions.get_by_id('BDO1').bounds=(0,1000) if g.get('routeA_kgd') else (0,0)
        m.reactions.get_by_id('BDO1B').bounds=(0,1000) if g.get('routeB_sucd') else (0,0)
    elif tid=='ISOBUTANOL':
        m.reactions.get_by_id('IBUTDH').bounds=(0,1000) if g.get('adh_nadh') else (0,0)
        m.reactions.get_by_id('IBUTDHP').bounds=(0,1000) if g.get('adh_nadph') else (0,0)
    elif tid=='LYCOPENE':
        m.reactions.get_by_id('DXPS').lower_bound=1.0 if g.get('dxs_push') else 0.0
        m.reactions.get_by_id('IPDDI').lower_bound=0.5 if g.get('idi_push') else 0.0
    m.reactions.get_by_id('ACKr').bounds=(0,0) if g.get('ko_ackApta') else (-1000,1000)
    m.reactions.get_by_id('PTAr').bounds=(0,0) if g.get('ko_ackApta') else (-1000,1000)
    m.reactions.get_by_id('PFL').bounds=(0,0) if g.get('ko_pflB') else (0,1000)
    m.reactions.get_by_id('LDH_D').bounds=(0,0) if g.get('ko_ldhA') else (0,1000)
    m.reactions.get_by_id('EX_glyc_e').lower_bound=-4.0 if g.get('cofeed_glycerol') else 0.0
    m.reactions.get_by_id('ALCD2x').bounds=(0,0) if g.get('ko_adhE') else (-1000,1000)
    m.reactions.get_by_id('TPI').bounds=(0,0) if g.get('ko_tpiA') else (-1000,1000)
def flux(m,prod,cond,jit):
    with m:
        for ex,b in BATT['base_condition']['bounds'].items(): m.reactions.get_by_id(ex).lower_bound=b*jit(ex)
        for ex,b in cond['bounds'].items(): m.reactions.get_by_id(ex).lower_bound=b*jit(ex)
        bio=m.reactions.get_by_id(BIOMASS); bio.lower_bound,bio.upper_bound=0.0,1000.0
        m.objective=bio; gg=m.slim_optimize()
        if gg!=gg or gg<=0: return 0.0
        bio.lower_bound=bio.upper_bound=0.5*gg
        m.objective=m.reactions.get_by_id(prod)
        p=m.slim_optimize()
        return float(p) if (p==p and p and p>0) else 0.0
rng=random.Random(260927)
m,prod=get_model(tid)
rts=[]; passes=0
for _ in range(200):
    table={ex:rng.uniform(0.8,1.2) for c in CONDS for ex in c['bounds']}
    jit=lambda ex: table.get(ex,1.0)
    with m:
        apply(m,tid,g)
        F={c['id']:flux(m,prod,c,jit) for c in CONDS}
    nom=F['GLC_AEROBIC']
    mild=[F[k]/nom if nom>0 else 0.0 for k in MILD]
    sev=[F[k]/fr[k] if fr[k]>0 else 0.0 for k in SEVERE]
    rts.append(0.5*sum(mild)/3+0.5*sum(sev)/5)
    if all(x>=0.8 for x in mild) and all(x>=0.8 for x in sev): passes+=1
rts.sort()
out={'mean_R_tiered':round(st.mean(rts),4),'sd':round(st.pstdev(rts),4),
 'p5':round(rts[9],4),'p95':round(rts[189],4),'battery_pass_fraction':round(passes/200,3)}
json.dump({tid:out},open(f'/tmp/mc_{tid}.json','w'))
print(tid,out)
