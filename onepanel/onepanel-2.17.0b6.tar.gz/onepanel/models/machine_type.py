from onepanel.models.api_json import APIJSON


class MachineType(APIJSON):
    def __init__(self):
        self.uid = None
        self.info = {}

    def api_json(self):
        return {
            'uid': self.uid
        }

    @classmethod
    def from_json(cls, dct):
        machine = cls()

        machine.uid = dct['uid']
        machine.info['cpu'] = dct['info']['cpu']
        machine.info['gpu'] = dct['info'].get('gpu')
        machine.info['ram'] = dct['info']['ram']

        return machine
