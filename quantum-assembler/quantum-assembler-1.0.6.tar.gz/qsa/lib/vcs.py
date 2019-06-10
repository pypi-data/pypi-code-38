import os


class VersionControlSystem:
    """Abstracts the version control system and allows the QSA
    command-line utility to organize its commits.
    """
    #: Indicates if version control is disabled.
    disabled = os.getenv('QSA_DISABLE_VCS') == '1'

    def __init__(self, config):
        self.config = config
