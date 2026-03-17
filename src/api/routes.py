"""FastAPI route definitions for ONA API."""

from __future__ import annotations

from fastapi import APIRouter, Request

from src.api.schemas import (
    AnalysisResponse,
    BottleneckOut,
    CommunityOut,
    GraphStatsOut,
    HealthResponse,
    KnowledgeRiskOut,
    RecommendationOut,
)

router = APIRouter(prefix="/api/v1", tags=["ona"])


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Return service health status."""
    return HealthResponse()


@router.get("/analysis", response_model=AnalysisResponse)
async def get_analysis(request: Request) -> AnalysisResponse:
    """Return full organizational network analysis results."""
    result = request.app.state.analysis

    graph_stats = GraphStatsOut(
        n_nodes=result.graph_stats.n_nodes,
        n_edges=result.graph_stats.n_edges,
        density=result.graph_stats.density,
        avg_clustering=result.graph_stats.avg_clustering,
        n_connected_components=result.graph_stats.n_connected_components,
        avg_degree=result.graph_stats.avg_degree,
        diameter=result.graph_stats.diameter,
    )

    bottlenecks = [
        BottleneckOut(
            employee_id=b.employee_id,
            betweenness=b.betweenness,
            degree=b.degree,
            departments_connected=b.departments_connected,
            risk_level=b.risk_level.value,
            reason=b.reason,
        )
        for b in result.bottleneck.bottlenecks
    ]

    knowledge_risks = [
        KnowledgeRiskOut(
            employee_id=k.employee_id,
            department=k.department,
            seniority=k.seniority,
            tenure_years=k.tenure_years,
            unique_connections=k.unique_connections,
            knowledge_score=k.knowledge_score,
            risk_level=k.risk_level.value,
            replacement_difficulty=k.replacement_difficulty,
        )
        for k in result.bottleneck.knowledge_risks[:20]
    ]

    communities = [
        CommunityOut(
            community_id=c.community_id,
            size=c.size,
            dominant_department=c.dominant_department,
            cross_department=c.cross_department,
            departments=c.departments,
        )
        for c in result.community.communities
    ]

    recommendations = [
        RecommendationOut(
            priority=r.priority.value,
            category=r.category,
            title=r.title,
            description=r.description,
            action_items=r.action_items,
        )
        for r in result.recommendations.recommendations
    ]

    return AnalysisResponse(
        graph_stats=graph_stats,
        bottlenecks=bottlenecks,
        knowledge_risks=knowledge_risks,
        communities=communities,
        recommendations=recommendations,
        risk_score=result.recommendations.risk_score,
        summary=result.recommendations.summary,
    )
