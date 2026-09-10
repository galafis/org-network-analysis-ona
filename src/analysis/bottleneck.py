"""Bottleneck detection and knowledge risk analysis."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

import networkx as nx
from loguru import logger


class RiskLevel(str, Enum):
    """Risk level classification."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class BottleneckResult:
    """Result for a detected bottleneck node."""

    employee_id: str
    betweenness: float
    degree: int
    departments_connected: int
    risk_level: RiskLevel
    reason: str


@dataclass
class KnowledgeRiskResult:
    """Knowledge loss risk assessment for a node."""

    employee_id: str
    department: str
    seniority: str
    tenure_years: float
    unique_connections: int
    knowledge_score: float
    risk_level: RiskLevel
    replacement_difficulty: str


@dataclass
class BottleneckReport:
    """Complete bottleneck and knowledge risk report."""

    bottlenecks: list[BottleneckResult] = field(default_factory=list)
    knowledge_risks: list[KnowledgeRiskResult] = field(default_factory=list)
    department_silos: list[dict[str, object]] = field(default_factory=list)


class BottleneckDetector:
    """Detect organizational bottlenecks and knowledge concentration risks."""

    def __init__(
        self,
        betweenness_threshold: float = 0.15,
        knowledge_risk_threshold: float = 0.70,
    ) -> None:
        self.betweenness_threshold = betweenness_threshold
        self.knowledge_risk_threshold = knowledge_risk_threshold

    def detect_bottlenecks(self, graph: nx.Graph) -> list[BottleneckResult]:
        """Identify nodes that act as critical bridges."""
        logger.info("Detecting bottlenecks (threshold={})", self.betweenness_threshold)
        betweenness = nx.betweenness_centrality(graph, weight="weight")
        results: list[BottleneckResult] = []

        for node, bet in betweenness.items():
            if bet < self.betweenness_threshold:
                continue

            degree = graph.degree(node)
            neighbor_depts: set[str] = set()
            for nb in graph.neighbors(node):
                neighbor_depts.add(graph.nodes[nb].get("department", "Unknown"))

            n_depts = len(neighbor_depts)
            if bet >= 0.30:
                risk = RiskLevel.CRITICAL
                reason = "Extremely high betweenness: single point of failure"
            elif bet >= 0.20:
                risk = RiskLevel.HIGH
                reason = "High betweenness: critical information broker"
            elif n_depts >= 4:
                risk = RiskLevel.HIGH
                reason = f"Bridges {n_depts} departments: cross-functional bottleneck"
            else:
                risk = RiskLevel.MEDIUM
                reason = "Elevated betweenness: moderate bottleneck risk"

            results.append(
                BottleneckResult(
                    employee_id=str(node),
                    betweenness=round(bet, 6),
                    degree=degree,
                    departments_connected=n_depts,
                    risk_level=risk,
                    reason=reason,
                )
            )

        results.sort(key=lambda x: x.betweenness, reverse=True)
        logger.info("Found {} bottlenecks", len(results))
        return results

    def assess_knowledge_risk(self, graph: nx.Graph) -> list[KnowledgeRiskResult]:
        """Assess knowledge loss risk for each node."""
        logger.info("Assessing knowledge loss risk")
        betweenness = nx.betweenness_centrality(graph, weight="weight")
        seniority_weights = {
            "Junior": 0.2,
            "Mid": 0.4,
            "Senior": 0.6,
            "Lead": 0.8,
            "Director": 0.9,
            "VP": 1.0,
        }
        max_degree = max((d for _, d in graph.degree()), default=1)
        results: list[KnowledgeRiskResult] = []

        for node in graph.nodes():
            attrs = graph.nodes[node]
            seniority = attrs.get("seniority", "Mid")
            tenure = float(attrs.get("tenure_years", 1.0))
            department = attrs.get("department", "Unknown")
            degree = graph.degree(node)

            neighbors = list(graph.neighbors(node))
            unique = 0
            for nb in neighbors:
                nb_neighbors = set(graph.neighbors(nb))
                if len((set(neighbors) - {nb}) & nb_neighbors) == 0:
                    unique += 1

            seniority_w = seniority_weights.get(seniority, 0.4)
            tenure_w = min(tenure / 15.0, 1.0)
            connectivity_w = degree / max_degree if max_degree > 0 else 0.0
            betweenness_w = min(betweenness.get(node, 0.0) / 0.3, 1.0)

            knowledge_score = round(
                0.25 * seniority_w
                + 0.25 * tenure_w
                + 0.25 * connectivity_w
                + 0.25 * betweenness_w,
                4,
            )

            if knowledge_score >= 0.80:
                risk, difficulty = RiskLevel.CRITICAL, "Very High: 6-12 months"
            elif knowledge_score >= self.knowledge_risk_threshold:
                risk, difficulty = RiskLevel.HIGH, "High: 3-6 months"
            elif knowledge_score >= 0.50:
                risk, difficulty = RiskLevel.MEDIUM, "Medium: 1-3 months"
            else:
                risk, difficulty = RiskLevel.LOW, "Low: standard timeline"

            results.append(
                KnowledgeRiskResult(
                    employee_id=str(node),
                    department=department,
                    seniority=seniority,
                    tenure_years=tenure,
                    unique_connections=unique,
                    knowledge_score=knowledge_score,
                    risk_level=risk,
                    replacement_difficulty=difficulty,
                )
            )

        results.sort(key=lambda x: x.knowledge_score, reverse=True)
        return results

    def detect_department_silos(self, graph: nx.Graph) -> list[dict[str, object]]:
        """Detect departments that are poorly connected to others."""
        departments: dict[str, list[str]] = {}
        for node, data in graph.nodes(data=True):
            departments.setdefault(data.get("department", "Unknown"), []).append(node)

        silos: list[dict[str, object]] = []
        for dept, nodes in departments.items():
            internal = graph.subgraph(nodes).number_of_edges()
            external = sum(1 for n in nodes for nb in graph.neighbors(n) if nb not in nodes)
            total = internal + external
            ratio = round(internal / total if total > 0 else 1.0, 4)
            silos.append(
                {
                    "department": dept,
                    "n_employees": len(nodes),
                    "internal_edges": internal,
                    "external_edges": external,
                    "isolation_ratio": ratio,
                    "is_silo": ratio > 0.80,
                }
            )
        silos.sort(key=lambda x: float(str(x["isolation_ratio"])), reverse=True)
        return silos

    def full_report(self, graph: nx.Graph) -> BottleneckReport:
        """Generate complete bottleneck and risk analysis."""
        return BottleneckReport(
            bottlenecks=self.detect_bottlenecks(graph),
            knowledge_risks=self.assess_knowledge_risk(graph),
            department_silos=self.detect_department_silos(graph),
        )
