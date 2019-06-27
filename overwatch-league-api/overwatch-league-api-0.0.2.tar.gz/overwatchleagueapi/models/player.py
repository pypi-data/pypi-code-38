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
        self.teams = json["teams"]
