# -*- coding: utf-8 -*-
from __future__ import unicode_literals


class EscapeInterrupt(Exception):
    "Signal that the ESC key has been pressed"


class ConfigError(Exception):
    "There was a problem with the configuration"


class TUIRError(Exception):
    "Base TUIR error class"


class AccountError(TUIRError):
    "Could not access user account"


class SubmissionError(TUIRError):
    "Submission could not be loaded"


class SubredditError(TUIRError):
    "Subreddit could not be loaded"


class NoSubmissionsError(TUIRError):
    "No submissions for the given page"

    def __init__(self, name):
        self.name = name
        message = '`{0}` has no submissions'.format(name)
        super(NoSubmissionsError, self).__init__(message)


class SubscriptionError(TUIRError):
    "Content could not be fetched"


class InboxError(TUIRError):
    "Content could not be fetched"


class ProgramError(TUIRError):
    "Problem executing an external program"


class BrowserError(TUIRError):
    "Could not open a web browser tab"


class TemporaryFileError(TUIRError):
    "Indicates that an error has occurred and the file should not be deleted"


class MailcapEntryNotFound(TUIRError):
    "A valid mailcap entry could not be coerced from the given url"


class InvalidRefreshToken(TUIRError):
    "The refresh token is corrupt and cannot be used to login"
