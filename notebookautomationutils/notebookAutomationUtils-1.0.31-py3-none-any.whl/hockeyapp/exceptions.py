class HockeyToGusError(Exception):
  def __init__(self, message):
    super(HockeyToGusError, self).__init__(message)


class PageNotFoundError(HockeyToGusError):
  def __init__(self, message):
    super(PageNotFoundError, self).__init__(message)

class AuthenticationError(HockeyToGusError):
  def __init__(self, message):
    super(AuthenticationError, self).__init__(message)


class DataNotFoundError(HockeyToGusError):
  def __init__(self, message):
    super(DataNotFoundError, self).__init__(message)


class BadRequestError(HockeyToGusError):
  def __init__(self, message):
    super(BadRequestError, self).__init__(message)

class RateLimitedError(HockeyToGusError):
  def __init__(self, message):
    super(RateLimitedError, self).__init__(message)