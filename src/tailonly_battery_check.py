import sys, json
sys.path.insert(0,'src')
exec(open('src/battery_tiered_v2.py').read().split('out = {}')[0])
TAIL = {'ko_ackApta':False,'ko_pflB':False,'ko_ldhA':False,'cofeed_glycerol':False,'routeA_kgd':False,'routeB_sucd':False}
frontier = json.load(open('results/battery_tiered_v2.json'))['results']['14BDO']['frontier_severe']
import cobra
m, prod = get_model('14BDO')
apply(m, '14BDO', TAIL)
nom = flux_cond(m, prod, CONDS[0])
mild = {c['id']: (flux_cond(m, prod, c)/nom if nom>0 else 0) for c in CONDS if c['id'] in MILD}
sev = {c['id']: (flux_cond(m, prod, c)/frontier[c['id']] if frontier[c['id']]>0 else 0) for c in CONDS if c['id'] in SEVERE}
mild_pass = all(v>=0.8 for v in mild.values()); sev_pass = all(v>=0.8 for v in sev.values())
R_pert = sum(min(v,1.0) for v in mild.values())/3; R_shift = sum(min(v,1.0) for v in sev.values())/5
print(json.dumps({'nominal':round(nom,4),'mild':{k:round(v,4) for k,v in mild.items()},'severe_rel':{k:round(v,4) for k,v in sev.items()},'R_pert':round(R_pert,4),'R_shift':round(R_shift,4),'R_tiered':round(0.5*R_pert+0.5*R_shift,4),'mild_pass':mild_pass,'severe_pass':sev_pass,'battery_pass':mild_pass and sev_pass}, indent=1))
