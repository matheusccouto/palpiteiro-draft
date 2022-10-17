"""Unit tests for AWS lambda function."""

import time

import pytest

import draft
from draft.draft.algorithm import DraftError
from . import helper


@pytest.fixture(name="event")
def fixture_event():
    """typical event"""
    return {
        "players": helper.load_players_dict(),
        "algorithm": "genetic",
        "scheme": {
            "goalkeeper": 1,
            "defender": 2,
            "fullback": 2,
            "midfielder": 3,
            "forward": 3,
            "coach": 0,
        },
        "price": 140,
        "max_players_per_club": 5,
        "bench": True,
    }


def test_time(event):
    """Test typical run time."""
    start = time.time()
    draft.handler(event=event, context=None)
    end = time.time()
    assert end - start < 10


def test_amount_of_players(event):
    """Test if amount of players is correct."""
    results = draft.handler(event=event, context=None)
    assert len(results["players"]) == 11
    assert len(results["bench"]) == 5


def test_expected_points(event):
    """Test if points lies under expected range."""
    results = draft.handler(event=event, context=None)
    assert sum(p["points"] for p in results["players"]) > 11.1


def test_price(event):
    """Test resulting price."""
    event["price"] = 50
    results = draft.handler(event=event, context=None)
    assert round(sum(p["price"] for p in results["players"])) <= 50


def test_few_players(event):
    """Test if it fails if using few players."""
    event["players"] = event["players"][:10]
    with pytest.raises(DraftError):
        draft.handler(event=event, context=None)


def test_bench_amount(event):
    """Test if bench was drafted correctly."""
    results = draft.handler(event=event, context=None)
    assert len(results["bench"]) == 5
    assert len({p["position"] for p in results["bench"]}) == 5


def test_bench_with_few_players(event):
    """Test if it ignores if there is a missing player on the bench."""
    # Remove all goalkeepers and keep only one.
    # It will make sure that there will be no goalkeeper available for the bench
    goalkeepers = [p for p in event["players"] if p["position"] == "goalkeeper"]
    event["players"] = [p for p in event["players"] if p["position"] != "goalkeeper"]
    event["players"] += goalkeepers[:1]

    # Make sure that the bench is incomplete.
    results = draft.handler(event=event, context=None)
    assert len(results["bench"]) < 5


def test_max_players_per_club(event):
    """Test if max players per club is respected."""
    event["max_players_per_club"] = 3
    results = draft.handler(event=event, context=None)
    clubs = [p["club"] for p in results["players"]]
    assert max(clubs.count(c) for c in clubs) <= 3


def test_schema(event):
    """Test if schema is respected"""
    event["scheme"] = {
        "goalkeeper": 2,
        "defender": 3,
        "fullback": 4,
        "midfielder": 4,
        "forward": 3,
        "coach": 2,
    }
    results = draft.handler(event=event, context=None)
    for pos, count in event["scheme"].items():
        actual = len([p for p in results["players"] if p["position"] == pos])
        assert actual == count


def test_bench_amount_when_position_does_not_exist(event):
    """Test if bench was drafted correctly when a position does not exist."""
    event["scheme"] = {
        "goalkeeper": 1,
        "defender": 3,
        "fullback": 0,
        "midfielder": 5,
        "forward": 2,
        "coach": 0,
    }
    results = draft.handler(event=event, context=None)
    assert len(results["bench"]) == 4
    assert len({p["position"] for p in results["bench"]}) == 4


def test_no_bench(event):
    """Test if bench is skipped when asked."""
    event["bench"] = False
    results = draft.handler(event=event, context=None)
    assert len(results["bench"]) == 0


def test_bench_prices(event):
    """Test if bench prices are lower than starters."""
    results = draft.handler(event=event, context=None)
    for bench in results["bench"]:
        for starter in results["players"]:
            if bench["position"] == starter["position"]:
                assert bench["price"] <= starter["price"]


def test_extra_properties(event):
    """Test if it passthrought players extra propertires"""
    for player in event["players"]:
        player["foo"] = "bar"

    results = draft.handler(event=event, context=None)

    players = results["players"] + results["bench"]
    for player in players:
        assert player["foo"] == "bar"
