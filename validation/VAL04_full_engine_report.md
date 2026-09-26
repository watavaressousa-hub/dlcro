# VAL-04 — Full-engine SHACL confirmation and regression bundle

- Engine: pySHACL 0.40.1 / RDFLib 7.5.0
- Inference: none; advanced: false; external OWL imports: disabled
- Valid fixture: conforms=True; results=0
- Invalid fixture: conforms=False; results=17
- Pull 09 controlled hashes preserved: True
- Schema Turtle files: 10; merged triples=382; external imports=0; import cycles=0
- Strong OWL constructs monitored: {'owl_restrictions': 0, 'owl_equivalentClass': 0, 'owl_equivalentProperty': 0, 'owl_disjointWith': 0, 'owl_propertyChainAxiom': 0, 'owl_oneOf': 0, 'owl_sameAs': 0}
- Must CQs: 15/15 compiled; 15/15 non-empty
- Gate PASS: True

## SPARQL regression

- CQ-01: rows=1; compiled=True; nonempty=True
- CQ-02: rows=1; compiled=True; nonempty=True
- CQ-03: rows=1; compiled=True; nonempty=True
- CQ-04: rows=5; compiled=True; nonempty=True
- CQ-05: rows=4; compiled=True; nonempty=True
- CQ-06: rows=1; compiled=True; nonempty=True
- CQ-08: rows=1; compiled=True; nonempty=True
- CQ-09: rows=1; compiled=True; nonempty=True
- CQ-10: rows=2; compiled=True; nonempty=True
- CQ-11: rows=2; compiled=True; nonempty=True
- CQ-12: rows=1; compiled=True; nonempty=True
- CQ-13: rows=3; compiled=True; nonempty=True
- CQ-14: rows=1; compiled=True; nonempty=True
- CQ-18: rows=4; compiled=True; nonempty=True
- CQ-20: rows=1; compiled=True; nonempty=True

## Controlled hashes

- `dlcro_minimal_shapes.ttl`: `4ccbe58bda5793bb6850071bbe2e0ccc477a509502dc496b29ed0333dcf363fb`; matches Pull 09=True
- `demo_dlcro_v0.1.ttl`: `75936925706658aa70e6a2250ac466cdfb4de3635d16bce675df6417fd7cb5c8`; matches Pull 09=True
- `demo_invalid.ttl`: `fae94fd82a327d2ac0cde39bc3fb10821b403b07c5d0b42f61511944680bf323`; matches Pull 09=True
