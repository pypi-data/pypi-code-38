from onepanel.models.api_json import APIJSON

class Environment(APIJSON):
    def __init__(self):
        self.uid = None
        self.name = None

    @classmethod
    def from_json(cls, dct):
        template = cls()

        template.uid = dct['uid']
        template.name = dct['name']

        return template

    def api_json(self):
        return {
            'uid': self.uid,
            'name': self.name
        }