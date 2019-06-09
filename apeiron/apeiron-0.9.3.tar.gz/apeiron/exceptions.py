class ModpackError(Exception):
    pass


class ManifestError(Exception):
    pass


class InvalidStatusError(ModpackError):
    pass


class StateConflictError(ModpackError):
    pass


class ConsistenceError(ManifestError):
    pass
