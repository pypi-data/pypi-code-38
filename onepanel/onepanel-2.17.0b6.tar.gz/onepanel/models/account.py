from onepanel.models.api_json import APIJSON

class Account(APIJSON):
    def __init__(self):
        self.uid = None

    def api_json(self):
        return {
            'uid': self.uid,
        }

    @classmethod
    def from_json(cls, dct):
        account = cls()

        account.uid = dct['uid']

        return account