from onepanel.models.api_json import APIJSON

class VolumeType(APIJSON):
    def __init__(self):
        self.uid = None
        self.info = {}

    def api_json(self):
        return {
            'uid': self.uid,
        }

    @classmethod
    def from_json(cls, dct):
        volume = cls()

        volume.uid = dct['uid']
        volume.info['size'] = dct['info']['size']

        return volume