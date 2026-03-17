"""Tests for CommunityDetector."""

from __future__ import annotations

import networkx as nx

from src.analysis.community import CommunityDetector, CommunityReport


class TestCommunityDetector:
    """Test suite for Louvain community detection."""

    def test_detect_returns_report(self, graph: nx.Graph) -> None:
        """detect must return a CommunityReport."""
        detector = CommunityDetector()
        report = detector.detect(graph)
        assert isinstance(report, CommunityReport)

    def test_n_communities_positive(self, graph: nx.Graph) -> None:
        """A non-empty graph must have at least one community."""
        detector = CommunityDetector()
        report = detector.detect(graph)
        assert report.n_communities > 0

    def test_modularity_is_float(self, graph: nx.Graph) -> None:
        """Modularity must be a float."""
        detector = CommunityDetector()
        report = detector.detect(graph)
        assert isinstance(report.modularity, float)

    def test_community_has_members(self, graph: nx.Graph) -> None:
        """Each community must have a non-empty members list."""
        detector = CommunityDetector()
        report = detector.detect(graph)
        for c in report.communities:
            assert isinstance(c.members, list)
            assert len(c.members) > 0
            assert c.size == len(c.members)

    def test_empty_graph_returns_empty_report(self) -> None:
        """Detecting communities on an empty graph must return an empty report."""
        detector = CommunityDetector()
        report = detector.detect(nx.Graph())
        assert isinstance(report, CommunityReport)
        assert report.n_communities == 0
        assert report.communities == []

    def test_all_nodes_assigned(self, graph: nx.Graph) -> None:
        """Every graph node must appear in exactly one community."""
        detector = CommunityDetector()
        report = detector.detect(graph)
        all_members = []
        for c in report.communities:
            all_members.extend(c.members)
        assert set(all_members) == set(graph.nodes())
        assert len(all_members) == graph.number_of_nodes()
