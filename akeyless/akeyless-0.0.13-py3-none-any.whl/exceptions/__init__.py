"""Contains exception classes for Akeyless SDK."""


class AkeylessSDKClientError(Exception):
    """General exception class for Akeyless SDK."""


class CredsRenewalError(AkeylessSDKClientError):
    """Exception class for Credentials renewal."""
