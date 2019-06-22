from onepanel.models.api_json import APIJSON

class GitSource(APIJSON):
    def __init__(self, branch, commit_hash=None):
        self.version = 1
        self.branch = branch
        self.commit_hash = commit_hash

    @classmethod
    def from_json(cls, dct):
        data = dct['data']

        branch_name = data['branch']['name']

        if isinstance(data['commit'], dict):
            commit_id = data['commit']['id']
        else:
            commit_id = ''

        return cls(branch_name, commit_id)

    @classmethod
    def from_string(cls, value):
        """value is expected to be branch_name/commit_hash"""

        parts = value.split('/')

        return cls(parts[0], parts[1])

    def api_json(self):
        return {
            'version': self.version,
            'data': {
                'commit': {
                    'id': self.commit_hash
                },
                'branch': {
                    'name': self.branch
                }
            }
        }