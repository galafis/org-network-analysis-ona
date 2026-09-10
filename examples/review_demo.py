from dataclasses import asdict
import pandas as pd
from src.network.graph_builder import OrgGraphBuilder


def run():
    employees = pd.DataFrame(
        {
            "employee_id": ["A", "B", "C", "D"],
            "department": ["Design", "Engineering", "Engineering", "Operations"],
        }
    )
    interactions = pd.DataFrame(
        {"source_id": ["A", "B", "B"], "target_id": ["B", "A", "C"], "weight": [0.25, 0.5, 1.25]}
    )
    builder = OrgGraphBuilder()
    graph = builder.build_from_interactions(interactions, employees)
    assert graph["A"]["B"]["weight"] == 0.75
    assert builder.get_stats().n_connected_components == 2
    return {
        "synthetic": True,
        "stats": asdict(builder.get_stats()),
        "edges": [
            {"source": a, "target": b, "weight": d["weight"]} for a, b, d in graph.edges(data=True)
        ],
        "isolated_employee": "D",
    }


if __name__ == "__main__":
    import json

    print(json.dumps(run(), ensure_ascii=False, indent=2, allow_nan=False))
