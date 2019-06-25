from onepanel.models.api_json import APIJSON


class DatasetMount(APIJSON):
    def __init__(self, account_uid=None, dataset_uid=None, version=None, destination=None):
        self.account_uid = account_uid
        self.dataset_uid = dataset_uid
        self.set_version(version)
        self.destination = destination

    def set_source(self, source):
        """Source is expected to be account_uid/dataset_uid"""
        source_parts = source.split('/')
        self.account_uid = source_parts[0]
        self.dataset_uid = source_parts[1]

    @classmethod
    def from_simple_json(cls, dct):
        identifier = cls()

        identifier.set_source(dct['source'])
        identifier.set_version(dct['version'])
        identifier.destination = dct['destination']

        return identifier

    @classmethod
    def from_json(cls, dct):
        dataset_mount = cls()

        dataset_mount.account_uid = dct['dataset']['account']['uid']
        dataset_mount.dataset_uid = dct['dataset']['uid']
        dataset_mount.set_version(dct['dataset_versioning']['version'])
        dataset_mount.destination = dct['alias']

        return dataset_mount

    def set_version(self, version):
        if version is None:
            self.version = None
            return
            
        self.version = int(version)

    def api_json(self):
        return {
            'accountUID': self.account_uid,
            'datasetUID': self.dataset_uid,
            'datasetVersion': self.version,
            'alias': self.destination
        }

    def __str__(self):
        return "{{accountUID:{}\ndatasetUID:{}\nversion:{}\nalias:{}}}".format(self.account_uid, self.dataset_uid, self.version, self.destination)

    def __repr__(self):
        return self.__str__()
