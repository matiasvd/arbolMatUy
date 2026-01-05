####
# Codigo aportado por Bernardo Marenco.
# 12/25.
####

import pydot
import networkx as nx
import re
import sys
from pathlib import Path

if len(sys.argv) != 3:
    print("Usage: python dot_to_graphml.py input.dot output.graphml")
    sys.exit(1)
    
DOT_FILE = Path(sys.argv[1])
GRAPHML_FILE = Path(sys.argv[2])


# -----------------------------
# Read DOT using pydot
# -----------------------------
graphs = pydot.graph_from_dot_file(DOT_FILE)
pd_graph = graphs[0]

# Convert to NetworkX
G0 = nx.nx_pydot.from_pydot(pd_graph)

# Ensure directed multigraph (safe default for DOT)
G0 = nx.MultiDiGraph(G0)

# Convert Graphviz pos to Gephi coordinates
for node, attrs in G0.nodes(data=True):
    pos = attrs.get("pos")
    if isinstance(pos, str):
        # Remove quotes if present
        pos = pos.strip('"')

        # Graphviz pos is "x,y" or "x,y!"
        pos = pos.rstrip("!")

        try:
            x_str, y_str = pos.split(",")[:2]
            attrs["x"] = float(x_str)
            attrs["y"] = float(y_str)
        except ValueError:
            pass

        # Remove Graphviz-specific attribute
        del attrs["pos"]

# -----------------------------
# Helper: GraphML-safe values
# -----------------------------
def is_graphml_scalar(x):
    return isinstance(x, (str, int, float, bool))


# -----------------------------
# Clean node attributes
# -----------------------------
for node, attrs in G0.nodes(data=True):
    for k in list(attrs):
        if not is_graphml_scalar(attrs[k]):
            del attrs[k]


# -----------------------------
# Clean edge attributes
# -----------------------------
for _, _, _, attrs in G0.edges(keys=True, data=True):
    for k in list(attrs):
        if not is_graphml_scalar(attrs[k]):
            del attrs[k]


# -----------------------------
# Clean graph-level attributes
# -----------------------------
for k in list(G0.graph):
    if not is_graphml_scalar(G0.graph[k]):
        del G0.graph[k]


# -----------------------------
# Fix labels and split name / affiliation
# -----------------------------
year_pattern = re.compile(r"(.*?)(?:\s+(\d{4}))?$")

for node, attrs in G0.nodes(data=True):
    # Prefer DOT label, fallback to node id
    raw = attrs.get("label", node)

    if isinstance(raw, str):
        # Remove surrounding quotes if present
        raw = raw.strip()
        if raw.startswith('"') and raw.endswith('"'):
            raw = raw[1:-1]

        # Convert escaped newline to real newline
        raw = raw.replace("\\n", "\n")

        # Split name / affiliation on first newline
        parts = raw.split("\n", 1)
        name = parts[0].strip()
        affiliation = parts[1].strip() if len(parts) > 1 else ""

        # Parse institution + year
        institution = ""
        year = ""

        if affiliation:
            m = year_pattern.fullmatch(affiliation)
            if m:
                institution = (m.group(1) or "").strip()
                year = m.group(2) or ""

        # Store clean attributes
        attrs["label"] = name          # Gephi display label
        attrs["name"] = name
        attrs["institution"] = institution
        attrs["year"] = year


# -----------------------------
# Remove dummy / empty nodes
# -----------------------------
to_remove = []

for node, attrs in G0.nodes(data=True):
    label = attrs.get("label", "")
    if not isinstance(label, str) or not label.strip():
        to_remove.append(node)
        
print("Removing dummy nodes:")
    
for node in to_remove:
    print(repr(node))
    G0.remove_node(node)


# -----------------------------
# CRITICAL: rebuild graph with unique edge keys
# (Gephi Lite requires globally unique edge IDs)
# -----------------------------
G = nx.MultiDiGraph()
G.add_nodes_from(G0.nodes(data=True))

for i, (u, v, _, attrs) in enumerate(G0.edges(keys=True, data=True)):
    G.add_edge(u, v, key=f"e{i}", **attrs)


# -----------------------------
# Write GraphML
# -----------------------------
nx.write_graphml(G, GRAPHML_FILE)

print(f"GraphML written to: {GRAPHML_FILE}")

