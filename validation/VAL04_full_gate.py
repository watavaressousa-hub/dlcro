from pathlib import Path
import hashlib, json, csv, sys, re
from collections import defaultdict
import openpyxl
from rdflib import Graph, URIRef, Namespace
from rdflib.namespace import RDF, OWL, RDFS

sys.path.insert(0,'/mnt/data/vendor_pyshacl')
import pyshacl
from pyshacl import validate

BASE=Path('/mnt/data')
SH=Namespace('http://www.w3.org/ns/shacl#')
DLCRO='https://w3id.org/dlcro/'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def parse_ttl(p):
    g=Graph(); g.parse(p,format='turtle'); return g

shape_p=BASE/'dlcro_minimal_shapes.ttl'
valid_p=BASE/'demo_dlcro_v0.1.ttl'
invalid_p=BASE/'demo_invalid.ttl'

# Full pySHACL engine validation
full_results={}
for name,p in [('valid',valid_p),('invalid',invalid_p)]:
    conforms, rg, rt = validate(
        data_graph=str(p), shacl_graph=str(shape_p),
        data_graph_format='turtle', shacl_graph_format='turtle',
        inference='none', advanced=False, meta_shacl=False,
        abort_on_first=False, allow_infos=False, allow_warnings=False,
        do_owl_imports=False,
    )
    res=set(rg.subjects(RDF.type, SH.ValidationResult))
    outp=BASE/f'VAL04_pyshacl_{name}_report.ttl'
    rg.serialize(destination=str(outp),format='turtle')
    full_results[name]={
        'conforms':bool(conforms), 'validation_results':len(res),
        'report_triples':len(rg), 'report_sha256':sha(outp),
        'report_text':rt,
    }

# Schema regression
schema_names=['core.ttl','radiometry.ttl','context.ttl','metrology.ttl','lcu.ttl','radiometer.ttl','material.ttl','qi.ttl','alignment.ttl','dlcro.ttl']
schema=Graph(); per_file={}; import_edges=[]
for name in schema_names:
    p=BASE/name; g=parse_ttl(p); per_file[name]={'triples':len(g),'sha256':sha(p)}
    for t in g: schema.add(t)
    onts=list(g.subjects(RDF.type,OWL.Ontology))
    for o in onts:
        for imp in g.objects(o,OWL.imports): import_edges.append((str(o),str(imp)))
external_imports=[e for e in import_edges if not e[1].startswith(DLCRO)]
# graph cycle check among ontology imports
adj=defaultdict(set)
for a,b in import_edges:
    if b.startswith(DLCRO): adj[a].add(b)
visiting=set(); visited=set(); cycles=[]
def dfs(n,path):
    if n in visiting:
        cycles.append(path+[n]); return
    if n in visited:return
    visiting.add(n)
    for m in adj.get(n,()): dfs(m,path+[n])
    visiting.remove(n); visited.add(n)
for n in list(adj): dfs(n,[])
strong={
 'owl_restrictions': len(set(schema.subjects(RDF.type,OWL.Restriction))),
 'owl_equivalentClass': len(list(schema.triples((None,OWL.equivalentClass,None)))),
 'owl_equivalentProperty': len(list(schema.triples((None,OWL.equivalentProperty,None)))),
 'owl_disjointWith': len(list(schema.triples((None,OWL.disjointWith,None)))),
 'owl_propertyChainAxiom': len(list(schema.triples((None,OWL.propertyChainAxiom,None)))),
 'owl_oneOf': len(list(schema.triples((None,OWL.oneOf,None)))),
 'owl_sameAs': len(list(schema.triples((None,OWL.sameAs,None)))),
}

# SPARQL Must CQ regression
xlsx=BASE/'Backlog DLCRO - Scrumban.xlsx'
wb=openpyxl.load_workbook(xlsx,read_only=True,data_only=False)
ws=wb['SPARQL_CQ_Suite']
demo=parse_ttl(valid_p)
cq=[]
for row in ws.iter_rows(min_row=2,values_only=True):
    if not row or not row[0]: continue
    cqid,priority,qtype,expected_vars,query=row[:5]
    if priority!='Must': continue
    try:
        rr=demo.query(query)
        rows=list(rr)
        cq.append({'cq':cqid,'compiled':True,'rows':len(rows),'nonempty':len(rows)>0,'error':None})
    except Exception as e:
        cq.append({'cq':cqid,'compiled':False,'rows':0,'nonempty':False,'error':repr(e)})

