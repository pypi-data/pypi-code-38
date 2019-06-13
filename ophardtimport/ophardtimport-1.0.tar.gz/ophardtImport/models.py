

class Fencer:
    """Model for a fencer"""
    id = None
    name = None
    surname = None
    nation = None
    birthday = None
    gender = None
    association = None
    league = None
    hand = None
    status = None
    license = None
    paid = None
    image = None

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)


class Tournament:
    """Model for a tournament"""
    id = None
    title = None
    title_long = None
    fencer = []
    gender = None
    weapon = None
    date = None
    season = None
