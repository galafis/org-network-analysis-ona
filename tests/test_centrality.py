"""Tests for CentralityAnalyzer."""

from __future__ import annotations

import networkx as nx
import pandas as pd

from src.network.centrality import CentralityAnalyzer, CentralityReport


class TestCentralityAnalyzer:
    """Test suite for centrality metrics computation."""

    def test_analyze_returns_report(self, graph: nx.Graph) -> None:
        """analyze must return a CentralityReport."""
        analyzer = CentralityAnalyzer()
        report = analyzer.analyze(graph)
        assert isinstance(report, CentralityReport)

    def test_results_length_equals_nodes(self, graph: nx.Graph) -> None:
        """Number of results must equal number of graph nodes."""
        analyzer = CentralityAnalyzer()
        report = analyzer.analyze(graph)
        assert len(report.results) == graph.number_of_nodes()

    def test_composite_score_range(self, graph: nx.Graph) -> None:
        """Composite score must be a float in [0, 1]."""
        analyzer = CentralityAnalyzer()
        report = analyzer.analyze(graph)
        for r in report.results:
            assert isinstance(r.composite_score, float)
            assert 0.0 <= r.composite_score <= 1.0

    def test_top_connectors_length(self, graph: nx.Graph) -> None:
        """top_connectors should have at most top_k entries."""
        analyzer = CentralityAnalyzer(top_k=5)
        report = analyzer.analyze(graph)
        assert len(report.top_connectors) <= 5

    def test_top_brokers_length(self, graph: nx.Graph) -> None:
        """top_brokers should have at most top_k entries."""
        analyzer = CentralityAnalyzer(top_k=5)
        report = analyzer.analyze(graph)
        assert len(report.top_brokers) <= 5

    def test_empty_graph_returns_empty_report(self) -> None:
        """Analyzing an empty graph must return an empty report."""
        analyzer = CentralityAnalyzer()
        report = analyzer.analyze(nx.Graph())
        assert isinstance(report, CentralityReport)
        assert len(report.results) == 0
        assert len(report.top_connectors) == 0

    def test_get_centrality_dataframe(self, graph: nx.Graph) -> None:
        """get_centrality_dataframe must return a DataFrame with correct shape."""
        analyzer = CentralityAnalyzer()
        report = analyzer.analyze(graph)
        df = analyzer.get_centrality_dataframe(report)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == graph.number_of_nodes()
        expected_cols = {
            "employee_id", "degree", "betweenness", "closeness",
            "eigenvector", "pagerank", "composite_score",
        }
        assert set(df.columns) == expected_cols

    def test_small_graph_hub_has_highest_degree(self, small_graph: nx.Graph) -> None:
        """In the small_graph, EMP-0001 should have the highest degree centrality."""
        analyzer = CentralityAnalyzer(top_k=3)
        report = analyzer.analyze(small_graph)
        top_by_degree = sorted(report.results, key=lambda r: r.degree, reverse=True)
        assert top_by_degree[0].employee_id == "EMP-0001"
