class Player:

    def __init__(self, json):
        self.accounts = json["accounts"]
        self.attributes = json["attributes"]
        self.attributes_version = json["attributesVersion"]
        self.available_languages = json["availableLanguages"]
        self.family_name = json["familyName"]
        self.game = json["game"]
        self.given_name = json["givenName"]
        if "handle" in json:
            self.handle = json["handle"]
        self.headshot = json["headshot"]
        if "homeLocation" in json:
            self.home_location = json["homeLocation"]
        self.id = json["id"]
        self.name = json["name"]
        if "nationality" in json:
            self.nationality = json["nationality"]

        if "teams" in json:
            team_list = []
            for team_json in json["teams"]:
                team_list.append(Team(team_json["team"]))
            self.teams = team_list


class Team:

    def __init__(self, json):
        self.abbreviated_name = json["abbreviatedName"]
        self.accounts = json["accounts"]
        self.address_country = json["addressCountry"]
        self.attributes = json["attributes"]
        self.attributes_version = json["attributesVersion"]
        self.available_languages = json["availableLanguages"]
        self.game = json["game"]
        self.handle = json["handle"]
        self.home_location = json["homeLocation"]
        self.icon = json["icon"]
        self.id = json["id"]
        self.logo = json["logo"]
        self.name = json["name"]
        if "owl_division" in json:
            self.owl_division = json["owl_division"]
        if "players" in json:
            player_list = []
            for player_json in json["players"]:
                player_list.append(Player(player_json['player']))

            self.players = player_list
        self.primary_color = json["primaryColor"]
        self.secondary_color = json["secondaryColor"]
        self.secondary_photo = json["secondaryPhoto"]
