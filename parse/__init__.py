"""Read data from Google Big Query."""

import json
import random
from decimal import Decimal

import pandas as pd
from pandas import Timestamp

import utils.google

creds = utils.google.get_creds_from_env_vars()


class Encoder(json.JSONEncoder):
    """Encoder for JSON."""

    def default(self, o):
        """Encode Decimal."""
        if isinstance(o, Decimal):
            return float(o)
        if isinstance(o, Timestamp):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)


def read_bigquery(query):
    """Read data from Bigquery"""
    dic = pd.read_gbq(
        query=query,
        project_id=creds.project_id,
        index_col=None,
        credentials=creds,
    ).to_dict(orient="records")
    return json.loads(json.dumps(dic, cls=Encoder))


def _n_to_keep(total, dropout):
    n_to_keep = round(total * (1 - dropout))
    if n_to_keep <= 0:
        n_to_keep = 1
    return int(n_to_keep)


def dropout_players(players, dropout):
    """Dropout a percentage of all players."""
    random.shuffle(players)
    return players[: _n_to_keep(len(players), dropout)]


def dropout_position(players, dropout):
    """Dropout a percentage of all players based on position."""
    positions = {player["position"] for player in players}
    groups = [
        dropout_players([p for p in players if p["position"] == position], dropout)
        for position in positions
    ]
    return [player for group in groups for player in group]


def dropout_clubs(players, dropout):
    """Dropout a percentage of all players based on club."""
    clubs = list({player["club"] for player in players})
    random.shuffle(clubs)
    selected_clubs = clubs[: _n_to_keep(len(clubs), dropout)]
    return [player for player in players if player["club"] in selected_clubs]


def handler(event, context=None):  # pylint: disable=unused-argument
    """Lambda handler."""
    if "express" in event["game"]:
        event["players"] = read_bigquery(
            "SELECT *, price_cartola_express AS price FROM palpiteiro.dim_player_last"
        )

    elif "cartola" in event["game"]:
        event["players"] = read_bigquery(
            "SELECT *, price_cartola AS price FROM palpiteiro.dim_player_last"
        )

    if event["dropout"]:
        if "all" in event["dropout_type"]:
            event["players"] = dropout_players(event["players"], event["dropout"])
        elif "position" in event["dropout_type"]:
            event["players"] = dropout_position(event["players"], event["dropout"])
        elif "club" in event["dropout_type"]:
            event["players"] = dropout_clubs(event["players"], event["dropout"])
        else:
            raise ValueError("Could not recognize dropout_type.")

    return event
