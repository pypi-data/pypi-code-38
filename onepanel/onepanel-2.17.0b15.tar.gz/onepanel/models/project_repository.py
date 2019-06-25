from onepanel.models.api_json import APIJSON

class ProjectRepository(APIJSON):
    def __init__(self, uid=None, url=None, branch=None):
        self.uid = uid
        self.url = url
        self.branch = branch

    def api_json(self):
        return {
            'uid': self.uid,
            'url': self.url,
            'branch': self.branch
        }

    @classmethod
    def from_json(cls, dct):
        project_repository = cls()
        project_repository.uid = dct['uid']
        project_repository.url = dct['url']
        project_repository.branch = dct['branch']

        return project_repository
