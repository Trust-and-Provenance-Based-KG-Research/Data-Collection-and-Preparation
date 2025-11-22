"""
Merge all Named Graphs into a single unified RDF graph and
generate a JSON index mapping each Named Graph URI → dataset metadata.

Outputs:
    - graphs/merged_graph.ttl
    - graphs/graph_index.json
"""

import os
import json
from rdflib import Graph, Namespace
from datetime import datetime

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NAMED_GRAPHS_DIR = os.path.join(BASE_DIR, "named_graphs")
MERGED_GRAPH_FILE = os.path.join(BASE_DIR, "merged_graph.ttl")
GRAPH_INDEX_FILE = os.path.join(BASE_DIR, "graph_index.json")

# Namespaces
FLOW = Namespace("http://flow.ai/schema/")

# Initialize global RDF graph
merged_graph = Graph()
graph_index = {}

# Iterate through all named graphs
for ttl_file in sorted(os.listdir(NAMED_GRAPHS_DIR)):
    if not ttl_file.endswith(".ttl"):
        continue

    file_path = os.path.join(NAMED_GRAPHS_DIR, ttl_file)
    graph = Graph()
    graph.parse(file_path, format="turtle")

    # Merge into the unified graph
    merged_graph += graph

    # Extract provenance info
    graph_name = ttl_file.replace(".ttl", "")
    dataset_uri = f"http://flow.ai/graph/{graph_name}"

    num_triples = len(graph)

    # Extract all publish years (if any)
    years = set()
    for s, p, o in graph.triples((None, FLOW.publishYear, None)):
        try:
            years.add(int(str(o)))
        except Exception:
            pass

    if years:
        year_min, year_max = min(years), max(years)
    else:
        year_min = year_max = None

    # Build index entry
    graph_index[dataset_uri] = {
        "graph_file": ttl_file,
        "triples": num_triples,
        "year_range": [year_min, year_max],
        "last_updated": datetime.now().isoformat(),
    }

    print(f"Merged: {ttl_file} ({num_triples} triples)")

# Serialize the merged graph
merged_graph.serialize(destination=MERGED_GRAPH_FILE, format="turtle")
print(f"\nMerged RDF graph saved to: {MERGED_GRAPH_FILE}")

# Write graph index JSON
with open(GRAPH_INDEX_FILE, "w", encoding="utf-8") as f:
    json.dump(graph_index, f, indent=4)

print(f"Graph index saved to: {GRAPH_INDEX_FILE}")

# Summary
print(f"\nTotal merged triples: {len(merged_graph)}")
print(f"Graphs indexed: {len(graph_index)}")
