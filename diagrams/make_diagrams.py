"""Create README.md overview diagram."""

# pylint: disable=expression-not-assigned

import os
from wsgiref.util import application_uri

from diagrams import Cluster, Diagram
from diagrams.aws.compute import Lambda
from diagrams.aws.network import APIGateway
from diagrams.custom import Custom
from diagrams.gcp.analytics import Bigquery
from diagrams.onprem.ci import GithubActions
from diagrams.onprem.vcs import Git, Github
from diagrams.programming.language import Python


THIS_DIR = os.path.dirname(__file__)
ICONS_DIR = os.path.join(THIS_DIR, "icons")


with Diagram(
    "\napi",
    filename=os.path.join(THIS_DIR, "api"),
    show=False,
    curvestyle="curved",
):
    api = APIGateway("post")
    with Cluster("Step Function"):
        (
            api
            >> Bigquery("dim_player_last")
            >> Lambda("read")
            >> Lambda("filter")
            >> Lambda("dropout")
            >> Lambda("draft")
        )


with Diagram(
    "\nFlow",
    filename=os.path.join(THIS_DIR, "flow"),
    show=False,
    curvestyle="curved",
):
    gh_pr = Github("pull request to main")
    gh_merge = Github("merge to main")
    serverless = Custom("serverless", os.path.join(ICONS_DIR, "serverless.png"))

    Git("push to dev") >> gh_pr
    gh_pr >> GithubActions("testing") >> Python("pytest") >> gh_merge
    gh_pr >> GithubActions("linting") >> Python("pylint") >> gh_merge
    gh_merge >> GithubActions("deploy") >> serverless
