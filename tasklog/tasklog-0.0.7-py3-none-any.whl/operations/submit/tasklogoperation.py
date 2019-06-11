from enum import Enum
from .generictasklog import GenericWorklog

class OperationStatus(Enum):
    UNKNOWN = 0
    SUCCESS = 1
    FAILED = 2
    PENDING = 3


class Reason(Enum):
    UNKNOWN = 0
    NO_APPLICABLE_REASON = 1
    NO_WORKLOG_PARSED = 2
    NO_ISSUE_TYPE_FOUND = 3
    NO_PROJECT_FOUND = 4
    NO_WORKLOG_APPENDED = 5


class WorklogOperation:
    def __init__(self, genericWorklog=None, rawWorkLog=None, status=OperationStatus.UNKNOWN, reason=Reason.UNKNOWN):
        self.jiraWorklog = None
        self.genericWorklog = genericWorklog
        self.rawWorklog = rawWorkLog
        self.status = status
        self.reason = reason

    def __format__(self, format):
        if format == 'human':
            jiraWorklog = self.jiraWorklog
            if jiraWorklog is not None:
                jiraWorklog = "{} ({} - {})\n{}\n{}\n{}".format(
                    jiraWorklog.issueId,
                    jiraWorklog.id,
                    jiraWorklog.author.name,
                    jiraWorklog.started,
                    jiraWorklog.timeSpent,
                    jiraWorklog.comment
                )

            genericWorklog = self.genericWorklog
            if genericWorklog is None:
                genericWorklog = GenericWorklog()

            value = "RAW:\n{}\n\nGENERIC:\n{:human}\n\nJIRA:\n{}\n\nSTATUS:\n{}\n\nREASON:\n{}".format(
                self.rawWorklog,
                genericWorklog,
                jiraWorklog,
                self.status,
                self.reason,
            )

            return value

        return "{} {} {} {} {}".format(
            self.projectKey,
            self.issueKey,
            self.date,
            self.durationInSeconds,
            self.description,
        )
