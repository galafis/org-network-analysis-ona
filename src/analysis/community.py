"""Community detection using Louvain algorithm."""

from __future__ import annotations

from dataclasses import dataclass, field

import networkx as nx
from loguru import logger


@dataclass
class CommunityInfo:
    """Information about a single detected community."""

    community_id: int
    members: list[str]
    size: int
    departments: dict[str, int]
    dominant_department: str
    cross_department: bool


@dataclass
class CommunityReport:
    """Complete community detection report."""

    n_communities: int = 0
    modularity: float = 0.0
    communities: list[CommunityInfo] = field(default_factory=list)


class CommunityDetector:
    """Detect communities in organizational networks using Louvain."""

    def __init__(self, resolution: float = 1.0) -> None:
        self.resolution = resolution

    def detect(self, graph: nx.Graph) -> CommunityReport:
        """Run Louvain community detection and build report."""
        if graph.number_of_nodes() == 0:
            return CommunityReport()

        logger.info(
            "Running Louvain community detection (resolution={})",
            self.resolution,
        )

        partitions: list[set[str]] = nx.community.louvain_communities(
            graph,
            resolution=self.resolution,
            seed=42,
        )

        modularity = nx.community.modularity(graph, partitions)

        communities: list[CommunityInfo] = []
        for idx, members_set in enumerate(partitions):
            members = sorted(members_set)
            departments: dict[str, int] = {}
            for node in members:
                dept = graph.nodes[node].get("department", "Unknown")
                departments[dept] = departments.get(dept, 0) + 1

            dominant_department = max(departments, key=departments.get)  # type: ignore[arg-type]
            cross_department = len(departments) > 1

            communities.append(
                CommunityInfo(
                    community_id=idx,
                    members=members,
                    size=len(members),
                    departments=departments,
                    dominant_department=dominant_department,
                    cross_department=cross_department,
                )
            )

        communities.sort(key=lambda c: c.size, reverse=True)

        report = CommunityReport(
            n_communities=len(communities),
            modularity=round(modularity, 4),
            communities=communities,
        )

        logger.info(
            "Detected {} communities (modularity={:.4f})",
            report.n_communities,
            report.modularity,
        )
        return report
