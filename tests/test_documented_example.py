import json
from pathlib import Path

from examples.review_demo import run


def test_documented_example_matches_published_result():
    expected = json.loads(
        (Path(__file__).resolve().parents[1] / "examples/expected.json").read_text(
            encoding="utf-8"
        )
    )
    actual = json.loads(json.dumps(run(), allow_nan=False))
    assert actual == expected
