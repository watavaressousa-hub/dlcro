from pathlib import Path
import csv, hashlib, json, os, sys
from collections import defaultdict, deque
from datetime import date

from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, OWL

VENDOR=Path('/mnt/data/vendor_pyshacl')
sys.path.insert(0,str(VENDOR))
import pyshacl
from pyshacl import validate
import rdflib

ROOT=Path('/mnt/data/DLCRO_v0.1.0_STABLE_CANDIDATE_LOCAL')
BASELINE=Path('/mnt/data/dlcro_stable_work')
ONTO=ROOT/'ontology'; VAL=ROOT/'validation'; EX=ROOT/'examples'; Q=ROOT/'queries'; RM=ROOT/'release-metadata'
SH=Namespace('http://www.w3.org/ns/shacl#')
DLCRO='https://w3id.org/dlcro/'
SCHEMA_NAMES=['core.ttl','radiometry.ttl','context.ttl','metrology.ttl','lcu.ttl','radiometer.ttl','material.ttl','qi.ttl','alignment.ttl','dlcro.ttl']
EXPECTED_ROWS={'CQ-01':1,'CQ-02':1,'CQ-03':1,'CQ-04':5,'CQ-05':4,'CQ-06':1,'CQ-08':1,'CQ-09':1,'CQ-10':2,'CQ-11':2,'CQ-12':1,'CQ-13':3,'CQ-14':1,'CQ-18':4,'CQ-20':1}
EXPECTED_VERSION_IRIS={
 'core.ttl':'https://w3id.org/dlcro/0.1.0/core','radiometry.ttl':'https://w3id.org/dlcro/0.1.0/radiometry',
 'context.ttl':'https://w3id.org/dlcro/0.1.0/context','metrology.ttl':'https://w3id.org/dlcro/0.1.0/metrology',
 'lcu.ttl':'https://w3id.org/dlcro/0.1.0/lcu','radiometer.ttl':'https://w3id.org/dlcro/0.1.0/radiometer',
 'material.ttl':'https://w3id.org/dlcro/0.1.0/material','qi.ttl':'https://w3id.org/dlcro/0.1.0/qi',
 'alignment.ttl':'https://w3id.org/dlcro/0.1.0/alignment','dlcro.ttl':'https://w3id.org/dlcro/0.1.0'}

