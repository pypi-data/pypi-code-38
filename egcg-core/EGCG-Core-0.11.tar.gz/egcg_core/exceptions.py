class EGCGError(Exception):
    pass


class ConfigError(EGCGError):
    pass


class RestCommunicationError(EGCGError):
    pass


class LimsCommunicationError(EGCGError):
    pass


class ArchivingError(EGCGError):
    pass
