"""Tests for RecommendationEngine."""

from __future__ import annotations

import networkx as nx
import pytest

from src.analysis.bottleneck import BottleneckDetector
from src.analysis.community import CommunityDetector
from src.analysis.recommendations import (
    ExecutiveReport,
    Priority,
    RecommendationEngine,
)
from src.network.centrality import CentralityAnalyzer


class TestRecommendationEngine:
    """Test suite for the recommendation engine."""

    @pytest.fixture()
    def exec_report(self, graph: nx.Graph) -> ExecutiveReport:
        """Run the full recommendation pipeline once."""
        centrality = CentralityAnalyzer().analyze(graph)
        bottleneck = BottleneckDetector().full_report(graph)
        community = CommunityDetector().detect(graph)
        engine = RecommendationEngine(centrality, bottleneck, community)
        return engine.generate()

    def test_generate_returns_executive_report(self, exec_report: ExecutiveReport) -> None:
        """generate must return an ExecutiveReport."""
        assert isinstance(exec_report, ExecutiveReport)

    def test_risk_score_range(self, exec_report: ExecutiveReport) -> None:
        """risk_score must be an integer in [0, 100]."""
        assert isinstance(exec_report.risk_score, int)
        assert 0 <= exec_report.risk_score <= 100

    def test_summary_non_empty(self, exec_report: ExecutiveReport) -> None:
        """Summary must be a non-empty string."""
        assert isinstance(exec_report.summary, str)
        assert len(exec_report.summary) > 0

    def test_recommendation_priorities_valid(self, exec_report: ExecutiveReport) -> None:
        """All recommendation priorities must be valid Priority enum values."""
        for r in exec_report.recommendations:
            assert isinstance(r.priority, Priority)
            assert r.priority in (Priority.HIGH, Priority.MEDIUM, Priority.LOW)

    def test_action_items_are_lists(self, exec_report: ExecutiveReport) -> None:
        """Each recommendation's action_items must be a list of strings."""
        for r in exec_report.recommendations:
            assert isinstance(r.action_items, list)
            for item in r.action_items:
                assert isinstance(item, str)

    def test_high_risk_scenario_produces_high_priority(self) -> None:
        """A star graph with a critical hub should produce HIGH priority recs."""
        # Create a star topology where one node bridges everything
        g = nx.star_graph(20)
        nx.set_node_attributes(g, "Engineering", "department")
        nx.set_edge_attributes(g, 1, "weight")
        # Give the hub node special attributes
        g.nodes[0]["department"] = "Engineering"
        g.nodes[0]["seniority"] = "VP"
        g.nodes[0]["tenure_years"] = 15.0
        for i in range(1, 21):
            g.nodes[i]["seniority"] = "Junior"
            g.nodes[i]["tenure_years"] = 1.0
            # Split departments so hub bridges them
            g.nodes[i]["department"] = "Sales" if i % 2 == 0 else "Engineering"

        centrality = CentralityAnalyzer().analyze(g)
        bottleneck = BottleneckDetector(betweenness_threshold=0.05).full_report(g)
        community = CommunityDetector().detect(g)
        engine = RecommendationEngine(centrality, bottleneck, community)
        report = engine.generate()

        priorities = {r.priority for r in report.recommendations}
        assert Priority.HIGH in priorities

    def test_recommendations_sorted_by_priority(self, exec_report: ExecutiveReport) -> None:
        """Recommendations should be sorted HIGH -> MEDIUM -> LOW."""
        order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
        prev = -1
        for r in exec_report.recommendations:
            cur = order[r.priority]
            assert cur >= prev
            prev = cur
