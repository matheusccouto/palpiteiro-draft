"""Unit tests for the lambda function."""

import pytest

import dropout


@pytest.fixture(name="players")
def fixture_players():
    """Generate synth players data."""
    yield [
        {
            "id": 1,
            "position": "goalkeeper",
            "price": 1,
            "points": 1,
            "club": 1,
        },
    ] * 100


def test_droupout(players):
    """Test if JSON file exists."""
    for val in [0.0, 0.1, 0.5]:
        event = {"players": players, "dropout": val}
        res = dropout.handler(event=event, context=None)
        assert len(res["players"]) == len(players) * (1 - val)


def test_other_args(players):
    """Test if other args persist."""
    event = {"players": players, "dropout": 0.5, "whatever": "else"}
    res = dropout.handler(event=event, context=None)
    assert res["whatever"] == "else"
