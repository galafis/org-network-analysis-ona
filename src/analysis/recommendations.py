"""Recommendation engine for organizational network improvements."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from loguru import logger

from src.analysis.bottleneck import BottleneckReport, RiskLevel
from src.analysis.community import CommunityReport
from src.network.centrality import CentralityReport


class Priority(str, Enum):
    """Recommendation priority level."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Recommendation:
    """A single actionable recommendation."""

    priority: Priority
    category: str
    title: str
    description: str
    action_items: list[str] = field(default_factory=list)


@dataclass
class ExecutiveReport:
    """Executive-level summary with recommendations."""

    recommendations: list[Recommendation] = field(default_factory=list)
    summary: str = ""
    risk_score: int = 0


class RecommendationEngine:
    """Generate actionable recommendations from analysis results."""

    def __init__(
        self,
        centrality_report: CentralityReport,
        bottleneck_report: BottleneckReport,
        community_report: CommunityReport,
    ) -> None:
        self.centrality = centrality_report
        self.bottleneck = bottleneck_report
        self.community = community_report

    def generate(self) -> ExecutiveReport:
        """Generate full executive report with recommendations."""
        logger.info("Generating executive recommendations")
        recommendations: list[Recommendation] = []

        recommendations.extend(self._check_bottleneck_risk())
        recommendations.extend(self._check_knowledge_risk())
        recommendations.extend(self._check_silo_detection())
        recommendations.extend(self._check_high_modularity())
        recommendations.extend(self._check_key_person_overlap())

        recommendations.sort(
            key=lambda r: (
                {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}[r.priority]
            ),
        )

        risk_score = self._compute_risk_score()
        summary = self._build_summary(recommendations, risk_score)

        report = ExecutiveReport(
            recommendations=recommendations,
            summary=summary,
            risk_score=risk_score,
        )
        logger.info(
            "Generated {} recommendations (risk_score={})",
            len(recommendations),
            risk_score,
        )
        return report

    def _check_bottleneck_risk(self) -> list[Recommendation]:
        """Check for critical bottleneck nodes."""
        results: list[Recommendation] = []
        critical = [
            b for b in self.bottleneck.bottlenecks
            if b.risk_level in (RiskLevel.CRITICAL, RiskLevel.HIGH)
        ]
        if not critical:
            return results

        ids = [b.employee_id for b in critical[:5]]
        results.append(
            Recommendation(
                priority=Priority.HIGH,
                category="Bottleneck Risk",
                title="Critical communication bottlenecks detected",
                description=(
                    f"{len(critical)} employee(s) act as critical information "
                    "bridges. Their absence would severely disrupt communication flow."
                ),
                action_items=[
                    f"Create redundant communication paths around {', '.join(ids)}",
                    "Cross-train team members to reduce single-point-of-failure risk",
                    "Establish shared channels for cross-departmental communication",
                ],
            )
        )
        return results

    def _check_knowledge_risk(self) -> list[Recommendation]:
        """Check for knowledge concentration risk."""
        results: list[Recommendation] = []
        high_risk = [
            k for k in self.bottleneck.knowledge_risks
            if k.risk_level in (RiskLevel.CRITICAL, RiskLevel.HIGH)
        ]
        if not high_risk:
            return results

        top = high_risk[:5]
        depts = {k.department for k in top}
        results.append(
            Recommendation(
                priority=Priority.HIGH,
                category="Knowledge Risk",
                title="High knowledge concentration detected",
                description=(
                    f"{len(high_risk)} employee(s) hold disproportionate "
                    f"institutional knowledge, concentrated in {', '.join(sorted(depts))}."
                ),
                action_items=[
                    "Implement knowledge-sharing sessions and documentation sprints",
                    "Create mentorship programs pairing high-risk holders with successors",
                    "Develop onboarding materials capturing tacit knowledge",
                ],
            )
        )
        return results

    def _check_silo_detection(self) -> list[Recommendation]:
        """Check for departmental silos."""
        results: list[Recommendation] = []
        silos = [
            s for s in self.bottleneck.department_silos
            if s.get("is_silo") is True
        ]
        if not silos:
            return results

        dept_names = [str(s["department"]) for s in silos]
        results.append(
            Recommendation(
                priority=Priority.MEDIUM,
                category="Silo Detection",
                title="Department silos identified",
                description=(
                    f"{len(silos)} department(s) show high internal isolation: "
                    f"{', '.join(dept_names)}. Limited cross-team collaboration "
                    "may hinder innovation."
                ),
                action_items=[
                    "Launch cross-functional project teams involving siloed departments",
                    "Create inter-departmental communication channels",
                    "Schedule regular cross-team knowledge sharing events",
                ],
            )
        )
        return results

    def _check_high_modularity(self) -> list[Recommendation]:
        """Check for excessively high modularity indicating fragmentation."""
        results: list[Recommendation] = []
        if self.community.modularity < 0.6:
            return results

        results.append(
            Recommendation(
                priority=Priority.MEDIUM,
                category="Network Fragmentation",
                title="High network modularity indicates fragmentation",
                description=(
                    f"Network modularity of {self.community.modularity:.2f} suggests "
                    "the organization is highly fragmented into distinct clusters "
                    "with limited inter-group interaction."
                ),
                action_items=[
                    "Identify and strengthen weak inter-community links",
                    "Assign cross-community liaisons for key projects",
                    "Consider organizational restructuring for better collaboration",
                ],
            )
        )
        return results

    def _check_key_person_overlap(self) -> list[Recommendation]:
        """Check for key persons appearing across multiple risk categories."""
        results: list[Recommendation] = []
        broker_set = set(self.centrality.top_brokers[:5])
        bottleneck_set = {b.employee_id for b in self.bottleneck.bottlenecks[:5]}
        knowledge_set = {
            k.employee_id
            for k in self.bottleneck.knowledge_risks[:5]
            if k.risk_level in (RiskLevel.CRITICAL, RiskLevel.HIGH)
        }

        overlap = broker_set & bottleneck_set
        triple_overlap = overlap & knowledge_set

        if triple_overlap:
            results.append(
                Recommendation(
                    priority=Priority.HIGH,
                    category="Key Person Risk",
                    title="Critical key-person dependency detected",
                    description=(
                        f"{len(triple_overlap)} employee(s) appear as top brokers, "
                        "bottlenecks, and knowledge risk holders simultaneously: "
                        f"{', '.join(sorted(triple_overlap))}."
                    ),
                    action_items=[
                        "Immediate succession planning for identified individuals",
                        "Distribute their responsibilities across multiple team members",
                        "Document all critical processes these individuals manage",
                    ],
                )
            )
        elif overlap:
            results.append(
                Recommendation(
                    priority=Priority.MEDIUM,
                    category="Key Person Risk",
                    title="Key-person overlap in broker and bottleneck roles",
                    description=(
                        f"{len(overlap)} employee(s) serve as both top brokers and "
                        f"bottlenecks: {', '.join(sorted(overlap))}."
                    ),
                    action_items=[
                        "Develop backup communication pathways",
                        "Cross-train colleagues on bridging responsibilities",
                    ],
                )
            )
        return results

    def _compute_risk_score(self) -> int:
        """Compute overall organizational risk score (0-100)."""
        score = 0.0

        # Bottleneck contribution (up to 30)
        critical_bottlenecks = sum(
            1 for b in self.bottleneck.bottlenecks
            if b.risk_level in (RiskLevel.CRITICAL, RiskLevel.HIGH)
        )
        score += min(critical_bottlenecks * 6.0, 30.0)

        # Knowledge risk contribution (up to 30)
        critical_knowledge = sum(
            1 for k in self.bottleneck.knowledge_risks
            if k.risk_level in (RiskLevel.CRITICAL, RiskLevel.HIGH)
        )
        total_nodes = len(self.bottleneck.knowledge_risks) or 1
        knowledge_ratio = critical_knowledge / total_nodes
        score += knowledge_ratio * 30.0

        # Silo contribution (up to 20)
        silo_count = sum(
            1 for s in self.bottleneck.department_silos
            if s.get("is_silo") is True
        )
        total_depts = len(self.bottleneck.department_silos) or 1
        score += (silo_count / total_depts) * 20.0

        # Modularity contribution (up to 20)
        if self.community.modularity > 0.4:
            score += min((self.community.modularity - 0.4) * 33.3, 20.0)

        return min(int(round(score)), 100)

    @staticmethod
    def _build_summary(
        recommendations: list[Recommendation],
        risk_score: int,
    ) -> str:
        """Build executive summary text."""
        high_count = sum(1 for r in recommendations if r.priority == Priority.HIGH)
        medium_count = sum(1 for r in recommendations if r.priority == Priority.MEDIUM)
        low_count = sum(1 for r in recommendations if r.priority == Priority.LOW)

        if risk_score >= 70:
            risk_label = "Critical"
        elif risk_score >= 40:
            risk_label = "Elevated"
        else:
            risk_label = "Moderate"

        return (
            f"Organizational Risk Score: {risk_score}/100 ({risk_label}). "
            f"Generated {len(recommendations)} recommendation(s): "
            f"{high_count} high, {medium_count} medium, {low_count} low priority."
        )
