# Network Metrics Glossary

## Node-Level Metrics

### Degree Centrality
**Formula:** `C_D(v) = deg(v) / (n - 1)`

Measures how many direct connections a node has, normalized by the maximum possible connections. High degree = many direct relationships.

- **In-degree**: connections received (who talks TO this person)
- **Out-degree**: connections sent (who this person talks TO)

### Betweenness Centrality
**Formula:** `C_B(v) = Σ_{s≠v≠t} [σ(s,t|v) / σ(s,t)]`

Where `σ(s,t)` = number of shortest paths between s and t, and `σ(s,t|v)` = those passing through v.

High betweenness = information bottleneck. This person sits on many communication pathways. Their absence would increase path lengths between other employees.

### Closeness Centrality
**Formula:** `C_C(v) = (n - 1) / Σ_u d(v, u)`

Where `d(v, u)` = shortest path distance between v and u.

High closeness = can reach everyone quickly. Good for identifying information disseminators.

### Eigenvector Centrality
**Formula:** `C_E(v) = (1/λ) Σ_{u ∈ N(v)} C_E(u)`

Solved as the dominant eigenvector of the adjacency matrix. Being connected to well-connected people matters more than just having many connections. Similar logic to Google's PageRank.

### PageRank
**Formula:** `PR(v) = (1-d)/n + d * Σ_{u → v} [PR(u) / out_deg(u)]`

Where `d = 0.85` (damping factor). Measures influence accounting for the quality of connections, not just quantity.

### Clustering Coefficient
**Formula:** `C(v) = 2 * T(v) / [deg(v) * (deg(v) - 1)]`

Where `T(v)` = number of triangles through v.

Measures how tightly connected a node's neighbors are to each other. High clustering = embedded in a close-knit group (good for resilience, bad if also high betweenness = isolated bottleneck).

---

## Graph-Level Metrics

### Network Density
**Formula:** `D = 2E / [N * (N - 1)]` (undirected)

Fraction of possible edges that actually exist. Low density (typical for organizations) means most people don't directly interact.

### Average Path Length
**Formula:** `L = (1 / [n(n-1)]) * Σ_{i≠j} d(i, j)`

Average number of steps to get from any node to any other. Lower = faster information flow.

### Modularity
**Formula:** `Q = Σ_c [L_c/m - (d_c/2m)²]`

Measures how well-defined the community structure is. Higher modularity = more siloed. Range: [-1, 1], with >0.3 indicating meaningful community structure.

### Transitivity (Global Clustering Coefficient)
**Formula:** `T = 3 * (closed triangles) / (all triads)`

Fraction of all possible triangles that are closed. Higher = more cohesive network.

---

## Derived Metrics (ONA-Specific)

### Bottleneck Score
**Formula:** `BS(v) = betweenness_rank(v) * (1 - clustering_coeff(v))`

High betweenness + low clustering = isolated bridge between groups. The most dangerous bottleneck pattern.

### Knowledge Loss Risk Score
**Formula:** `KLR(v) = 0.5 * betweenness_rank(v) + 0.3 * (tenure / max_tenure) + 0.2 * degree_rank(v)`

Composite score estimating organizational impact of losing this employee.

### Silo Ratio
**Formula:** `SR(dept) = cross_dept_interactions / total_interactions_for_dept`

How much of a department's communication crosses departmental boundaries. Below org average = potential silo.
