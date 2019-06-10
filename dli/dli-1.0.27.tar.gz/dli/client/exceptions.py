class DatalakeException(Exception):
    pass


class CatalogueEntityNotFoundException(DatalakeException):

    def __init__(self, entity, params=None, message=None):
        if not params and not message:
            message = "%s not found" % entity

        self.message = (
            message or '{} with params `{}` not found'.format(entity, params)
        )

        super(CatalogueEntityNotFoundException, self).__init__(self.message)


class InvalidPayloadException(DatalakeException):
    pass


class S3FileDoesNotExist(DatalakeException):
    def __init__(self, file_path):
        self.message = (
            "Either file at path `%s` does not exist / Potential issue with the bucket policy."
            "Please reach out to Datalake Tech Data Ops user for resolution." % file_path
        )

        super(S3FileDoesNotExist, self).__init__(self.message)


class DownloadDestinationNotValid(DatalakeException):
    """
    Raised when a download destination is not a directory
    """
    pass


class DownloadFailed(DatalakeException):
    pass


class NoAccountSpecified(DatalakeException):

    def __init__(self, accounts):
        self.accounts = accounts
        self.message = (
            "Unable to default the account for access_manager_id, tech_data_ops_id and/or manager_id "
            "due to multiple accounts being attached to this API key. "
            "Your accounts are: %s" % [(a.id, a.name) for a in accounts]
        )
        super(NoAccountSpecified, self).__init__(self.message)


class UnAuthorisedAccessException(DatalakeException):
    pass


class InsufficientPrivilegesException(DatalakeException):
    def __init__(self, message=None):
        self.message = (
            message or 'Insufficient privileges to perform this action'
        )

        super(InsufficientPrivilegesException, self).__init__(self.message)


class MissingMandatoryArgumentException(DatalakeException):
    def __init__(self, argument):
        self.message = "%s is required" % argument
        super(MissingMandatoryArgumentException, self).__init__(self.message)


def is_boto_client_access_denied_error(e):
    # s3fs wraps the boto ClientError under OSError with no particular code. Hence the check
    return isinstance(e, OSError) and 'AccessDenied' in str(e.strerror)
