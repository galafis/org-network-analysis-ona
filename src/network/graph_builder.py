"""Build and manage organizational network graphs."""

from __future__ import annotations

from dataclasses import dataclass

import networkx as nx
import numpy as np
import pandas as pd
from loguru import logger


@dataclass
class GraphStats:
    """Summary statistics for a network graph."""

    n_nodes: int
    n_edges: int
    density: float
    avg_clustering: float
    n_connected_components: int
    avg_degree: float
    diameter: int | None = None


class OrgGraphBuilder:
    """Build organizational network graphs from interaction data."""

    def __init__(self) -> None:
        self.graph: nx.Graph = nx.Graph()
        self.directed_graph: nx.DiGraph = nx.DiGraph()

    @staticmethod
    def _validate_inputs(interactions: pd.DataFrame, employees: pd.DataFrame) -> pd.DataFrame:
        if "employee_id" not in employees or not {"source_id", "target_id", "weight"} <= set(
            interactions
        ):
            raise ValueError("Missing required columns / colunas obrigatórias ausentes")
        ids = employees["employee_id"]
        if ids.isna().any() or ids.astype(str).duplicated().any():
            raise ValueError("Employee IDs must be unique and non-null / IDs únicos e preenchidos")
        df = interactions.copy()
        for col in ("source_id", "target_id"):
            if df[col].isna().any() or not set(df[col].astype(str)) <= set(ids.astype(str)):
                raise ValueError("Unknown interaction endpoint / participante desconhecido")
            df[col] = df[col].astype(str)
        try:
            weights = pd.to_numeric(df["weight"], errors="raise")
        except (TypeError, ValueError) as exc:
            raise ValueError("Weights must be numeric / pesos devem ser numéricos") from exc
        if not np.isfinite(weights).all() or (weights <= 0).any():
            raise ValueError("Weights must be finite and positive / pesos finitos e positivos")
        if (df["source_id"] == df["target_id"]).any():
            raise ValueError(
                "Self interactions are not supported / auto-interações não são aceitas"
            )
        df["weight"] = weights
        return df

    def build_from_interactions(
        self,
        interactions_df: pd.DataFrame,
        employees_df: pd.DataFrame,
        month: int | None = None,
        channel: str | None = None,
    ) -> nx.Graph:
        """Build undirected weighted graph from interactions."""
        df = self._validate_inputs(interactions_df, employees_df)
        if month is not None:
            df = df[df["month"] == month]
        if channel is not None:
            df = df[df["channel"] == channel]

        # Aggregate weights
        agg = df.groupby(["source_id", "target_id"])["weight"].sum().reset_index()

        self.graph = nx.Graph()

        # Add all employees as nodes with attributes
        emp_attrs = employees_df.set_index("employee_id").to_dict("index")
        for emp_id, attrs in emp_attrs.items():
            self.graph.add_node(str(emp_id), **{str(key): value for key, value in attrs.items()})

        # Add edges
        for _, row in agg.iterrows():
            src = str(row["source_id"])
            tgt = str(row["target_id"])
            w = float(row["weight"])
            if self.graph.has_edge(src, tgt):
                self.graph[src][tgt]["weight"] += w
            else:
                self.graph.add_edge(src, tgt, weight=w)

        logger.info(
            "Graph built: {} nodes, {} edges",
            self.graph.number_of_nodes(),
            self.graph.number_of_edges(),
        )
        return self.graph

    def build_directed(
        self,
        interactions_df: pd.DataFrame,
        employees_df: pd.DataFrame,
        month: int | None = None,
    ) -> nx.DiGraph:
        """Build directed weighted graph."""
        df = self._validate_inputs(interactions_df, employees_df)
        if month is not None:
            df = df[df["month"] == month]

        agg = df.groupby(["source_id", "target_id"])["weight"].sum().reset_index()

        self.directed_graph = nx.DiGraph()
        emp_attrs = employees_df.set_index("employee_id").to_dict("index")
        for emp_id, attrs in emp_attrs.items():
            self.directed_graph.add_node(
                str(emp_id), **{str(key): value for key, value in attrs.items()}
            )

        for _, row in agg.iterrows():
            src = str(row["source_id"])
            tgt = str(row["target_id"])
            w = float(row["weight"])
            self.directed_graph.add_edge(src, tgt, weight=w)

        return self.directed_graph

    def get_stats(self, graph: nx.Graph | None = None) -> GraphStats:
        """Compute summary statistics for the graph."""
        g = self.graph if graph is None else graph
        n_nodes = g.number_of_nodes()
        n_edges = g.number_of_edges()
        density = round(nx.density(g), 6) if n_nodes > 1 else 0.0
        avg_clust = (
            round(float(nx.average_clustering(g, weight="weight")), 4) if n_nodes > 0 else 0.0
        )

        if isinstance(g, nx.DiGraph):
            components = nx.number_weakly_connected_components(g)
        else:
            components = nx.number_connected_components(g)

        degrees = [d for _, d in g.degree()]
        avg_deg = round(float(np.mean(degrees)), 2) if degrees else 0.0

        # Diameter only for connected graphs
        diameter: int | None = None
        if n_nodes > 1 and components == 1 and not isinstance(g, nx.DiGraph):
            diameter = nx.diameter(g)

        return GraphStats(
            n_nodes=n_nodes,
            n_edges=n_edges,
            density=density,
            avg_clustering=avg_clust,
            n_connected_components=components,
            avg_degree=avg_deg,
            diameter=diameter,
        )

    def filter_by_department(self, department: str) -> nx.Graph:
        """Return subgraph for a specific department."""
        nodes = [n for n, d in self.graph.nodes(data=True) if d.get("department") == department]
        subgraph: nx.Graph = self.graph.subgraph(nodes).copy()
        return subgraph

    def get_cross_department_edges(self) -> list[tuple[str, str, dict[str, object]]]:
        """Return edges that connect different departments."""
        cross: list[tuple[str, str, dict[str, object]]] = []
        for u, v, data in self.graph.edges(data=True):
            dept_u = self.graph.nodes[u].get("department", "")
            dept_v = self.graph.nodes[v].get("department", "")
            if dept_u != dept_v:
                cross.append((u, v, dict(data)))
        return cross
