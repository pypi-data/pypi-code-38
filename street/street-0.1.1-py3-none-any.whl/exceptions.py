class StreetError(Exception):
    pass

class RequestBlocked(StreetError):
    pass

class EarningsTableNotFound(StreetError):
    pass