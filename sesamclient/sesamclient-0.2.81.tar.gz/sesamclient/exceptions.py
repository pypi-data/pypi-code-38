# Copyright (C) Bouvet ASA - All Rights Reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.
import pprint


class PumpIsAlreadyRunning(Exception):
    def __init__(self, running_task):
        self.running_task = running_task


class PipeAlreadyExists(Exception):
    pass


class SystemAlreadyExists(Exception):
    pass


class TimeoutWhileWaitingForRunningPumpToFinishException(Exception):
    pass


class TimeoutWhileWaitingForRunningIndexToFinishUpdatingException(Exception):
    pass


class ExceptionWithResponse(Exception):
    def __init__(self, msg=None, response=None):
        super_args = []
        if msg:
            super_args.append(msg)
        super().__init__(*super_args)
        self.response = response


class InternalServerError(ExceptionWithResponse):
    """This is raised when the server has responded with a 5xx statuscode"""
    pass


class BadRequestException(ExceptionWithResponse):
    """This is raised when the server has responded with an 4xx statuscode"""
    pass


class PumpDoesNotSupportTheOperation(BadRequestException):
    def __init__(self, pump, operation, response):
        super().__init__(response=response)
        self.pump = pump
        self.operation = operation
        assert response is not None


class ConfigUploadFailed(BadRequestException):
    """This is raised when the server has responded with a 400 statuscode on a configuration upload request. The
    reponse object is stored in the 'response' attribute. The json payload of the response is stored in the
    'parsed_response' attribute."""
    def __init__(self, msg=None, response=None):
        if response is not None:
            from .utils import parse_json_response
            self.parsed_response = parse_json_response(response)
        else:
            self.parsed_response = None

        if msg is None:
            msg = "Config upload failed! response:\n%s" % (pprint.pformat(self.parsed_response),)

        super().__init__(msg=msg, response=response)
