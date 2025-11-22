# Data-Collection-and-Preparation

### 1. Setup the GraphDB and Confirm that the container is running

Run this in your project directory (where your `docker-compose.yml` lives):

```bash
docker-compose up -d
```
To confirm that the container is available run the below:

```bash
docker ps
```

You should see something like:

```
CONTAINER ID   IMAGE                     COMMAND                 PORTS                    NAMES
e2bcd7b22352   ontotext/graphdb:10.7.0   "/opt/graphdb/dist/b…"  0.0.0.0:7200->7200/tcp,  flow-prov-graphdb
```

---

### 2. Verify the GraphDB Workbench is accessible

In your browser, open:
**[http://localhost:7200](http://localhost:7200)**

You should see the **GraphDB Workbench** interface.

If this page doesn’t load:

* Either the container isn’t starting correctly,
* or the port mapping isn’t active,
* or GraphDB crashed during boot.

Check logs:

```bash
docker logs flow-prov-graphdb
```

You should see something like:

```
Starting GraphDB...
Listening on port 7200
```

If you see repeated restarts or errors, fix those first (for example, by cleaning up the data directory).

---

### 3. Create the **`flow_kg`** repository exists

1. Go to **[http://localhost:7200](http://localhost:7200)**
2. Click **Setup → Repositories → Create new repository**
3. Name: `flow_kg`
4. Ruleset: `rdfs+`
5. Create.


### 4. Test GraphDB health with a GET (Optional)

Before sending data, test the endpoint with a simple request:

```bash
curl http://localhost:7200/rest/repositories
```

If it works, you’ll get JSON output like:

```json
[
  {
    "id": "flow_kg",
    "title": "flow_kg",
    "uri": "http://localhost:7200/repositories/flow_kg"
  }
]
```

If you still get a connection reset:

* Check Docker network configuration (`docker inspect flow-prov-graphdb`).
* Confirm port `7200` is not used by another process (`sudo lsof -i :7200`).
* Restart container (`docker-compose restart`).

### 5. Upload Turtle files

### **1. Upload `graph_first_batch.ttl`**

```bash
curl -X POST \
  -H "Content-Type: application/x-turtle" \
  --data-binary @graphs/named_graphs/graph_first_batch.ttl \
  "http://localhost:7200/repositories/flow_kg/statements?context=%3Chttp://flow.ai/graph/first_batch%3E"
```

---

### **2. Upload `graph_second_batch.ttl`**

```bash
curl -X POST \
  -H "Content-Type: application/x-turtle" \
  --data-binary @graphs/named_graphs/graph_second_batch.ttl \
  "http://localhost:7200/repositories/flow_kg/statements?context=%3Chttp://flow.ai/graph/second_batch%3E"
```

---

### **3. Upload `graph_third_batch.ttl`**

```bash
curl -X POST \
  -H "Content-Type: application/x-turtle" \
  --data-binary @graphs/named_graphs/graph_third_batch.ttl \
  "http://localhost:7200/repositories/flow_kg/statements?context=%3Chttp://flow.ai/graph/third_batch%3E"
```

---

### **4. Upload `graph_fourth_batch.ttl`**

```bash
curl -X POST \
  -H "Content-Type: application/x-turtle" \
  --data-binary @graphs/named_graphs/graph_fourth_batch.ttl \
  "http://localhost:7200/repositories/flow_kg/statements?context=%3Chttp://flow.ai/graph/fourth_batch%3E"
```

---

## **Test the GraphDB**

1. Go to **GraphDB → SPARQL → Editor**.
2. Copy-paste any of the queries.
3. Press **Run**.
4. Results will show provenance (`?dataset`) and semantic fields.

### 1. **Provenance & Temporal Query**

**Question:**

> “Which videos published between 2019 and 2020 introduce *programming* or *Python basics*, and from which dataset batch do they originate?”

```sparql
PREFIX flow: <http://flow.ai/schema/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?video ?title ?publishYear ?dataset
WHERE {
  GRAPH ?dataset {
    ?video a flow:Video ;
           flow:title ?title ;
           flow:publishYear ?publishYear .
    FILTER (
      (?publishYear >= "2019"^^xsd:gYear && ?publishYear <= "2020"^^xsd:gYear) &&
      (CONTAINS(LCASE(?title), "programming") || CONTAINS(LCASE(?title), "python"))
    )
  }
}
ORDER BY ?publishYear
```

**Tests:**

* Temporal filtering (`xsd:gYear`)
* Keyword-based semantic filtering
* Provenance (via `GRAPH ?dataset`)

---

## 2. **Contextual Semantic Retrieval**

**Question:**

> “Find all videos that explain *image segmentation* methods, including U-Net, LinkNet, watershed, or StarDist, even if the term ‘segmentation’ isn’t used in the title.”

```sparql
PREFIX flow: <http://flow.ai/schema/>

SELECT ?video ?title ?description ?dataset
WHERE {
  GRAPH ?dataset {
    ?video a flow:Video ;
           flow:title ?title ;
           flow:description ?description .
    FILTER (
      REGEX(LCASE(CONCAT(?title, " ", ?description)),
            "(segmentation|u-net|linknet|watershed|stardist)")
    )
  }
}
```

**Tests:**

* Semantic similarity through regex pattern matching
* Contextual understanding across title + description
* Multi-graph provenance tracing

---

### 3. **Provenance Chain Trace**

**Question:**

> “Show the provenance trail for the video *‘3D U-Net for semantic segmentation’* — which dataset it was derived from, when it was added, and what transformations were applied.”

```sparql
PREFIX flow: <http://flow.ai/schema/>
PREFIX prov: <http://www.w3.org/ns/prov#>

SELECT ?video ?dataset ?publishTimestamp ?activity ?wasDerivedFrom
WHERE {
  GRAPH ?dataset {
    ?video a flow:Video ;
           flow:title ?title ;
           flow:publishTimestamp ?publishTimestamp .
    FILTER(CONTAINS(LCASE(?title), "3d u-net for semantic segmentation"))
  }
  OPTIONAL { ?video prov:wasDerivedFrom ?wasDerivedFrom . }
  OPTIONAL { ?video prov:wasGeneratedBy ?activity . }
}
```

**Tests:**

* PROV-O lineage (`wasDerivedFrom`, `wasGeneratedBy`)
* Temporal provenance fields
* Graph-level traceability

---

### 4. **Thematic Evolution Query**

**Question:**

> “How has the topic of *image analysis* evolved across datasets — list videos per year that mention histogram, segmentation, or DCT, ordered chronologically.”

```sparql
PREFIX flow: <http://flow.ai/schema/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?year ?video ?title ?dataset
WHERE {
  GRAPH ?dataset {
    ?video a flow:Video ;
           flow:title ?title ;
           flow:publishYear ?year .
    FILTER (
      REGEX(LCASE(?title), "(histogram|segmentation|dct|image analysis)")
    )
  }
}
ORDER BY ?year
```

**Tests:**

* Cross-graph aggregation
* Chronological ordering
* Thematic evolution detection

---

## 5. **Quality & Duration Correlation**

**Question:**

> “Which videos longer than 15 minutes discuss *COVID-19 data analysis* and what are their publish timestamps and batch provenance?”

```sparql
PREFIX flow: <http://flow.ai/schema/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?video ?title ?duration ?publishTimestamp ?dataset
WHERE {
  GRAPH ?dataset {
    ?video a flow:Video ;
           flow:title ?title ;
           flow:durationMs ?duration ;
           flow:publishTimestamp ?publishTimestamp .
    FILTER (
      ?duration > 900000 &&
      REGEX(LCASE(?title), "covid|data analysis|predicting covid")
    )
  }
}
ORDER BY DESC(?duration)
```

**Tests:**

* Numeric reasoning (`> 900000` ms ≈ 15 minutes)
* Topic association
* Temporal precision
