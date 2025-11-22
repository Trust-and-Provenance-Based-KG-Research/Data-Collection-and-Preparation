from pyshacl import validate
from rdflib import Graph
import os

# Paths
GRAPH_DIR = "graphs/named_graphs"
SHACL_FILE = "validation/shacl_shapes.ttl"
OUTPUT_REPORT = "validation/validation_report.ttl"

# Combine all named graphs
combined_graph = Graph()
for file in os.listdir(GRAPH_DIR):
    if file.endswith(".ttl"):
        combined_graph.parse(os.path.join(GRAPH_DIR, file), format="turtle")
        print(f"Added {file}")

# Load SHACL shapes
shapes_graph = Graph()
shapes_graph.parse(SHACL_FILE, format="turtle")

# Validate
conforms, report_graph, report_text = validate(
    data_graph=combined_graph,
    shacl_graph=shapes_graph,
    inference="rdfs",
    debug=False
)

# Print and save results
print("Conforms:", conforms)
print(report_text)

report_graph.serialize(destination=OUTPUT_REPORT, format="turtle")
print(f"Validation report saved to {OUTPUT_REPORT}")
