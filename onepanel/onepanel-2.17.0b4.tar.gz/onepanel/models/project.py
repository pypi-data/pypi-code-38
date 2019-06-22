from onepanel.models.api_json import APIJSON
from onepanel.models.account import Account

class Project(APIJSON):
    def __init__(self):
        self.uid = None
        self.account = Account()

    def api_json(self):
        return {
            'uid': self.uid,
        }

    @classmethod
    def from_json(cls, dct):
        project = cls()

        project.uid = dct['uid']
        project.account = Account.from_json(dct['account'])

        return project