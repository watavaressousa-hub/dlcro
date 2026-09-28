# Pull 12 — DLCRO v0.1.0 stable-candidate full regression

- Gate PASS: **True**
- Engine: pySHACL 0.40.1 / RDFLib 7.5.0
- Full SHACL: valid=True / 0 results; invalid=False / 17 results
- Turtle: 10/10; merged triples=382
- Imports: internal=33; external=0; missing=0; cycles=0
- Strong OWL monitored: {'owl:Restriction': 0, 'owl:equivalentClass': 0, 'owl:equivalentProperty': 0, 'owl:disjointWith': 0, 'owl:propertyChainAxiom': 0, 'owl:oneOf': 0, 'owl:sameAs': 0}
- Profile: local entities=119; punning=0; logical blank nodes=0; unlabeled=0
- Reasoning: class universe=65; asserted subclasses=9; non-reflexive closure=9; cycles=0
- SPARQL: 15/15 compiled; 15/15 non-empty; frozen row counts=True
- RDF release diff: removed=21, added=21, unexpected semantic diffs=0
- semantic_change = `false`

## Checks

- pyshacl_version: PASS
- rdflib_version: PASS
- valid_shacl: PASS
- invalid_shacl: PASS
- turtle_10: PASS
- merged_382: PASS
- internal_import_edges_33: PASS
- external_imports_zero: PASS
- missing_internal_imports_zero: PASS
- import_cycles_zero: PASS
- stable_version_iris: PASS
- version_info_0_1_0: PASS
- strong_owl_zero: PASS
- local_entities_119: PASS
- punning_zero: PASS
- logical_blank_nodes_zero: PASS
- unlabeled_zero: PASS
- reasoning_class_universe_65: PASS
- asserted_subclasses_9: PASS
- closure_9: PASS
- subclass_cycles_zero: PASS
- nothing_conflicts_zero: PASS
- disjoint_conflicts_zero: PASS
- same_diff_conflicts_zero: PASS
- sparql_15: PASS
- sparql_all_compiled: PASS
- sparql_all_nonempty: PASS
- sparql_row_counts_frozen: PASS
- cq20_end_to_end: PASS
- semantic_change_false: PASS

## SPARQL rows

- CQ-01: rows=1 expected=1 — PASS
- CQ-02: rows=1 expected=1 — PASS
- CQ-03: rows=1 expected=1 — PASS
- CQ-04: rows=5 expected=5 — PASS
- CQ-05: rows=4 expected=4 — PASS
- CQ-06: rows=1 expected=1 — PASS
- CQ-08: rows=1 expected=1 — PASS
- CQ-09: rows=1 expected=1 — PASS
- CQ-10: rows=2 expected=2 — PASS
- CQ-11: rows=2 expected=2 — PASS
- CQ-12: rows=1 expected=1 — PASS
- CQ-13: rows=3 expected=3 — PASS
- CQ-14: rows=1 expected=1 — PASS
- CQ-18: rows=4 expected=4 — PASS
- CQ-20: rows=1 expected=1 — PASS
