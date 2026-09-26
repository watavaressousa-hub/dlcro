#!/usr/bin/env python3
"""
DLCRO VAL-03 deterministic SHACL Core subset validator.


Supported constraints are deliberately limited to the constructs used by
dlcro_minimal_shapes.ttl:
- sh:targetClass
- sh:property / sh:path
- sh:minCount
- sh:class
- sh:datatype


This is not a substitute for a full SHACL implementation. It is a reproducible
validator for the frozen minimal profile used in Pull 09. A full pySHACL/Jena
regression test is required if the shapes introduce other SHACL constructs.
"""
import sys, json
from rdflib import Graph, RDF, Literal
from rdflib.namespace import SH


def validate(data_path, shapes_path):
    data = Graph().parse(data_path, format="turtle")
    shapes = Graph().parse(shapes_path, format="turtle")
    violations = []
    for ns in shapes.subjects(RDF.type, SH.NodeShape):
        target_classes = list(shapes.objects(ns, SH.targetClass))
        if not target_classes:
            continue
        focus_nodes = set()
        for tc in target_classes:
            focus_nodes.update(data.subjects(RDF.type, tc))
        for focus in focus_nodes:
            for ps in shapes.objects(ns, SH.property):
                path = shapes.value(ps, SH.path)
                if path is None:
                    continue
                values = list(data.objects(focus, path))
                min_count = shapes.value(ps, SH.minCount)
                if min_count is not None and len(values) < int(min_count):
                    violations.append({
                        "focus": str(focus), "shape": str(ns), "path": str(path),
                        "constraint": "minCount", "expected": int(min_count),
                        "actual": len(values)
                    })
                expected_class = shapes.value(ps, SH["class"])
                if expected_class is not None:
                    for value in values:
                        if (value, RDF.type, expected_class) not in data:
                            violations.append({
                                "focus": str(focus), "shape": str(ns), "path": str(path),
                                "constraint": "class", "value": str(value),
                                "expected": str(expected_class)
                            })
                datatype = shapes.value(ps, SH.datatype)
                if datatype is not None:
                    for value in values:
                        if not isinstance(value, Literal) or value.datatype != datatype:
                            violations.append({
                                "focus": str(focus), "shape": str(ns), "path": str(path),
                                "constraint": "datatype", "value": str(value),
                                "actual": str(getattr(value, "datatype", None)),
                                "expected": str(datatype)
                            })
    return violations


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("usage: VAL03_validator.py DATA.ttl SHAPES.ttl")
    violations = validate(sys.argv[1], sys.argv[2])
    print(json.dumps({
        "conforms": not violations,
        "violation_count": len(violations),
        "violations": violations
    }, indent=2))
    raise SystemExit(0 if not violations else 1)