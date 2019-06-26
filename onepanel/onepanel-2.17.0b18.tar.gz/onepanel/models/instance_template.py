from onepanel.models.api_json import APIJSON

class InstanceTemplate(APIJSON):
    def __init__(self):
        self.uid = None

    @classmethod
    def from_json(cls, dct):
        template = cls()

        template.uid = dct['uid']

        return template

    def api_json(self):
        return {
            'uid': self.uid
        }