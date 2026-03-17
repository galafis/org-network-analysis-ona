"""Tests for BottleneckDetector."""

from __future__ import annotations

import networkx as nx

from src.analysis.bottleneck import (
    BottleneckDetector,
    BottleneckReport,
    BottleneckResult,
    KnowledgeRiskResult,
    RiskLevel,
)


class TestBottleneckDetector:
    """Test suite for bottleneck detection and knowledge risk analysis."""

    def test_detect_bottlenecks_returns_list(self, graph: nx.Graph) -> None:
        """detect_bottlenecks must return a list."""
        detector = BottleneckDetector()
        results = detector.detect_bottlenecks(graph)
        assert isinstance(results, list)

    def test_bottleneck_has_required_fields(self, graph: nx.Graph) -> None:
        """Each BottleneckResult must have the expected attributes."""
        detector = BottleneckDetector(betweenness_threshold=0.01)
        results = detector.detect_bottlenecks(graph)
        if results:
            b = results[0]
            assert isinstance(b, BottleneckResult)
            assert hasattr(b, "employee_id")
            assert hasattr(b, "betweenness")
            assert hasattr(b, "degree")
            assert hasattr(b, "departments_connected")
            assert hasattr(b, "risk_level")
            assert hasattr(b, "reason")

    def test_risk_levels_are_valid_enum(self, graph: nx.Graph) -> None:
        """risk_level values must be valid RiskLevel enum members."""
        detector = BottleneckDetector(betweenness_threshold=0.01)
        results = detector.detect_bottlenecks(graph)
        for b in results:
            assert isinstance(b.risk_level, RiskLevel)
            assert b.risk_level in (
                RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL
            )

    def test_assess_knowledge_risk_returns_all_nodes(self, graph: nx.Graph) -> None:
        """assess_knowledge_risk must return a result for every node."""
        detector = BottleneckDetector()
        results = detector.assess_knowledge_risk(graph)
        assert isinstance(results, list)
        assert len(results) == graph.number_of_nodes()

    def test_knowledge_score_range(self, graph: nx.Graph) -> None:
        """knowledge_score must be a float in [0, 1]."""
        detector = BottleneckDetector()
        results = detector.assess_knowledge_risk(graph)
        for k in results:
            assert isinstance(k, KnowledgeRiskResult)
            assert isinstance(k.knowledge_score, float)
            assert 0.0 <= k.knowledge_score <= 1.0

    def test_detect_department_silos_has_isolation_ratio(
        self, graph: nx.Graph
    ) -> None:
        """Each silo dict must include an isolation_ratio key."""
        detector = BottleneckDetector()
        silos = detector.detect_department_silos(graph)
        assert isinstance(silos, list)
        assert len(silos) > 0
        for s in silos:
            assert "isolation_ratio" in s
            assert 0.0 <= float(str(s["isolation_ratio"])) <= 1.0

    def test_full_report_returns_bottleneck_report(self, graph: nx.Graph) -> None:
        """full_report must return a BottleneckReport with all sections."""
        detector = BottleneckDetector()
        report = detector.full_report(graph)
        assert isinstance(report, BottleneckReport)
        assert isinstance(report.bottlenecks, list)
        assert isinstance(report.knowledge_risks, list)
        assert isinstance(report.department_silos, list)

    def test_small_graph_bottleneck_detection(self, small_graph: nx.Graph) -> None:
        """EMP-0001 in small_graph bridges both departments; should be detected."""
        detector = BottleneckDetector(betweenness_threshold=0.1)
        results = detector.detect_bottlenecks(small_graph)
        detected_ids = {b.employee_id for b in results}
        assert "EMP-0001" in detected_ids

    def test_empty_graph_no_bottlenecks(self) -> None:
        """An empty graph should produce no bottlenecks."""
        detector = BottleneckDetector()
        results = detector.detect_bottlenecks(nx.Graph())
        assert results == []
