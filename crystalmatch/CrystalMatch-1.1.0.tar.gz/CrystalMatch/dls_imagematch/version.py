# Version information for CrystalMatch
__version__ = "1.1.0"
__date__ = "04/06/2019"


class VersionHandler:
    def __init__(self):
        pass

    @staticmethod
    def version():
        return __version__

    @staticmethod
    def release_date():
        return __date__

    @staticmethod
    def version_string():
        return '%(prog)s ' + VersionHandler.version() + ', ' + VersionHandler.release_date()
