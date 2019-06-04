import abc
import six

from akeyless.api.base import AkeylessApiI


@six.add_metaclass(abc.ABCMeta)
class Authenticator(object):
    """Parent interface for authentication."""

    def __init__(self, akeyless_api):
        # type: (AkeylessApiI) -> None
        self.akeyless_api = akeyless_api

    @abc.abstractmethod
    def authenticate(self):
        # type: () -> str
        """Gets Akeyless access credentials.

        :rtype: akeyless_auth_api.SystemUserCredentialsReplyObj: an object that contains access credentials.
        :raises CredsRenewalError: if the authentication process fails.
        """