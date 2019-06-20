import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sports_client_factory import SportsClientFactory  # noqa: F401,E402
from sports_client_nba import SportsClientNBA  # noqa: F401,E402

name = 'odds_client'
