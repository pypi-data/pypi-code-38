import requests
from os import path
from .models.team import Team
from .models.player import Player


class OverwatchApi:

    def __init__(self, base_url="https://api.overwatchleague.com/"):
        self.base_url = base_url

    def construct_url(self, endpoint):
        return path.join(self.base_url, endpoint)

    def get(self, endpoint):
        return requests.get(self.construct_url(endpoint)).json()

    def get_teams(self):
        teams_api_response = self.get("teams")

        teams = []
        for competitor in teams_api_response["competitors"]:
            teams.append(Team(competitor["competitor"]))

        return teams

    def get_players(self):
        players_api_response = self.get("players")

        players = []
        for player in players_api_response["content"]:
            players.append(Player(player))

        return players
