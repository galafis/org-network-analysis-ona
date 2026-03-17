# Architecture Overview — ONA Platform

## System Overview

The Organizational Network Analysis (ONA) Platform is a modular Python application that transforms raw organizational communication data into actionable insights about collaboration patterns, information bottlenecks, knowledge risks, and community structures.

The system follows a pipeline architecture with clear separation of concerns across six functional layers.

## Pipeline Flow

```
 ┌──────────────────────────────────────────────────────────────────────────┐
 │                        ONA Analysis Pipeline                            │
 │                                                                         │
 │  ┌─────────────┐   ┌─────────────┐   ┌─────────────────────────────┐   │
 │  │   Data      │   │   Graph     │   │     Analysis Layer          │   │
 │  │ Generation  │──▶│ Construction│──▶│                             │   │
 │  │             │   │             │   │  Centrality   Bottleneck    │   │
 │  │ employees   │   │ NetworkX    │   │  Analysis     Detection     │   │
 │  │ interactions│   │ DiGraph     │   │                             │   │
 │  └─────────────┘   └─────────────┘   │  Community    Knowledge    │   │
 │                                       │  Detection    Risk         │   │
 │                                       └──────────┬──────────────┘   │
 │                                                   │                  │
 │                                       ┌───────────▼──────────┐      │
 │                                       │  Recommendations     │      │
 │                                       │  Engine               │      │
 │                                       └───────────┬──────────┘      │
 │                                                   │                  │
 │                          ┌────────────────────────┼───────────┐      │
 │                          │                        │           │      │
 │                   ┌──────▼──────┐   ┌─────────────▼───┐      │      │
 │                   │  FastAPI    │   │    Streamlit    │      │      │
 │                   │  REST API   │   │    Dashboard    │      │      │
 │                   │  :8000      │   │    :8501        │      │      │
 │                   └──────┬──────┘   └─────────────────┘      │      │
 │                          │                                    │      │
 │                   ┌──────▼──────┐                             │      │
 │                   │ JSON Reports│                             │      │
 │                   └─────────────┘                             │      │
 └──────────────────────────────────────────────────────────────────────┘
```

## Pipeline Stages

### 1. Data Generation (`src/data/generator.py`)

Generates synthetic but realistic organizational data:
- **Employee roster**: 200 employees across 8 departments with seniority levels, tenure, and location attributes.
- **Interaction records**: Communication events across Slack, email, and meeting channels over a configurable time window. Interaction probabilities account for same-department affinity and seniority-driven cross-department connections.

### 2. Graph Construction (`src/network/graph_builder.py`)

Transforms tabular interaction data into a weighted NetworkX graph:
- Nodes represent employees, annotated with department, seniority, tenure, and location.
- Edges represent aggregated communication, weighted by interaction frequency.
- Supports both directed and undirected graph representations.

### 3. Centrality Analysis (`src/network/centrality.py`)

Computes graph-theoretic metrics for each node:
- **Betweenness centrality**: Identifies employees who bridge communication paths between otherwise disconnected groups.
- **Degree centrality**: Measures direct connectivity (in-degree and out-degree for directed graphs).
- **Closeness centrality**: Quantifies how quickly information can reach or be reached from a given node.
- **Clustering coefficient**: Measures local cohesion around each employee.

### 4. Bottleneck Detection (`src/analysis/bottleneck.py`)

Identifies structural vulnerabilities:
- Employees with high betweenness and low clustering are flagged as information bottlenecks.
- Cross-department connection counts determine single-point-of-failure risk.
- Risk levels (CRITICAL, HIGH, MODERATE, LOW) are assigned based on composite scoring.

### 5. Community Detection (`src/analysis/community.py`)

Discovers natural groupings using the Louvain algorithm:
- Optimizes modularity to find densely connected sub-networks.
- Identifies cross-departmental communities that do not align with formal org structure.
- Reports dominant department composition per community.

### 6. Recommendations Engine (`src/analysis/recommendations.py`)

Translates analytical findings into executive-level action items:
- Prioritized recommendations (HIGH, MEDIUM, LOW) with specific action items.
- Categories: knowledge transfer, silo breaking, succession planning, workload rebalancing.
- Composite organizational risk score (0-100).

### 7. Output Layer

#### FastAPI REST API (`src/api/`)
- Serves analysis results via RESTful endpoints under `/api/v1/`.
- Health check at `/api/v1/health`.
- Full analysis payload at `/api/v1/analysis`.
- Pydantic v2 schemas for request/response validation.

#### Streamlit Dashboard (`src/dashboard/app.py`)
- Interactive multi-page dashboard for visual exploration of network metrics.
- Network graph visualization via Plotly and PyVis.
- Department-level and individual-level drill-down views.

#### Report Generator (`src/reporting/report_generator.py`)
- Exports structured JSON and HTML executive reports to `data/reports/`.

## Technology Stack

| Layer               | Technology                        |
|---------------------|-----------------------------------|
| Language            | Python 3.10+                      |
| Graph Engine        | NetworkX 3.2+                     |
| Community Detection | Louvain algorithm (NetworkX)      |
| API Framework       | FastAPI 0.110+ / Uvicorn          |
| Dashboard           | Streamlit 1.32+                   |
| Visualization       | Plotly 5.20+ / PyVis              |
| Data Processing     | Pandas / NumPy / SciPy            |
| Validation          | Pydantic v2                       |
| Configuration       | pydantic-settings / python-dotenv |
| Testing             | pytest / pytest-asyncio           |
| Linting             | ruff / mypy                       |
| Containerization    | Docker / Docker Compose           |

## Deployment Architecture

```
 ┌──────────────────────────────────────────┐
 │            Docker Compose                │
 │                                          │
 │  ┌────────────┐    ┌─────────────────┐   │
 │  │  ona-api   │    │ ona-dashboard   │   │
 │  │  :8000     │    │ :8501           │   │
 │  │            │    │                 │   │
 │  │ Dockerfile │    │ Dockerfile      │   │
 │  │ .api       │    │ .dashboard      │   │
 │  └─────┬──────┘    └────────┬────────┘   │
 │        │                    │            │
 │        └────────┬───────────┘            │
 │                 │                        │
 │        ┌────────▼────────┐               │
 │        │  Shared Volume  │               │
 │        │  ona-reports    │               │
 │        └─────────────────┘               │
 └──────────────────────────────────────────┘
```

Both services share a Docker network (`ona-network`) and a volume (`ona-reports`) for report output persistence. The dashboard service depends on the API service health check passing before startup.
