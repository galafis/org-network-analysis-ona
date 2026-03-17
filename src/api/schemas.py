"""Pydantic v2 schemas for the ONA REST API."""

from __future__ import annotations

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "ok"
    service: str = "ona-api"


class GraphStatsOut(BaseModel):
    """Graph statistics output schema."""

    n_nodes: int
    n_edges: int
    density: float
    avg_clustering: float
    n_connected_components: int
    avg_degree: float
    diameter: int | None = None


class BottleneckOut(BaseModel):
    """Bottleneck result output schema."""

    employee_id: str
    betweenness: float
    degree: int
    departments_connected: int
    risk_level: str
    reason: str


class KnowledgeRiskOut(BaseModel):
    """Knowledge risk output schema."""

    employee_id: str
    department: str
    seniority: str
    tenure_years: float
    unique_connections: int
    knowledge_score: float
    risk_level: str
    replacement_difficulty: str


class RecommendationOut(BaseModel):
    """Recommendation output schema."""

    priority: str
    category: str
    title: str
    description: str
    action_items: list[str] = Field(default_factory=list)


class CommunityOut(BaseModel):
    """Community info output schema."""

    community_id: int
    size: int
    dominant_department: str
    cross_department: bool
    departments: dict[str, int] = Field(default_factory=dict)


class AnalysisResponse(BaseModel):
    """Full analysis response schema."""

    graph_stats: GraphStatsOut
    bottlenecks: list[BottleneckOut] = Field(default_factory=list)
    knowledge_risks: list[KnowledgeRiskOut] = Field(default_factory=list)
    communities: list[CommunityOut] = Field(default_factory=list)
    recommendations: list[RecommendationOut] = Field(default_factory=list)
    risk_score: int = 0
    summary: str = ""
