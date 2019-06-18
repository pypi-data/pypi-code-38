class EloquaException(Exception):
    """ Eloqua Exception base class"""
    pass


class EloquaConnectionException(EloquaException):
    """ Connection Exception caused on connecting to Eloqua. Usually login or downtime associated"""
    pass


class EloquaInvalidUseageException(EloquaException):
    """ Using the library incorrectly """
    pass


class EloquaRequestError(EloquaException):
    """ Error from Eloqua API request """

    def __init__(self, resp, msg=None):
        self.url = resp.url
        self.error_code = resp.status_code
        if not msg:
            self.msg = resp.content
            if self.error_code == 404:
                self.msg = "Not found"

    def __str__(self):
        return '\nURL: %s \nError Code:%s \n%s' % (self.url, self.error_code, self.msg)


class EloquaRequestErrorNotFound(EloquaRequestError):
    """ 404 error code """

    def __init__(self, resp, msg=None):
        self.url = resp.url
        self.error_code = resp.status_code
        if not msg:
            self.msg = "Not found"

    def __str__(self):
        return '%s %s : %s' % (self.url, self.error_code, self.msg)
