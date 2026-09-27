#!/usr/bin/env python3
"""W11 3B HELD-OUT TARGET 3-HP (amendment 2026-09-27 10:04 IST 3B, locked pre-construction).
MCR1: malonyl-CoA + NADPH -> malonate semialdehyde + CoA + NADP+ + H+
MCR2: malonate semialdehyde + NADPH + H+ -> 3-hydroxypropionate + NADP+
+ transport + EX_3hp_e. Pool = 6 host levers only (64 genomes). Tiered battery identical;
severe frontier WITHIN the 3-HP pool. WIN 3B: one-tailed Fisher p<0.05 for motif
M={cofeed_glycerol, ko_pflB} enrichment among battery-passers; else falsified (no loosening)."""
import cobra, json, itertools, sys
sys.path.insert(0, 'src')
from benchmark_flux import BASE, rxn, met, add_exchange
from scipy.stats import fisher_exact

BATT = json.load(open('data/condition_battery.json'))
BIOMASS = 'BIOMASS_Ec_iML1515_core_75p37M'
HOST_BLOCKS = ['ko_ackApta','ko_pflB','ko_ldhA','cofeed_glycerol','ko_adhE','ko_tpiA']
MILD = ['GLC_PERT_MINUS20','GLC_PERT_PLUS20','O2_PERT_MINUS50']
SEVERE = ['GLC_LOW','GLC_MID','ANAEROBIC','GLYCEROL','ACETATE']
CONDS = [dict(id='GLC_AEROBIC', bounds=BATT['base_condition']['bounds'])] + BATT['battery']

def build_3HP(m):
    malsa = met(m, 'malsa_c', 'malonate semialdehyde')
    hp = met(m, '3hp_c', '3-hydroxypropionate')
    g = lambda i: m.metabolites.get_by_id(i)
    rxn(m,'MCR1','malonyl-CoA reductase (MCR1)',{g('malcoa_c'):-1,g('nadph_c'):-1,malsa:1,g('coa_c'):1,g('nadp_c'):1,g('h_c'):1})
    rxn(m,'MCR2','malonate semialdehyde reductase (MCR2)',{malsa:-1,g('nadph_c'):-1,g('h_c'):-1,hp:1,g('nadp_c'):1})
    return add_exchange(m,'3hp_c','3hp_e','3-hydroxypropionate').id

def apply_host(m, genome):
    m.reactions.get_by_id('ACKr').bounds = (0,0) if genome.get('ko_ackApta') else (-1000,1000)
    m.reactions.get_by_id('PTAr').bounds = (0,0) if genome.get('ko_ackApta') else (-1000,1000)
    m.reactions.get_by_id('PFL').bounds = (0,0) if genome.get('ko_pflB') else (0,1000)
    m.reactions.get_by_id('LDH_D').bounds = (0,0) if genome.get('ko_ldhA') else (0,1000)
    m.reactions.get_by_id('EX_glyc_e').lower_bound = -4.0 if genome.get('cofeed_glycerol') else 0.0
    m.reactions.get_by_id('ALCD2x').bounds = (0,0) if genome.get('ko_adhE') else (-1000,1000)
    m.reactions.get_by_id('TPI').bounds = (0,0) if genome.get('ko_tpiA') else (-1000,1000)

def flux_cond(m, prod, cond):
    with m:
        for ex,b in BATT['base_condition']['bounds'].items(): m.reactions.get_by_id(ex).lower_bound = b
        for ex,b in cond['bounds'].items(): m.reactions.get_by_id(ex).lower_bound = b
        bio = m.reactions.get_by_id(BIOMASS); bio.lower_bound, bio.upper_bound = 0.0, 1000.0
        m.objective = bio
        g = m.slim_optimize()
        if g != g or g <= 0: return 0.0
        bio.lower_bound = bio.upper_bound = 0.5*g
        m.objective = m.reactions.get_by_id(prod)
        p = m.slim_optimize()
        return float(p) if (p==p and p and p>0) else 0.0

m0 = cobra.io.read_sbml_model('data/models/iML1515.xml.gz')
for ex,b in BASE.items(): m0.reactions.get_by_id(ex).lower_bound = b
prod = build_3HP(m0)
genomes = [dict(zip(HOST_BLOCKS, hb)) for hb in itertools.product([False,True], repeat=6)]
F = []
for gn in genomes:
    with m0:
        apply_host(m0, gn)
        F.append({c['id']: flux_cond(m0, prod, c) for c in CONDS})
nominal = [f['GLC_AEROBIC'] for f in F]
frontier = {k: max(f[k] for f in F) for k in SEVERE}
rows = []
for gn, f, nom in zip(genomes, F, nominal):
    mild = {k: (f[k]/nom if nom>0 else 0.0) for k in MILD}
    sev = {k: (f[k]/frontier[k] if frontier[k]>0 else 0.0) for k in SEVERE}
    Rp = min(mild.values()) if mild else 0.0; Rs = min(sev.values()) if sev else 0.0
    mild_leg = all(v>=0.8 for v in mild.values()); sev_leg = all(v>=0.8 for v in sev.values())
    rows.append({'genome':gn,'nominal':round(nom,4),'R_pert':round(sum(mild.values())/3,4),
        'R_shift':round(sum(sev.values())/5,4),'R_tiered':round(0.5*sum(mild.values())/3+0.5*sum(sev.values())/5,4),
        'mild_leg_pass':mild_leg,'severe_leg_pass':sev_leg,'battery_pass':mild_leg and sev_leg})
npass = sum(r['battery_pass'] for r in rows)
def hasM(r): g=r['genome']; return g['cofeed_glycerol'] and g['ko_pflB']
a = sum(1 for r in rows if r['battery_pass'] and hasM(r))
b = npass - a
c = sum(1 for r in rows if (not r['battery_pass']) and hasM(r))
d = 64 - npass - c
odds, p = fisher_exact([[a,b],[c,d]], alternative='greater')
out = {'amendment':'2026-09-27 10:04 IST 3B (locked pre-construction)','target':'3-hydroxypropionate',
 'route':'MCR1+MCR2 heterologous, transport + EX_3hp_e','pool':'6 host levers, 64 genomes, exhaustive',
 'nominal_max':max(nominal),'frontier_severe':{k:round(v,4) for k,v in frontier.items()},
 'n_pass':npass,'motif_M':'cofeed_glycerol AND ko_pflB',
 'fisher_table':{'pass_with_M':a,'pass_without_M':b,'fail_with_M':c,'fail_without_M':d},
 'fisher_one_tailed_p':float(p),'odds_ratio':float(odds) if odds==odds else None,
 'WIN_3B': bool(p<0.05 and npass>0),
 'falsification_rule':'p>=0.05 OR zero passers -> falsified, no loosening',
 'best_by_R_tiered':max(rows,key=lambda r:r['R_tiered']) if rows else None,
 'all_scored':rows}
json.dump(out, open('results/h_3hp_holdout.json','w'), indent=1)
print('nominal max', round(max(nominal),4), '| passers', npass, '/64 | table', [a,b,c,d], '| Fisher p', round(p,4), '| WIN_3B', out['WIN_3B'])