# Pull09 hash match for controlled fixtures
mtext=(BASE/'PULL09_manifest.json').read_text(encoding='utf-8-sig')
m9=json.loads(mtext)
fixture_hashes={x:sha(BASE/x) for x in ['dlcro_minimal_shapes.ttl','demo_dlcro_v0.1.ttl','demo_invalid.ttl']}
hash_match={k:(fixture_hashes[k]==m9['hashes_sha256_drive_readback'][k]) for k in fixture_hashes}

report={
 'gate':'VAL-04','date':'2026-09-26','engine':{'name':'pySHACL','version':pyshacl.__version__,'rdflib':__import__('rdflib').__version__,'inference':'none','advanced':False},
 'full_shacl':full_results,
 'fixtures':{'hashes_sha256':fixture_hashes,'matches_pull09_manifest':hash_match,'valid_triples':len(demo),'invalid_triples':len(parse_ttl(invalid_p)),'shapes_triples':len(parse_ttl(shape_p))},
 'schema':{'merged_triples':len(schema),'per_file':per_file,'import_edges':import_edges,'external_imports':external_imports,'import_cycles':cycles,'strong_axioms':strong},
 'sparql':{'must_total':len(cq),'compiled':sum(x['compiled'] for x in cq),'nonempty':sum(x['nonempty'] for x in cq),'details':cq},
}
report['pass']=(
 full_results['valid']['conforms'] is True and full_results['valid']['validation_results']==0 and
 full_results['invalid']['conforms'] is False and full_results['invalid']['validation_results']>0 and
 all(hash_match.values()) and not external_imports and not cycles and
 len(cq)==15 and all(x['compiled'] and x['nonempty'] for x in cq) and
 all(v==0 for v in strong.values())
)
json_p=BASE/'VAL04_full_engine_report.json'; json_p.write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
# csv
with (BASE/'VAL04_sparql_regression.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=['cq','compiled','rows','nonempty','error']); w.writeheader(); w.writerows(cq)
# markdown concise
lines=[
'# VAL-04 — Full-engine SHACL confirmation and regression bundle','',
f"- Engine: pySHACL {pyshacl.__version__} / RDFLib {report['engine']['rdflib']}",
'- Inference: none; advanced: false; external OWL imports: disabled',
f"- Valid fixture: conforms={full_results['valid']['conforms']}; results={full_results['valid']['validation_results']}",
f"- Invalid fixture: conforms={full_results['invalid']['conforms']}; results={full_results['invalid']['validation_results']}",
f"- Pull 09 controlled hashes preserved: {all(hash_match.values())}",
f"- Schema Turtle files: {len(schema_names)}; merged triples={len(schema)}; external imports={len(external_imports)}; import cycles={len(cycles)}",
f"- Strong OWL constructs monitored: {strong}",
f"- Must CQs: {len(cq)}/15 compiled; {sum(x['nonempty'] for x in cq)}/15 non-empty",
f"- Gate PASS: {report['pass']}", '', '## SPARQL regression',''
]
for x in cq: lines.append(f"- {x['cq']}: rows={x['rows']}; compiled={x['compiled']}; nonempty={x['nonempty']}")
lines += ['', '## Controlled hashes','']
for k,v in fixture_hashes.items(): lines.append(f'- `{k}`: `{v}`; matches Pull 09={hash_match[k]}')
md_p=BASE/'VAL04_full_engine_report.md'; md_p.write_text('\n'.join(lines)+'\n',encoding='utf-8')
# manifest hashes
artifacts=['VAL04_pyshacl_valid_report.ttl','VAL04_pyshacl_invalid_report.ttl','VAL04_full_engine_report.json','VAL04_full_engine_report.md','VAL04_sparql_regression.csv','val04_full_gate.py']
manifest={'artifacts':{a:sha(BASE/a) for a in artifacts},'engine':report['engine'],'gate_pass':report['pass']}
(BASE/'VAL04_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps({
 'pass':report['pass'], 'engine':report['engine'],
 'valid':full_results['valid']|{'report_text':'[omitted]'},
 'invalid':full_results['invalid']|{'report_text':'[omitted]'},
 'hash_match':hash_match,'schema_triples':len(schema),'imports':len(import_edges),'external_imports':external_imports,'cycles':cycles,'strong':strong,
 'cq_total':len(cq),'cq_nonempty':sum(x['nonempty'] for x in cq),'cq_rows':[(x['cq'],x['rows']) for x in cq],
 'manifest':manifest
},indent=2))
