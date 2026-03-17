"""Orchestrate full organizational network analysis pipeline."""

from __future__ import annotations

from dataclasses import dataclass

import networkx as nx
from loguru import logger

from src.analysis.bottleneck import BottleneckDetector, BottleneckReport
from src.analysis.community import CommunityDetector, CommunityReport
from src.analysis.recommendations import ExecutiveReport, RecommendationEngine
from src.network.centrality import CentralityAnalyzer, CentralityReport
from src.network.graph_builder import GraphStats, OrgGraphBuilder


@dataclass
class FullAnalysisResult:
    """Container for all analysis outputs."""

    graph_stats: GraphStats
    centrality: CentralityReport
    bottleneck: BottleneckReport
    community: CommunityReport
    recommendations: ExecutiveReport


def run_full_analysis(
    graph: nx.Graph,
    betweenness_threshold: float = 0.15,
    knowledge_risk_threshold: float = 0.70,
    community_resolution: float = 1.0,
) -> FullAnalysisResult:
    """Run the complete analysis pipeline on an organizational graph.

    Parameters
    ----------
    graph:
        NetworkX undirected graph with employee attributes.
    betweenness_threshold:
        Minimum betweenness centrality to flag as bottleneck.
    knowledge_risk_threshold:
        Minimum knowledge score to flag as high risk.
    community_resolution:
        Resolution parameter for Louvain community detection.

    Returns
    -------
    FullAnalysisResult with all analysis components.
    """
    logger.info("Starting full ONA pipeline")

    # Graph statistics
    builder = OrgGraphBuilder()
    graph_stats = builder.get_stats(graph)
    logger.info("Graph stats: {} nodes, {} edges", graph_stats.n_nodes, graph_stats.n_edges)

    # Centrality analysis
    centrality_analyzer = CentralityAnalyzer()
    centrality_report = centrality_analyzer.analyze(graph)

    # Bottleneck detection
    bottleneck_detector = BottleneckDetector(
        betweenness_threshold=betweenness_threshold,
        knowledge_risk_threshold=knowledge_risk_threshold,
    )
    bottleneck_report = bottleneck_detector.full_report(graph)

    # Community detection
    community_detector = CommunityDetector(resolution=community_resolution)
    community_report = community_detector.detect(graph)

    # Recommendations
    engine = RecommendationEngine(
        centrality_report=centrality_report,
        bottleneck_report=bottleneck_report,
        community_report=community_report,
    )
    executive_report = engine.generate()

    result = FullAnalysisResult(
        graph_stats=graph_stats,
        centrality=centrality_report,
        bottleneck=bottleneck_report,
        community=community_report,
        recommendations=executive_report,
    )

    logger.info("Full ONA pipeline complete (risk_score={})", executive_report.risk_score)
    return result
