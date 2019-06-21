class VenvExistsError(Exception):
    pass


class VenvNotFound(Exception):
    pass


class VenvBinariesMissing(Exception):
    pass


class InvalidJSON(Exception):
    pass


class MissingJSONKeys(Exception):
    pass


class InvalidVersionFormat(Exception):
    pass


class InvalidMainScriptPath(Exception):
    pass


class InvalidTestsPath(Exception):
    pass


class DownloadDependenciesError(Exception):
    pass


class MissingDependencies(Exception):
    pass
