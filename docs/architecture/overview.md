# Architecture Overview — ONA Platform

## System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     ONA Platform                            │
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  Data Layer  │    │ Network Layer│    │  Output Layer│  │
│  │              │    │              │    │              │  │
│  │ OrgData      │───▶│ NetworkBuilder│───▶│ FastAPI      │  │
│  │ Generator    │    │ NetworkMetrics│   │ Routes       │  │
│  │              │    │ OrgAnalyzer  │    │              │  │
│  └──────────────┘    └──────────────┘    └──────┬───────┘  │
│                                                 │           │
│  ┌──────────────┐    ┌──────────────┐           │           │
│  │ Recommenda-  │    │ Visualization│           │           │
│  │ tion Engine  │    │ GraphViz     │           │           │
│  └──────────────┘    └──────────────┘           │           │
│                                                 │           │
│  ┌──────────────┐    ┌──────────────┐           │           │
│  │ Report       │    │  Streamlit   │◀──────────┘           │
│  │ Generator    │    │  Dashboard   │                       │
│  └──────────────┘    └──────────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

1. **OrgDataGenerator** creates synthetic employees and interactions
2. **NetworkBuilder** constructs a weighted directed NetworkX graph
3. **NetworkMetrics** computes centrality, community detection (Louvain), path metrics
4. **OrgAnalyzer** runs bottleneck detection, silo analysis, knowledge risk assessment
5. **RecommendationEngine** translates findings into executive recommendations
6. **FastAPI** serves results via REST endpoints
7. **Streamlit Dashboard** provides interactive visualization
8. **ReportGenerator** exports JSON and HTML executive reports

## Technology Stack

| Layer | Technology |
|-------|------------|
| Graph Engine | NetworkX 3.x |
| Community Detection | python-louvain (Louvain algorithm) |
| API | FastAPI + Uvicorn |
| Dashboard | Streamlit |
| Visualization | Plotly |
| Data | Pandas + NumPy |
| Validation | Pydantic v2 |
| Testing | pytest + pytest-asyncio |
| Linting | ruff + mypy |
| Containerization | Docker + Docker Compose |
