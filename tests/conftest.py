"""Shared test fixtures for ONA test suite."""

from __future__ import annotations

import networkx as nx
import pandas as pd
import pytest

from src.data.generator import ONADataGenerator
from src.network.graph_builder import OrgGraphBuilder


@pytest.fixture(scope="session")
def generator() -> ONADataGenerator:
    """Create a small data generator for tests."""
    return ONADataGenerator(n_employees=50, n_months=2, seed=99)


@pytest.fixture(scope="session")
def employees_df(generator: ONADataGenerator) -> pd.DataFrame:
    return generator.generate_employees()


@pytest.fixture(scope="session")
def interactions_df(
    generator: ONADataGenerator, employees_df: pd.DataFrame
) -> pd.DataFrame:
    return generator.generate_interactions(employees_df)


@pytest.fixture(scope="session")
def graph(employees_df: pd.DataFrame, interactions_df: pd.DataFrame) -> nx.Graph:
    builder = OrgGraphBuilder()
    return builder.build_from_interactions(interactions_df, employees_df)


@pytest.fixture(scope="session")
def small_graph() -> nx.Graph:
    """A tiny hand-crafted graph for deterministic tests."""
    g = nx.Graph()
    for i in range(1, 6):
        g.add_node(
            f"EMP-{i:04d}",
            department="Engineering" if i <= 3 else "Sales",
            seniority="Senior" if i == 1 else "Mid",
            tenure_years=float(i * 2),
        )
    g.add_edge("EMP-0001", "EMP-0002", weight=5)
    g.add_edge("EMP-0001", "EMP-0003", weight=3)
    g.add_edge("EMP-0001", "EMP-0004", weight=2)
    g.add_edge("EMP-0001", "EMP-0005", weight=1)
    g.add_edge("EMP-0004", "EMP-0005", weight=4)
    return g
