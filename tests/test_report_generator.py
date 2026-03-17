"""Tests for the JSON report generator."""

from __future__ import annotations

import json
from pathlib import Path

import networkx as nx
import pytest

from src.analysis.runner import run_full_analysis
from src.reporting.report_generator import generate_json_report


class TestReportGenerator:
    """Test suite for generate_json_report."""

    @pytest.fixture()
    def analysis_result(self, graph: nx.Graph):
        """Run full analysis to get a FullAnalysisResult."""
        return run_full_analysis(graph)

    def test_generate_json_report_returns_dict(self, analysis_result) -> None:
        """generate_json_report must return a dictionary."""
        report = generate_json_report(analysis_result)
        assert isinstance(report, dict)

    def test_dict_has_all_required_keys(self, analysis_result) -> None:
        """Report dict must contain all top-level keys."""
        report = generate_json_report(analysis_result)
        required_keys = {
            "graph_stats", "centrality", "bottleneck",
            "community", "recommendations",
        }
        assert required_keys.issubset(set(report.keys()))

    def test_bottleneck_risk_level_is_string(self, analysis_result) -> None:
        """Serialized bottleneck risk_level must be a plain string, not enum."""
        report = generate_json_report(analysis_result)
        for b in report["bottleneck"]["bottlenecks"]:
            assert isinstance(b["risk_level"], str)
            assert b["risk_level"] in ("low", "medium", "high", "critical")

    def test_recommendation_priority_is_string(self, analysis_result) -> None:
        """Serialized recommendation priority must be a plain string, not enum."""
        report = generate_json_report(analysis_result)
        for r in report["recommendations"]["recommendations"]:
            assert isinstance(r["priority"], str)
            assert r["priority"] in ("low", "medium", "high")

    def test_writes_to_file(self, analysis_result, tmp_path: Path) -> None:
        """When output_path is provided, report must be written as JSON."""
        out = tmp_path / "report.json"
        report = generate_json_report(analysis_result, output_path=out)
        assert out.exists()
        loaded = json.loads(out.read_text(encoding="utf-8"))
        assert loaded["graph_stats"]["n_nodes"] == report["graph_stats"]["n_nodes"]

    def test_graph_stats_fields(self, analysis_result) -> None:
        """graph_stats section must contain expected metric fields."""
        report = generate_json_report(analysis_result)
        stats = report["graph_stats"]
        assert "n_nodes" in stats
        assert "n_edges" in stats
        assert "density" in stats
        assert "avg_degree" in stats
