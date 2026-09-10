"""Centrality metrics computation for organizational networks."""

from __future__ import annotations

from dataclasses import dataclass, field

import networkx as nx
import pandas as pd
from loguru import logger


@dataclass
class CentralityResult:
    """Centrality scores for a single node."""

    employee_id: str
    degree: float
    betweenness: float
    closeness: float
    eigenvector: float
    pagerank: float
    composite_score: float = 0.0


@dataclass
class CentralityReport:
    """Complete centrality analysis report."""

    results: list[CentralityResult] = field(default_factory=list)
    top_connectors: list[str] = field(default_factory=list)
    top_brokers: list[str] = field(default_factory=list)
    top_influencers: list[str] = field(default_factory=list)


class CentralityAnalyzer:
    """Compute and analyze centrality metrics."""

    def __init__(self, top_k: int = 10) -> None:
        self.top_k = top_k

    def analyze(self, graph: nx.Graph) -> CentralityReport:
        """Compute all centrality metrics for the graph."""
        n = graph.number_of_nodes()
        if n == 0:
            return CentralityReport()

        logger.info("Computing centrality metrics for {} nodes", n)

        degree_c = nx.degree_centrality(graph)
        betweenness_c = nx.betweenness_centrality(graph, weight="weight")
        closeness_c = nx.closeness_centrality(graph)

        try:
            eigenvector_c = nx.eigenvector_centrality_numpy(graph, weight="weight")
        except Exception:
            eigenvector_c = {node: 0.0 for node in graph.nodes()}

        pagerank_c = nx.pagerank(graph, weight="weight")

        results: list[CentralityResult] = []
        for node in graph.nodes():
            deg = round(degree_c.get(node, 0.0), 6)
            bet = round(betweenness_c.get(node, 0.0), 6)
            clo = round(closeness_c.get(node, 0.0), 6)
            eig = round(eigenvector_c.get(node, 0.0), 6)
            pr = round(pagerank_c.get(node, 0.0), 6)

            # Composite: weighted average of normalized scores
            composite = round(0.25 * deg + 0.30 * bet + 0.15 * clo + 0.15 * eig + 0.15 * pr, 6)

            results.append(
                CentralityResult(
                    employee_id=str(node),
                    degree=deg,
                    betweenness=bet,
                    closeness=clo,
                    eigenvector=eig,
                    pagerank=pr,
                    composite_score=composite,
                )
            )

        results.sort(key=lambda x: x.composite_score, reverse=True)

        top_connectors = sorted(results, key=lambda x: x.degree, reverse=True)
        top_brokers = sorted(results, key=lambda x: x.betweenness, reverse=True)
        top_influencers = sorted(results, key=lambda x: x.eigenvector, reverse=True)

        report = CentralityReport(
            results=results,
            top_connectors=[r.employee_id for r in top_connectors[: self.top_k]],
            top_brokers=[r.employee_id for r in top_brokers[: self.top_k]],
            top_influencers=[r.employee_id for r in top_influencers[: self.top_k]],
        )

        logger.info(
            "Centrality analysis complete: {} nodes analyzed",
            len(results),
        )
        return report

    def get_centrality_dataframe(self, report: CentralityReport) -> pd.DataFrame:
        """Convert centrality results to a DataFrame."""

        rows = [
            {
                "employee_id": r.employee_id,
                "degree": r.degree,
                "betweenness": r.betweenness,
                "closeness": r.closeness,
                "eigenvector": r.eigenvector,
                "pagerank": r.pagerank,
                "composite_score": r.composite_score,
            }
            for r in report.results
        ]
        return pd.DataFrame(rows)
