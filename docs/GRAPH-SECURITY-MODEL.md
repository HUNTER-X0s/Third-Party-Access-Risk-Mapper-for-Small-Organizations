# GRAPH SECURITY REASONING ENGINE MODEL
# AccessGuard: Graph Topology, Traversal Algorithms, Attack Paths & Blast Radius

**Document Type:** Technical Architecture Specification  
**Version:** 1.0  
**Date:** 2026-08-13  
**Status:** Approved Technical Specification  

---

## 1. Graph Domain Architecture (Server-Side Reasoning)

React Flow is **strictly a rendering library**. The authoritative graph reasoning engine operates on the server-side as an in-memory directed graph domain model (`AccessGraph Engine`).

```
┌────────────────────────────────────────────────────────────────────────┐
│                        ACCESSGRAPH DOMAIN ENGINE                       │
├────────────────────────────────────────────────────────────────────────┤
│ Node Types:                                                            │
│  - VendorNode (V)                                                      │
│  - ApplicationInstanceNode (A)                                         │
│  - PermissionGrantNode (P)                                             │
│  - DataAssetNode (D)                                                   │
│  - UserIdentityNode (U)                                                │
│                                                                        │
│ Edge Types (Directed):                                                 │
│  - PROV_BY   : (V) -> (A)  [Vendor provides Application]              │
│  - AUTH_BY   : (U) -> (A)  [User authorized Application]              │
│  - HAS_GRANT : (A) -> (P)  [Application holds Permission Grant]        │
│  - REACHES   : (P) -> (D)  [Permission reaches Data Asset]            │
│  - DEPENDS_ON: (A) -> (A)  [App relies on another App / Zapier chain]   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Exports Graph JSON
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                    REACT FLOW PRESENTATION LAYER                       │
│  - Custom Nodes (Compact, High-Density Cards)                          │
│  - Dynamic Edge Color & Stroke Thickness (Severity Weight)             │
│  - Interactive Path Highlighting & Zoom Controls                       │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Quantitative Blast-Radius Calculation

The Blast Radius of an Application Instance $A_i$ represents the total set of reachable data assets, users, and business processes exposed if $A_i$ (or its vendor) is compromised.

$$\text{BlastRadiusSet}(A_i) = \{ D_k \in \text{DataAssets} \mid \exists \text{ path } P = (A_i \to \dots \to D_k) \}$$

### Quantitative Metric Output:
```python
@dataclass
class BlastRadiusMetric:
    application_instance_id: UUID
    total_reachable_assets_count: int
    critical_asset_count: int
    exposed_data_classifications: List[str]  # ["PII", "FINANCIAL"]
    affected_departments: List[str]          # ["FINANCE", "EXECUTIVE"]
    estimated_blast_score: float             # 0.0 to 100.0
```

---

## 3. Attack-Path Discovery & Traversal Algorithm

AccessGuard identifies **Potential Attack Paths** (Access Paths) by conducting depth-first directed search (DFS) with pruning from entry-point applications to high-sensitivity Data Assets ($D_{\text{critical}}$).

### Terminology Precision:
> AccessGuard explicitly labels graph chains as **"Potential Access Paths"** or **"Reachable Attack Surfaces"** rather than claiming verified exploitability, unless direct breach indicators exist.

### Algorithm Specification (Python Engine):
```python
def find_potential_attack_paths(
    graph: AccessGraph,
    start_app_id: UUID,
    max_depth: int = 4
) -> List[AttackPathResult]:
    paths = []
    
    def dfs(current_node, current_path, visited_nodes):
        if len(current_path) > max_depth:
            return
            
        if current_node.type == NodeType.DATA_ASSET and current_node.sensitivity >= 4:
            # Reached a critical crown jewel asset
            paths.append(construct_path_result(current_path))
            return

        for neighbor, edge in graph.get_out_edges(current_node):
            if neighbor not in visited_nodes:
                dfs(neighbor, current_path + [(neighbor, edge)], visited_nodes | {neighbor})

    dfs(graph.get_node(start_app_id), [start_app_id], {start_app_id})
    return prioritize_paths_by_risk(paths)
```

---

## 4. Graph Filtering & Performance Optimizations

To maintain 60 FPS performance in the frontend while rendering complex graphs (up to 500 nodes):
1. **Server-Side Subgraph Filtering**: The API returns only subgraphs filtered by selected organization, severity, or active search path.
2. **Viewport Clustering**: Nodes beyond current zoom viewport are grouped into cluster summaries.
3. **Memoized Graph Calculations**: Traversal paths and blast-radius metrics are cached per sync generation.

---

*Graph Security Model v1.0 — Approved Engine Specification.*
