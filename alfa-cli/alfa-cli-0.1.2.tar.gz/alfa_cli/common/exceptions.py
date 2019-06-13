from alfa_sdk.common.exceptions import AlfaError


class AlfaCliError(AlfaError):
    template = "{message}"


class RuntimeError(AlfaCliError):
    pass
