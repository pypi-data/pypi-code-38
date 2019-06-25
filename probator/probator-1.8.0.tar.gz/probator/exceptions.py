class ProbatorError(Exception):
    pass


class ProbatorFatalError(ProbatorError):
    pass


class CloudFlareError(ProbatorError):
    pass


class EmailSendError(ProbatorError):
    pass


class ObjectDeserializationError(ProbatorError):
    pass


class SlackError(ProbatorError):
    pass


class ResourceException(ProbatorError):
    """Exception class for resource types"""


class IssueException(ProbatorError):
    """Exception class for issue types"""


class AccountException(ProbatorError):
    """Exception class for Account types"""


class SchedulerError(ProbatorError):
    """Exception class for scheduler plugins"""
