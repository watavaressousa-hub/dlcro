# Changelog

## [0.1.0] — 2026-09-26

First stable-release candidate of the Dental Light-Curing and Radiometry Ontology (DLCRO).

- Nine semantic modules plus default aggregator.
- Stable version IRI family `https://w3id.org/dlcro/0.1.0`.
- Selective chemical and clinical mappings retained without external OWL imports.
- Frozen radiometric/metrological distinctions and claim ceiling preserved.
- 15 Must Competency Questions materialized as individual `.rq` files.
- No cardinalities, `owl:Restriction`, strong equivalences, disjointness, property chains, nominals, or `owl:sameAs`.
- W3ID activation remains a release gate.
- Known limitation: no automatic clinical cure, equipment-performance, conformity, calibration-validity, or fitness-for-purpose claim.

## [0.1-RC1] — 2026-09-26

- Frozen release-candidate baseline.
- 10 Turtle files / 382 merged triples.
- VAL-04 pySHACL 0.40.1 / RDFLib 7.5.0 PASS.
- 15/15 Must CQs non-empty on the controlled demo graph.
