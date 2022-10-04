"""Profiling"""

import pprofile

from draft.draft import Scheme
from draft.draft.algorithm.genetic import Genetic
from . import helper


if __name__ == "__main__":

    # Profiling.
    prof = pprofile.Profile()
    with prof():
        Genetic(helper.load_players()).draft(
            price=140,
            scheme=Scheme(
                goalkeeper=1,
                defender=2,
                fullback=2,
                midfielder=3,
                forward=3,
                coach=0,
            ),
            max_players_per_club=5,
        )

    prof.dump_stats("profiling.txt")
