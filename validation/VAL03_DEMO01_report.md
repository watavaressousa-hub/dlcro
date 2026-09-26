# VAL-03 + DEMO-01 — Drive-readback validation report


Date: 2026-09-26
Ontology: DLCRO v0.1-dev
Pull: 09


## Scope
No OWL cardinalities, owl:Restriction, disjointness axioms, property chains,
nominals, owl:equivalentClass, or owl:equivalentProperty were introduced.


The demonstrative graph is a synthetic semantic-validation fixture. Numeric
values are sentinel values only and are not measurements or performance,
clinical, calibration, conformity, or fitness-for-purpose claims.


## SHACL profile
The frozen minimal profile uses only:
- sh:targetClass
- sh:minCount
- sh:class
- sh:datatype


Shapes cover ExposureEvent, LightCuringUnit, MeasurementActivity,
DentalRadiometer, MeasurementResult, QUDT QuantityValue, UncertaintyBudget,
ExpandedUncertainty, TraceabilityStatement and EvidenceBundle.


## Engine note
RDFLib was available. pySHACL/Jena SHACL were not available and external
package installation was disabled. VAL03_validator.py therefore validates the
exact SHACL Core subset above. This is not presented as a general SHACL engine.
A full-engine confirmation is required before the public stable release.


## Drive-readback results
- demo_dlcro_v0.1.ttl: 172 triples; 0 violations — PASS.
- demo_invalid.ttl: 14 triples; 17 deliberate violations — PASS.
- 15/15 Must SPARQL queries executed and returned >=1 row — PASS.
- CQ-20 reconstructs the full EvidenceBundle → ExposureEvent → LCU →
  MeasurementActivity/DentalRadiometer → MeasurementResult → Target chain.


## SPARQL row counts
CQ-01 1; CQ-02 1; CQ-03 1; CQ-04 5; CQ-05 4; CQ-06 1; CQ-08 1;
CQ-09 1; CQ-10 2; CQ-11 2; CQ-12 1; CQ-13 3; CQ-14 1; CQ-18 4; CQ-20 1.


## SHA-256 calculated from raw Drive-readback bytes
- dlcro_minimal_shapes.ttl:
  4ccbe58bda5793bb6850071bbe2e0ccc477a509502dc496b29ed0333dcf363fb
- VAL03_validator.py:
  efbdbf4b0141e6e2fc10726a1b5c849a3656044b2e4ee2e60252c5b8627349ad
- demo_dlcro_v0.1.ttl:
  75936925706658aa70e6a2250ac466cdfb4de3635d16bce675df6417fd7cb5c8
- demo_invalid.ttl:
  fae94fd82a327d2ac0cde39bc3fb10821b403b07c5d0b42f61511944680bf323
- DEMO01_sparql_results.csv:
  97dd30608ad09d59ca5a5184538de409891c8ca9215313421cbf5bc2d90d476a


## Result
VAL-03 PASS for the frozen minimal profile.
DEMO-01 PASS for end-to-end semantic/query demonstration.
Full-engine SHACL confirmation remains a pre-release validation gate.