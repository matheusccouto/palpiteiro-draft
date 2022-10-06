"""Create README.md overview diagram."""

# pylint: disable=expression-not-assigned

import os

from diagrams import Cluster, Diagram
from diagrams.aws.compute import Lambda
from diagrams.aws.network import APIGateway
from diagrams.gcp.analytics import Bigquery


THIS_DIR = os.path.dirname(__file__)
ICONS_DIR = os.path.join(THIS_DIR, "icons")


with Diagram(filename=os.path.join(THIS_DIR, "architecture"), show=False):
    api = APIGateway("post")
    with Cluster("step function"):
        (
            api
            >> Bigquery("dim_player_last")
            >> Lambda("read")
            >> Lambda("filter")
            >> Lambda("dropout")
            >> Lambda("draft")
        )
