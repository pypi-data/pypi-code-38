class OffsetCheckBaseError(Exception):
    pass


class OffsetSpanOverlapError(OffsetCheckBaseError):
    pass


class OffsetSpanTextMismatchError(OffsetCheckBaseError):
    pass


class OffsetSpanCheckError(OffsetCheckBaseError):
    pass
