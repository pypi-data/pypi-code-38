from pprint import pprint
from sports_client_factory import SportsClientFactory
# from datetime import datetime, timedelta, date
# import json

subs_key_nba = '38894df74dde436f9e749089aaa28106'

factory = SportsClientFactory()
sr = factory.get_api_client('nba')
# print("\n Testing get_pre_game_odds_by_date \n")
# data = sr.get_pre_game_odds_by_date()
# pprint(data)

# print("\n Testing get_pre_game_odds \n")
# start_date = date(2019, 5, 1)
# end_date = date(2019, 5, 7)
# data = sr.get_pre_game_odds(start_date, end_date)
# data = sr.get_pre_game_odds('2019-05-15', '2019-05-25')
print("\n Testing get_consolidated_games \n")
data = sr.get_active_players()
#data = sr.get_pre_game_odds_by_date()

pprint(data)
