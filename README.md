# DLCRO v0.1 — Dental Light-Curing and Radiometry Ontology

DLCRO is a modular OWL 2 ontology for dental light-curing units, dental radiometers, radiometric and metrological evidence, exposure/measurement context, material and photoinitiator information, Quality Infrastructure, provenance, and controlled alignments.

## Release status

This repository state is the technical **v0.1.0 stable candidate**. Final stable publication remains gated by human approval, W3ID activation/resolution QA, final regression, merge and tag `v0.1.0`.

- Editorial version: DLCRO v0.1
- Technical version: 0.1.0
- Ontology IRI: `https://w3id.org/dlcro`
- Stable version IRI: `https://w3id.org/dlcro/0.1.0`
- Namespace target: `https://w3id.org/dlcro/`

## Scope and claim ceiling

DLCRO supports semantic representation and audit of dental light-curing, radiometry and metrological evidence. It does not automatically infer adequate cure, clinical performance, regulatory conformity, calibration validity, or fitness for purpose of a real device.

## Modular architecture

Nine semantic modules are frozen: Core, Radiometry, Context, Metrology, LCU, Radiometer, Material, QI and Alignment. The default aggregator `ontology/dlcro.ttl` intentionally does not import Alignment. There are no external `owl:imports`.

## Validation baseline

The release candidate must preserve 10/10 Turtle parsing, 382 merged triples, zero external imports, zero import cycles, zero monitored strong OWL constructs, positive SHACL conformance, negative-fixture non-conformance with 17 results, and 15/15 Must Competency Questions compiled and non-empty.

## Repository layout

- `ontology/` — DLCRO Turtle modules and aggregator
- `validation/` — SHACL and regression assets
- `examples/` — controlled positive/negative fixtures and results
- `queries/` — 15 authoritative Must CQ SPARQL queries
- `documentation/` — public English documentation
- `release-metadata/` — release manifests and QA records

## Licensing

Ontology modules, RDF example data, SHACL, SPARQL and documentation are released under CC BY 4.0. Validation/software scripts are released under MIT. External resources remain subject to their own licenses.

## Citation

`CITATION.cff` is intentionally pending until project-authority authorship is explicitly established. No author is inferred from repository ownership.

## Limitations

Demonstration values are synthetic validation sentinels and are not clinical, calibration, conformity, or equipment-performance claims. W3ID activation is still pending.
