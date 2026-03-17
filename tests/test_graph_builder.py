"""Tests for OrgGraphBuilder."""

from __future__ import annotations

import networkx as nx
import pandas as pd

from src.network.graph_builder import GraphStats, OrgGraphBuilder


class TestOrgGraphBuilder:
    """Test suite for the graph builder."""

    def test_build_returns_graph(
        self, employees_df: pd.DataFrame, interactions_df: pd.DataFrame
    ) -> None:
        """build_from_interactions must return a networkx Graph."""
        builder = OrgGraphBuilder()
        g = builder.build_from_interactions(interactions_df, employees_df)
        assert isinstance(g, nx.Graph)

    def test_correct_node_count(self, graph: nx.Graph) -> None:
        """Graph should contain 50 nodes (one per employee)."""
        assert graph.number_of_nodes() == 50

    def test_edges_have_weight(self, graph: nx.Graph) -> None:
        """Every edge must carry a 'weight' attribute."""
        for _u, _v, edata in graph.edges(data=True):
            assert "weight" in edata
            assert edata["weight"] > 0

    def test_get_stats_returns_graphstats(self, graph: nx.Graph) -> None:
        """get_stats must return a GraphStats dataclass with correct n_nodes."""
        builder = OrgGraphBuilder()
        stats = builder.get_stats(graph)
        assert isinstance(stats, GraphStats)
        assert stats.n_nodes == 50

    def test_get_stats_fields(self, graph: nx.Graph) -> None:
        """GraphStats must have all expected numeric fields."""
        builder = OrgGraphBuilder()
        stats = builder.get_stats(graph)
        assert stats.n_edges > 0
        assert 0.0 <= stats.density <= 1.0
        assert stats.avg_degree > 0.0
        assert stats.n_connected_components >= 1

    def test_filter_by_department(
        self, employees_df: pd.DataFrame, interactions_df: pd.DataFrame
    ) -> None:
        """filter_by_department must return a subgraph of only that department."""
        builder = OrgGraphBuilder()
        builder.build_from_interactions(interactions_df, employees_df)
        sub = builder.filter_by_department("Engineering")
        for _, data in sub.nodes(data=True):
            assert data.get("department") == "Engineering"

    def test_get_cross_department_edges(
        self, employees_df: pd.DataFrame, interactions_df: pd.DataFrame
    ) -> None:
        """Cross-department edges must connect different departments."""
        builder = OrgGraphBuilder()
        g = builder.build_from_interactions(interactions_df, employees_df)
        cross = builder.get_cross_department_edges()
        assert isinstance(cross, list)
        for u, v, _edata in cross:
            dept_u = g.nodes[u].get("department")
            dept_v = g.nodes[v].get("department")
            assert dept_u != dept_v

    def test_build_directed_returns_digraph(
        self, employees_df: pd.DataFrame, interactions_df: pd.DataFrame
    ) -> None:
        """build_directed must return a DiGraph."""
        builder = OrgGraphBuilder()
        dg = builder.build_directed(interactions_df, employees_df)
        assert isinstance(dg, nx.DiGraph)

    def test_empty_graph_handling(self) -> None:
        """get_stats on an empty graph must not raise."""
        builder = OrgGraphBuilder()
        stats = builder.get_stats(nx.Graph())
        assert stats.n_nodes == 0
        assert stats.n_edges == 0
