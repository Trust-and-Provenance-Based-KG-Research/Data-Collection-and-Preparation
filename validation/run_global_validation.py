# /validation/run_global_validation.py
"""
Validate the merged global RDF Knowledge Graph using SHACL constraints.

Input:
    graphs/merged_graph.ttl
Output:
    validation/global_validation_report.ttl

Purpose:
    - Ensure global KG consistency after merging all named graphs.
    - Detect cross-graph datatype or ontology violations.
"""

from pyshacl import validate
from rdflib import Graph
import os

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GRAPH_FILE = os.path.join(BASE_DIR, "../graphs/merged_graph.ttl")
SHACL_FILE = os.path.join(BASE_DIR, "shacl_shapes.ttl")
OUTPUT_REPORT = os.path.join(BASE_DIR, "global_validation_report.ttl")

# Load merged RDF graph
print(f"Loading merged graph from: {GRAPH_FILE}")
data_graph = Graph()
data_graph.parse(GRAPH_FILE, format="turtle")

# Load SHACL shapes
print(f"Loading SHACL shapes from: {SHACL_FILE}")
shapes_graph = Graph()
shapes_graph.parse(SHACL_FILE, format="turtle")

# Run validation
print("Running global SHACL validation...")
conforms, report_graph, report_text = validate(
    data_graph=data_graph,
    shacl_graph=shapes_graph,
    inference="rdfs",
    debug=False
)

# Print results
print("Conforms:", conforms)
print(report_text)

# Save the report
report_graph.serialize(destination=OUTPUT_REPORT, format="turtle")
print(f"Global validation report saved to: {OUTPUT_REPORT}")
