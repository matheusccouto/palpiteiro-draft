"""Unit tests for the lambda function."""

import json
import os

import pytest

import parse
import utils.google
import utils.test

THIS_DIR = os.path.dirname(__file__)

creds = utils.google.get_creds_from_env_vars()


@pytest.fixture(name="players")
def fixture_players():
    """Generate synth players data."""
    with open(os.path.join(THIS_DIR, "sample.json"), encoding="utf-8") as file:
        yield json.load(file)


def test_return_serializable(players):  # pylint: disable=unused-argument
    """Test if return is serializable."""
    events = [
        {
            "players": players,
            "game": "custom",
            "dropout": False,
        },
        {
            "game": "cartola",
            "dropout": False,
        },
        {
            "game": "cartola express",
            "dropout": False,
        },
        {
            "players": players,
            "game": "custom",
            "dropout": 0.1,
        },
        {
            "players": players,
            "game": "custom",
            "dropout": 0.1,
            "dropout_type": "all",
        },
        {
            "players": players,
            "game": "custom",
            "dropout": 0.1,
            "dropout_type": "position",
        },
        {
            "players": players,
            "game": "custom",
            "dropout": 0.1,
            "dropout_type": "club",
        },
    ]
    for event in events:
        res = parse.handler(event)
        assert utils.test.is_serializable(res)


def test_dropout_all(players):
    """Test dropout considering all players."""
    for val in [0.0, 0.1, 0.5]:
        event = {
            "game": "custom",
            "players": players,
            "dropout": val,
            "dropout_type": "all",
        }
        res = parse.handler(event=event, context=None)
        assert len(res["players"]) == round(len(players) * (1 - val))


def test_dropout_clubs(players):
    """Test dropout considering all players."""
    clubs_before = {player["club"] for player in players}
    event = {
        "game": "custom",
        "players": players,
        "dropout": 0.333,
        "dropout_type": "club",
    }
    res = parse.handler(event=event, context=None)
    clubs_after = {player["club"] for player in res["players"]}
    assert len(clubs_before) > len(clubs_after)


def test_dropout_position(players):
    """Test dropout considering position."""
    coaches_before = {
        player["id"] for player in players if player["position"] == "coach"
    }
    event = {
        "game": "custom",
        "players": players,
        "dropout": 0.5,
        "dropout_type": "position",
    }
    res = parse.handler(event=event, context=None)
    coaches_after = {
        player["id"] for player in res["players"] if player["position"] == "coach"
    }
    assert len(coaches_before) >= len(coaches_after)


def test_other_args(players):
    """Test if other args persist."""
    event = {
        "game": "custom",
        "players": players,
        "dropout": 0.5,
        "whatever": "else",
        "dropout_type": "all",
    }
    res = parse.handler(event=event, context=None)
    assert res["whatever"] == "else"
