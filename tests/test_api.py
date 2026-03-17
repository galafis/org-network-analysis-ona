"""Tests for the ONA FastAPI endpoints."""

from __future__ import annotations

import networkx as nx
import pytest
from httpx import ASGITransport, AsyncClient

from src.analysis.runner import run_full_analysis
from src.api.main import create_app


@pytest.fixture(scope="module")
def analysis_result() -> object:
    """Build a small graph and run analysis for API tests."""
    g = nx.Graph()
    for i in range(1, 16):
        g.add_node(
            f"EMP-{i:04d}",
            department="Engineering" if i <= 5 else ("Sales" if i <= 10 else "HR"),
            seniority="Senior" if i <= 3 else "Mid",
            tenure_years=float(i),
        )
    # Create edges: star topology + some random
    for i in range(2, 16):
        g.add_edge("EMP-0001", f"EMP-{i:04d}", weight=5)
    g.add_edge("EMP-0006", "EMP-0007", weight=3)
    g.add_edge("EMP-0011", "EMP-0012", weight=2)
    return run_full_analysis(g, betweenness_threshold=0.05)


@pytest.fixture
def app(analysis_result: object):
    """Create FastAPI app with pre-populated analysis state."""
    application = create_app()
    application.state.analysis = analysis_result
    return application


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health(client):
    resp = await client.get("/api/v1/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_analysis_endpoint(client):
    resp = await client.get("/api/v1/analysis")
    assert resp.status_code == 200
    data = resp.json()
    assert "graph_stats" in data
    assert "bottlenecks" in data
    assert "recommendations" in data
    assert "risk_score" in data


@pytest.mark.asyncio
async def test_analysis_has_communities(client):
    resp = await client.get("/api/v1/analysis")
    data = resp.json()
    assert "communities" in data
    assert isinstance(data["communities"], list)


@pytest.mark.asyncio
async def test_analysis_graph_stats_fields(client):
    resp = await client.get("/api/v1/analysis")
    data = resp.json()
    stats = data["graph_stats"]
    assert "n_nodes" in stats
    assert "n_edges" in stats
    assert "density" in stats


@pytest.mark.asyncio
async def test_analysis_risk_score_range(client):
    resp = await client.get("/api/v1/analysis")
    data = resp.json()
    assert 0 <= data["risk_score"] <= 100
