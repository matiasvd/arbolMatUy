import json
import networkx as nx
import sys
from pathlib import Path

# -------------------------------------------------
# Arguments
# -------------------------------------------------
if len(sys.argv) != 3:
    print("Usage: python graphml_to_sigma_json.py input.graphml output.json")
    sys.exit(1)

INPUT = Path(sys.argv[1])
OUTPUT = Path(sys.argv[2])

# Load GraphML
G = nx.read_graphml(INPUT)

nodes = []
edges = []

# ---- Nodes ----
for n, attrs in G.nodes(data=True):
    # Graphviz layout may appear as strings → convert safely
    def num(x, default=0.0):
        try:
            return float(x)
        except Exception:
            return default

    nodes.append({
        "id": str(n),
        "label": attrs.get("label", n),
        "institution": attrs.get("institution", ""),
        "year": attrs.get("year", ""),
        "x": num(attrs.get("x")),
        "y": num(attrs.get("y")),
        "size": 2
    })

# ---- Edges ----
for i, (u, v) in enumerate(G.edges()):
    edges.append({
        "id": f"e{i}",
        "source": str(u),
        "target": str(v)
    })

# ---- Final Sigma-compatible format ----
sigma_graph = {
    "nodes": nodes,
    "edges": edges
}

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(sigma_graph, f, indent=2, ensure_ascii=False)

print(f"✓ Wrote {OUTPUT}")
print(f"  Nodes: {len(nodes)}")
print(f"  Edges: {len(edges)}")

