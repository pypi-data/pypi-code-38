import data

class Namespace:
    name = None
    service = None

    def __init__(self):
        self.name = "hcli"
        self.service = []

    def serialize(self):
        return data.DAO(self).serialize()     