def sha256(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def parse(p):
    g=Graph(); g.parse(str(p),format='turtle'); return g

# Engine provenance
engine={'pyshacl':pyshacl.__version__,'rdflib':rdflib.__version__,'pyshacl_source_commit':'469cca7a22a078b36c167c1e8dadecf5e5ec6c75','pyshacl_vendor_module_count':51}

# Full SHACL
shapes=VAL/'dlcro_minimal_shapes.ttl'
full={}
for key,p in [('valid',EX/'demo_dlcro_v0.1.ttl'),('invalid',EX/'demo_invalid.ttl')]:
    conforms,rg,rt=validate(data_graph=str(p),shacl_graph=str(shapes),data_graph_format='turtle',shacl_graph_format='turtle',
        inference='none',advanced=False,meta_shacl=False,abort_on_first=False,allow_infos=False,allow_warnings=False,do_owl_imports=False)
    results=set(rg.subjects(RDF.type,SH.ValidationResult))
    op=VAL/f'PULL12_pyshacl_{key}_report.ttl'
    rg.serialize(destination=str(op),format='turtle')
    full[key]={'conforms':bool(conforms),'validation_results':len(results),'report_triples':len(rg),'report_sha256':sha256(op),'report_text':rt}

# Parse/import/profile/version
merged=Graph(); per_file={}; import_edges=[]; all_onts=set(); stable_version_ok=True; version_info_ok=True
for name in SCHEMA_NAMES:
    g=parse(ONTO/name)
    for t in g: merged.add(t)
    onts=list(g.subjects(RDF.type,OWL.Ontology)); vers=[]
    for o in onts:
        all_onts.add(str(o)); vers += [str(v) for v in g.objects(o,OWL.versionIRI)]
        for imp in g.objects(o,OWL.imports): import_edges.append((str(o),str(imp)))
    vinfos=[str(v) for o in onts for v in g.objects(o,OWL.versionInfo)]
    expected=EXPECTED_VERSION_IRIS[name]
    this_v_ok=(len(onts)==1 and vers==[expected]); this_info_ok=(vinfos==['0.1.0'])
    stable_version_ok &= this_v_ok; version_info_ok &= this_info_ok
    per_file[name]={'triples':len(g),'sha256':sha256(ONTO/name),'ontology_count':len(onts),'version_iris':vers,'version_info':vinfos,'version_ok':this_v_ok,'version_info_ok':this_info_ok}
internal=[e for e in import_edges if e[1].startswith(DLCRO)]; external=[e for e in import_edges if not e[1].startswith(DLCRO)]
missing=[e for e in internal if e[1] not in all_onts]
adj=defaultdict(set)
for a,b in internal: adj[a].add(b)
visiting=set(); visited=set(); cycles=[]
def dfs(n,path):
    if n in visiting: cycles.append(path+[n]); return
    if n in visited: return
    visiting.add(n)
    for m in adj.get(n,()): dfs(m,path+[n])
    visiting.remove(n); visited.add(n)
for n in list(adj): dfs(n,[])

strong={
 'owl:Restriction':len(set(merged.subjects(RDF.type,OWL.Restriction))),
 'owl:equivalentClass':len(list(merged.triples((None,OWL.equivalentClass,None)))),
 'owl:equivalentProperty':len(list(merged.triples((None,OWL.equivalentProperty,None)))),
 'owl:disjointWith':len(list(merged.triples((None,OWL.disjointWith,None)))),
 'owl:propertyChainAxiom':len(list(merged.triples((None,OWL.propertyChainAxiom,None)))),
 'owl:oneOf':len(list(merged.triples((None,OWL.oneOf,None)))),
 'owl:sameAs':len(list(merged.triples((None,OWL.sameAs,None))),)
}
# local declarations / profile
local_prefix='https://w3id.org/dlcro/'
decl_types=[OWL.Class,OWL.ObjectProperty,OWL.DatatypeProperty,OWL.AnnotationProperty,OWL.NamedIndividual]
roles=defaultdict(set)
for typ in decl_types:
    for s in merged.subjects(RDF.type,typ):
        if str(s).startswith(local_prefix): roles[s].add(typ)
punning=sum(1 for x in roles.values() if len(x)>1)
local_entities=set(roles)
unlabeled=sum(1 for s in local_entities if not list(merged.objects(s,RDFS.label)))
logical_blank_nodes=sum(1 for s,p,o in merged if (getattr(s,'__class__',None).__name__=='BNode' or getattr(o,'__class__',None).__name__=='BNode'))

# Conservative named-class reasoning, matching VAL-01 scope
sub_edges=[(s,o) for s,o in merged.subject_objects(RDFS.subClassOf) if isinstance(s,URIRef) and isinstance(o,URIRef)]
class_universe=set(merged.subjects(RDF.type,OWL.Class)) | {x for e in sub_edges for x in e}
sub_adj=defaultdict(set)
for a,b in sub_edges: sub_adj[a].add(b)
closure=set(); sub_cycles=[]
for a in class_universe:
    stack=[(a,[a])]; seen=set()
    while stack:
        x,path=stack.pop()
        for y in sub_adj.get(x,()):
            if y==a: sub_cycles.append(path+[y])
            if y not in seen:
                seen.add(y); closure.add((a,y)); stack.append((y,path+[y]))
closure_nonref={(a,b) for a,b in closure if a!=b}
nothing_conflicts=[str(a) for a,b in closure_nonref if b==OWL.Nothing]
disjoint_pairs={(a,b) for a,b in merged.subject_objects(OWL.disjointWith)}
disjoint_conflicts=[]
for c in class_universe:
    sups={b for a,b in closure_nonref if a==c}|{c}
    for a,b in disjoint_pairs:
        if a in sups and b in sups: disjoint_conflicts.append((str(c),str(a),str(b)))
same_diff=[]
DIFF=URIRef('http://www.w3.org/2002/07/owl#differentFrom')
for a,b in merged.subject_objects(OWL.sameAs):
    if (a,DIFF,b) in merged or (b,DIFF,a) in merged: same_diff.append((str(a),str(b)))

# SPARQL frozen suite
kg=parse(EX/'demo_dlcro_v0.1.ttl')
rows=[]
for qfile in sorted(Q.glob('CQ-*.rq')):
    cq=qfile.stem
    try:
        rr=list(kg.query(qfile.read_text(encoding='utf-8-sig')))
        rec={'cq':cq,'compiled':True,'rows':len(rr),'nonempty':len(rr)>0,'expected_rows':EXPECTED_ROWS[cq],'row_count_match':len(rr)==EXPECTED_ROWS[cq],'error':None}
    except Exception as e:
        rec={'cq':cq,'compiled':False,'rows':0,'nonempty':False,'expected_rows':EXPECTED_ROWS.get(cq),'row_count_match':False,'error':repr(e)}
    rows.append(rec)

# RDF semantic diff vs frozen RC1. Only specified release metadata predicates may differ.
base=Graph()
for name in SCHEMA_NAMES:
    for t in parse(BASELINE/'ontology'/name): base.add(t)
removed=set(base)-set(merged); added=set(merged)-set(base)
DCT_DESCRIPTION=URIRef('http://purl.org/dc/terms/description')
allowed_preds={OWL.versionIRI,OWL.versionInfo,DCT_DESCRIPTION}
unexpected_removed=[tuple(map(str,t)) for t in removed if t[1] not in allowed_preds]
unexpected_added=[tuple(map(str,t)) for t in added if t[1] not in allowed_preds]
semantic_change=bool(unexpected_removed or unexpected_added)

checks={
 'pyshacl_version':engine['pyshacl']=='0.40.1','rdflib_version':engine['rdflib']=='7.5.0',
 'valid_shacl':full['valid']['conforms'] is True and full['valid']['validation_results']==0,
 'invalid_shacl':full['invalid']['conforms'] is False and full['invalid']['validation_results']==17,
 'turtle_10':len(per_file)==10,'merged_382':len(merged)==382,'internal_import_edges_33':len(internal)==33,
 'external_imports_zero':len(external)==0,'missing_internal_imports_zero':len(missing)==0,'import_cycles_zero':len(cycles)==0,
 'stable_version_iris':stable_version_ok,'version_info_0_1_0':version_info_ok,'strong_owl_zero':all(v==0 for v in strong.values()),
 'local_entities_119':len(local_entities)==119,'punning_zero':punning==0,'logical_blank_nodes_zero':logical_blank_nodes==0,'unlabeled_zero':unlabeled==0,
 'reasoning_class_universe_65':len(class_universe)==65,'asserted_subclasses_9':len(sub_edges)==9,'closure_9':len(closure_nonref)==9,
 'subclass_cycles_zero':len(sub_cycles)==0,'nothing_conflicts_zero':len(nothing_conflicts)==0,'disjoint_conflicts_zero':len(disjoint_conflicts)==0,'same_diff_conflicts_zero':len(same_diff)==0,
 'sparql_15':len(rows)==15,'sparql_all_compiled':all(x['compiled'] for x in rows),'sparql_all_nonempty':all(x['nonempty'] for x in rows),'sparql_row_counts_frozen':all(x['row_count_match'] for x in rows),
 'cq20_end_to_end':next(x for x in rows if x['cq']=='CQ-20')['rows']==1,
 'semantic_change_false':semantic_change is False
}
passed=all(checks.values())
report={
 'gate':'PULL12_STABLE_CANDIDATE_FULL_REGRESSION','date':'2026-09-26','candidate_version':'0.1.0','semantic_change':semantic_change,'pass':passed,
 'engine':engine,'checks':checks,'shacl':full,'schema':{'files':per_file,'merged_triples':len(merged),'import_edges':import_edges,'internal_import_edges':len(internal),'external_imports':external,'missing_internal_imports':missing,'cycles':cycles,'strong_owl':strong,'local_entities':len(local_entities),'punning':punning,'logical_blank_nodes':logical_blank_nodes,'unlabeled':unlabeled},
 'reasoning':{'class_universe':len(class_universe),'asserted_subclasses':len(sub_edges),'nonreflexive_closure':len(closure_nonref),'cycles':sub_cycles,'owl_nothing_conflicts':nothing_conflicts,'disjointness_conflicts':disjoint_conflicts,'sameAs_differentFrom_conflicts':same_diff},
 'sparql':{'total':len(rows),'compiled':sum(x['compiled'] for x in rows),'nonempty':sum(x['nonempty'] for x in rows),'rows':rows},
 'rdf_diff':{'removed_triples':len(removed),'added_triples':len(added),'allowed_predicates':[str(x) for x in allowed_preds],'unexpected_removed':unexpected_removed,'unexpected_added':unexpected_added}
}
json_path=VAL/'PULL12_full_regression_report.json'; json_path.write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
with (VAL/'PULL12_sparql_regression.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=['cq','compiled','rows','nonempty','expected_rows','row_count_match','error']); w.writeheader(); w.writerows(rows)
md=[
 '# Pull 12 — DLCRO v0.1.0 stable-candidate full regression','',
 f"- Gate PASS: **{passed}**",f"- Engine: pySHACL {engine['pyshacl']} / RDFLib {engine['rdflib']}",
 f"- Full SHACL: valid={full['valid']['conforms']} / {full['valid']['validation_results']} results; invalid={full['invalid']['conforms']} / {full['invalid']['validation_results']} results",
 f"- Turtle: 10/10; merged triples={len(merged)}",f"- Imports: internal={len(internal)}; external={len(external)}; missing={len(missing)}; cycles={len(cycles)}",
 f"- Strong OWL monitored: {strong}",f"- Profile: local entities={len(local_entities)}; punning={punning}; logical blank nodes={logical_blank_nodes}; unlabeled={unlabeled}",
 f"- Reasoning: class universe={len(class_universe)}; asserted subclasses={len(sub_edges)}; non-reflexive closure={len(closure_nonref)}; cycles={len(sub_cycles)}",
 f"- SPARQL: {sum(x['compiled'] for x in rows)}/15 compiled; {sum(x['nonempty'] for x in rows)}/15 non-empty; frozen row counts={all(x['row_count_match'] for x in rows)}",
 f"- RDF release diff: removed={len(removed)}, added={len(added)}, unexpected semantic diffs={len(unexpected_removed)+len(unexpected_added)}",
 f"- semantic_change = `{str(semantic_change).lower()}`",'', '## Checks',''
]
for k,v in checks.items(): md.append(f"- {k}: {'PASS' if v else 'FAIL'}")
md += ['', '## SPARQL rows','']
for x in rows: md.append(f"- {x['cq']}: rows={x['rows']} expected={x['expected_rows']} — {'PASS' if x['row_count_match'] else 'FAIL'}")
(VAL/'PULL12_full_regression_report.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
# Evidence manifest
arts=['PULL12_pyshacl_valid_report.ttl','PULL12_pyshacl_invalid_report.ttl','PULL12_full_regression_report.json','PULL12_full_regression_report.md','PULL12_sparql_regression.csv','PULL12_full_regression_gate.py']
manifest={'gate':'PULL12_STABLE_CANDIDATE_FULL_REGRESSION','pass':passed,'engine':engine,'artifacts':{a:sha256(VAL/a) for a in arts}}
(VAL/'PULL12_validation_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps({'pass':passed,'engine':engine,'checks':checks,'shacl':{k:{'conforms':v['conforms'],'validation_results':v['validation_results']} for k,v in full.items()},'rdf_diff':report['rdf_diff'],'validation_manifest':manifest},indent=2,ensure_ascii=False))
