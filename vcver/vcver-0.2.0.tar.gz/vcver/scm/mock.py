from .base import SCM


class MockSCM(SCM):
    """ a mock scm """

    RELEASE_BRANCH_REGEX = "master"

    def __init__(self, props):
        self._props = props

    @staticmethod
    def is_repo(path):
        return True

    def get_properties(self):
        return self._props
