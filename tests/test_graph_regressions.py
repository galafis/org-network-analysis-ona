import networkx as nx
import pandas as pd
import pytest

from src.network.graph_builder import OrgGraphBuilder


def inputs(weight=0.25, target="B"):
    return pd.DataFrame(
        {"source_id": ["A"], "target_id": [target], "weight": [weight]}
    ), pd.DataFrame({"employee_id": ["A", "B", "C"]})


def test_fractional_weights_and_isolated_employee():
    builder = OrgGraphBuilder()
    g = builder.build_from_interactions(*inputs())
    assert g["A"]["B"]["weight"] == 0.25
    assert builder.get_stats().n_connected_components == 2
    assert builder.get_stats(nx.Graph()).n_nodes == 0


@pytest.mark.parametrize("weight", [0, -1, float("nan"), float("inf")])
def test_bad_weight(weight):
    with pytest.raises(ValueError):
        OrgGraphBuilder().build_from_interactions(*inputs(weight))


@pytest.mark.parametrize("target", ["unknown", "A"])
def test_bad_endpoint(target):
    with pytest.raises(ValueError):
        OrgGraphBuilder().build_directed(*inputs(target=target))
