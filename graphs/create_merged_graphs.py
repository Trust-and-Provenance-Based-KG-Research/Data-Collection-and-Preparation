import pandas as pd
import os
from rdflib import Graph, Literal, RDF, URIRef, Namespace, XSD

# -----------------------------------------------------------------------------
# Flow Named Graph Builder (Ontology-aware)
# -----------------------------------------------------------------------------
# This explicitly loads and binds ontology + schema definitions
# from the ontology folder before creating Named Graphs.
# -----------------------------------------------------------------------------

# Namespaces
FLOW = Namespace("http://flow.ai/schema/")
PROV = Namespace("http://www.w3.org/ns/prov#")
SCHEMA = Namespace("http://schema.org/")

# Input and output directories
DATA_DIR = "../Prove_Data/Preprocessed_Provenance_Datasets"
ONTOLOGY_DIR = "ontology"
OUTPUT_DIR = "graphs/merged_graphs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def csv_to_named_graph(csv_path: str, batch_name: str):
    """Convert a preprocessed CSV file into a Named Graph (.ttl) using the Flow Provenance Ontology."""

    # Load dataset
    df = pd.read_csv(csv_path)

    # Initialize RDF Graph
    g = Graph()

    # Load ontology and schema to bind classes & properties
    ontology_files = ["provenance_ontology.ttl", "schema.ttl"]
    for file in ontology_files:
        onto_path = os.path.join(ONTOLOGY_DIR, file)
        if os.path.exists(onto_path):
            g.parse(onto_path, format="turtle")
            print(f"Loaded ontology: {onto_path}")
        else:
            print(f"Ontology file missing: {onto_path}")

    # Bind namespaces
    g.bind("flow", FLOW)
    g.bind("prov", PROV)
    g.bind("schema", SCHEMA)

    # Define dataset URI (used as provenance Named Graph reference)
    dataset_uri = URIRef(f"http://flow.ai/graph/{batch_name}")
    dataset_res = URIRef(f"http://flow.ai/dataset/{batch_name}")
    g.add((dataset_res, RDF.type, FLOW.Dataset))
    g.add((dataset_res, SCHEMA.name, Literal(batch_name, datatype=XSD.string)))

    # Iterate over each video row
    for _, row in df.iterrows():
        video_uri = URIRef(f"http://flow.ai/video/{row['video_id']}")

        # Add triples for video entity
        g.add((video_uri, RDF.type, FLOW.Video))
        g.add((video_uri, FLOW.videoId, Literal(row['video_id'], datatype=XSD.string)))
        g.add((video_uri, FLOW.title, Literal(row['video_title_(original)'], datatype=XSD.string)))
        g.add((video_uri, FLOW.description, Literal(row['video_description_(original)'], datatype=XSD.string)))

        # Handle duration
        if pd.notnull(row['approx_duration_(ms)']):
            g.add((video_uri, FLOW.durationMs, Literal(int(row['approx_duration_(ms)']), datatype=XSD.integer)))

        # Handle timestamp and year
        if pd.notnull(row['video_publish_timestamp']):
            g.add((video_uri, FLOW.publishTimestamp, Literal(row['video_publish_timestamp'], datatype=XSD.dateTime)))
        if pd.notnull(row['publish_year']):
            g.add((video_uri, FLOW.publishYear, Literal(int(row['publish_year']), datatype=XSD.gYear)))

        # Add provenance link to dataset
        g.add((video_uri, FLOW.belongsToDataset, dataset_res))
        g.add((video_uri, PROV.wasDerivedFrom, dataset_res))

    # Serialize graph to Turtle format
    output_path = os.path.join(OUTPUT_DIR, f"graph_{batch_name}.ttl")
    g.serialize(destination=output_path, format="turtle")
    print(f"Ontology-aware Named Graph created: {output_path}")


def main():
    # Map batch names to CSV paths
    datasets = {
        "first_batch": f"{DATA_DIR}/first_batch_metadata_preprocessed.csv",
        "second_batch": f"{DATA_DIR}/second_batch_metadata_preprocessed.csv",
        "third_batch": f"{DATA_DIR}/third_batch_metadata_preprocessed.csv",
        "fourth_batch": f"{DATA_DIR}/fourth_batch_metadata_preprocessed.csv",
    }

    # Generate named graphs for each dataset batch
    for batch_name, csv_path in datasets.items():
        if os.path.exists(csv_path):
            csv_to_named_graph(csv_path, batch_name)
        else:
            print(f"Missing dataset file: {csv_path}")

if __name__ == "__main__":
    main()
