#!/usr/bin/env python3
"""W11 benchmark_flux.py - locked benchmark numbers (Amendment A1).

For each locked target pathway (data/benchmarks.json, reaction lists LOCKED
2026-09-26 before any search run): implement the cited engineered pathway in
iML1515, apply the locked base condition (GLC_AEROBIC: EX_glc__D_e -10,
EX_o2_e -1000), and compute the benchmark metric:
  product flux (mmol/gDW/h) at the pFBA-optimal growth-constrained solution.
Operationalization (fixed HERE, before any evolved architecture is evaluated):
  1. FBA max growth; biomass lower bound fixed at that max (growth-constrained).
  2. Maximize product boundary flux (FBA) -> max growth-coupled production.
  3. pFBA tie-break (fraction_of_optimum 0.999) -> parsimonious fluxes;
     reported product flux is the pFBA solution's product flux.
No evolved design exists yet, so this cannot be tuned post-hoc.
"""
import cobra, json, datetime
from cobra import Metabolite, Reaction

MODEL = 'data/models/iML1515.xml.gz'
BASE = {'EX_glc__D_e': -10.0, 'EX_o2_e': -1000.0}

def met(m, mid, name, formula=None):
    try:
        return m.metabolites.get_by_id(mid)
    except KeyError:
        x = Metabolite(mid, name=name, compartment='c')
        m.add_metabolites([x]); return x

def rxn(m, rid, name, stoich, lb=0.0, ub=1000.0):
    r = Reaction(rid); r.name = name; r.lower_bound = lb; r.upper_bound = ub
    r.add_metabolites(stoich); m.add_reactions([r]); return r

def add_exchange(m, cid, eid, name, secreted=True):
    e = Metabolite(eid, name=name + ' (extracellular)', compartment='e')
    m.add_metabolites([e])
    rxn(m, 'T_' + eid, name + ' transport', {m.metabolites.get_by_id(cid): -1, e: 1},
        lb=-1000.0, ub=1000.0)
    ex = rxn(m, 'EX_' + eid, 'Exchange ' + name, {e: -1}, lb=0.0, ub=1000.0)
    return ex

def build_14BDO(m):
    hb   = met(m, '4hb_c',   '4-hydroxybutyrate')
    hbcoa= met(m, '4hbcoa_c','4-hydroxybutyryl-CoA')
    hbal = met(m, '4hbal_c', '4-hydroxybutyraldehyde')
    bdo  = met(m, '14bdo_c', '1,4-butanediol')
    g=lambda i:m.metabolites.get_by_id(i)
    rxn(m,'BDO1','alpha-ketoglutarate decarboxylase (kgd)',{g('akg_c'):-1,g('h_c'):-1,g('sucsal_c'):1,g('co2_c'):1})
    rxn(m,'BDO2','4-hydroxybutyrate dehydrogenase (4hbD)',{g('sucsal_c'):-1,g('nadh_c'):-1,g('h_c'):-1,hb:1,g('nad_c'):1})
    rxn(m,'BDO3','CoA transferase (cat2)',{hb:-1,g('accoa_c'):-1,hbcoa:1,g('ac_c'):1})
    rxn(m,'BDO4','CoA-acylating aldehyde dehydrogenase',{hbcoa:-1,g('nadh_c'):-1,g('h_c'):-1,hbal:1,g('coa_c'):1,g('nad_c'):1})
    rxn(m,'BDO5','alcohol dehydrogenase (adhE2)',{hbal:-1,g('nadh_c'):-1,g('h_c'):-1,bdo:1,g('nad_c'):1})
    return add_exchange(m,'14bdo_c','14bdo_e','1,4-butanediol').id

