"""Generate JSON reports from analysis results."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from loguru import logger

from src.analysis.bottleneck import BottleneckResult, KnowledgeRiskResult
from src.analysis.recommendations import Recommendation
from src.analysis.runner import FullAnalysisResult


def generate_json_report(
    result: FullAnalysisResult,
    output_path: Path | None = None,
) -> dict[str, Any]:
    """Serialize full analysis result to a JSON-compatible dict.

    Parameters
    ----------
    result:
        Complete analysis output from ``run_full_analysis``.
    output_path:
        Optional file path to write the JSON report.

    Returns
    -------
    Dictionary with all analysis results serialized.
    """
    logger.info("Generating JSON report")

    report: dict[str, Any] = {
        "graph_stats": asdict(result.graph_stats),
        "centrality": {
            "results": [asdict(r) for r in result.centrality.results],
            "top_connectors": result.centrality.top_connectors,
            "top_brokers": result.centrality.top_brokers,
            "top_influencers": result.centrality.top_influencers,
        },
        "bottleneck": {
            "bottlenecks": [_serialize_bottleneck(b) for b in result.bottleneck.bottlenecks],
            "knowledge_risks": [
                _serialize_knowledge_risk(k) for k in result.bottleneck.knowledge_risks
            ],
            "department_silos": result.bottleneck.department_silos,
        },
        "community": {
            "n_communities": result.community.n_communities,
            "modularity": result.community.modularity,
            "communities": [asdict(c) for c in result.community.communities],
        },
        "recommendations": {
            "risk_score": result.recommendations.risk_score,
            "summary": result.recommendations.summary,
            "recommendations": [
                _serialize_recommendation(r) for r in result.recommendations.recommendations
            ],
        },
    }

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))
        logger.info("Report written to {}", output_path)

    return report


def _serialize_bottleneck(b: BottleneckResult) -> dict[str, Any]:
    """Serialize a BottleneckResult, converting enums to strings."""
    data: dict[str, Any] = asdict(b)
    if hasattr(data["risk_level"], "value"):
        data["risk_level"] = data["risk_level"].value
    else:
        data["risk_level"] = str(data["risk_level"])
    return data


def _serialize_knowledge_risk(k: KnowledgeRiskResult) -> dict[str, Any]:
    """Serialize a KnowledgeRiskResult, converting enums to strings."""
    data: dict[str, Any] = asdict(k)
    if hasattr(data["risk_level"], "value"):
        data["risk_level"] = data["risk_level"].value
    else:
        data["risk_level"] = str(data["risk_level"])
    return data


def _serialize_recommendation(r: Recommendation) -> dict[str, Any]:
    """Serialize a Recommendation, converting enums to strings."""
    data: dict[str, Any] = asdict(r)  # type: ignore[arg-type]
    if hasattr(data["priority"], "value"):
        data["priority"] = data["priority"].value
    else:
        data["priority"] = str(data["priority"])
    return data
