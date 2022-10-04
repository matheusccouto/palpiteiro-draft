"""Functions for testing."""

import json


def is_serializable(dic):
    """Check if an dictionary is serializable."""
    try:
        json.dumps(dic)
        return True
    except TypeError:
        return False