def build_ISOBUTANOL(m):
    ibyr = met(m,'ibutyr_c','isobutyraldehyde')
    ibut = met(m,'ibut_c','isobutanol')
    g=lambda i:m.metabolites.get_by_id(i)
    # heterologous alsS (same chemistry as native ACLS, locked per Atsumi 2008)
    rxn(m,'ALSS','acetolactate synthase (alsS, B. subtilis)',{g('pyr_c'):-2,g('h_c'):-1,g('alac__S_c'):1,g('co2_c'):1})
    rxn(m,'KIVD','ketoisovalerate decarboxylase (kivd)',{g('3mob_c'):-1,g('h_c'):-1,ibyr:1,g('co2_c'):1})
    rxn(m,'IBUTDH','isobutanol dehydrogenase (adhA)',{ibyr:-1,g('nadh_c'):-1,g('h_c'):-1,ibut:1,g('nad_c'):1})
    return add_exchange(m,'ibut_c','ibut_e','isobutanol').id

def build_LYCOPENE(m):
    ggdp = met(m,'ggdp_c','geranylgeranyl diphosphate')
    phyto= met(m,'phyto_c','phytoene')
    lyco = met(m,'lyco_c','lycopene')
    g=lambda i:m.metabolites.get_by_id(i)
    rxn(m,'CRTE','GGPP synthase (crtE)',{g('frdp_c'):-1,g('ipdp_c'):-1,ggdp:1,g('ppi_c'):1})
    rxn(m,'CRTB','phytoene synthase (crtB)',{ggdp:-2,phyto:1,g('ppi_c'):2})
    rxn(m,'CRTI','phytoene desaturase (crtI)',{phyto:-1,g('nad_c'):-4,lyco:1,g('nadh_c'):4,g('h_c'):4})
    # intracellular product: demand sink, not secretion
    dm = rxn(m,'DM_lyco_c','lycopene accumulation sink',{lyco:-1},lb=0.0,ub=1000.0)
    return dm.id

BUILDERS = {'14BDO': build_14BDO, 'ISOBUTANOL': build_ISOBUTANOL, 'LYCOPENE': build_LYCOPENE}

if __name__ == '__main__':
    out = {'locked_metric': 'production envelope: product flux (mmol/gDW/h) at pFBA-optimal growth-constrained solutions',
           'operationalization': ('growth fixed at locked fractions [1.0, 0.9, 0.75, 0.5, 0.25, 0.0] of FBA max; product maximized at each; '
                                  'pFBA tie-break (0.999). At 100% max growth all three pathways carry zero flux '
                                  '(verified 2026-09-26): production competes with biomass, so the envelope is the comparator.'),
           'growth_fractions': [1.0, 0.9, 0.75, 0.5, 0.25, 0.0],
           'base_condition': BASE, 'model': MODEL, 'cobra': cobra.__version__,
           'run_at': datetime.datetime.now().isoformat(timespec='seconds'), 'targets': {}}
    FRACS = [1.0, 0.9, 0.75, 0.5, 0.25, 0.0]
    for tid, build in BUILDERS.items():
        m = cobra.io.read_sbml_model(MODEL)
        for ex, b in BASE.items(): m.reactions.get_by_id(ex).lower_bound = b
        prod = build(m)
        bio = m.reactions.get_by_id('BIOMASS_Ec_iML1515_core_75p37M')
        gmax = m.slim_optimize()
        env = {}
        for frac in FRACS:
            with m:
                bio.lower_bound = frac * gmax
                m.objective = m.reactions.get_by_id(prod)
                pmax = m.slim_optimize()
                m.reactions.get_by_id(prod).lower_bound = 0.999 * pmax
                sol = cobra.flux_analysis.pfba(m)
                env[str(frac)] = {'max_product_flux': round(float(pmax), 6),
                                  'product_flux_pfba': round(float(sol.fluxes[prod]), 6),
                                  'status': sol.status}
        out['targets'][tid] = {'product_boundary': prod, 'max_growth_per_h': round(float(gmax), 6), 'envelope': env}
        print(tid, out['targets'][tid])
    with open('results/benchmark_flux.json', 'w') as f: json.dump(out, f, indent=1)
    print('written results/benchmark_flux.json')

