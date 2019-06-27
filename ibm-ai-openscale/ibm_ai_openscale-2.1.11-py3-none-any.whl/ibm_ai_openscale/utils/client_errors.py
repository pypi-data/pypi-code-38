# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-J33
# Copyright IBM Corp. 2018
# The source code for this program is not published or other-wise divested of its trade 
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import logging
import sys


class ClientError(Exception):
    def __init__(self, error_msg, reason = None):
        self.error_msg = error_msg
        self.reason = reason
        #logging.getLogger(__name__).warning(self.__str__())
        logging.getLogger(__name__).debug(str(self.error_msg) + ('\nReason: ' + str(self.reason) if sys.exc_info()[0] is not None else ''))

    def __str__(self):
        return str(self.error_msg) + ('\nReason: ' + str(self.reason) if self.reason is not None else '')


class MissingValue(ClientError, ValueError):
    def __init__(self, value_name, reason = None):
        ClientError.__init__(self, 'No \"' + value_name + '\" provided.', reason)


class IncorrectValue(ClientError, ValueError):
    def __init__(self, value_name, reason = None):
        ClientError.__init__(self, 'Incorrect \"' + value_name + '\" provided.', reason)


class IncorrectParameter(ClientError, ValueError):
    def __init__(self, parameter_name, reason=None):
        ClientError.__init__(self, 'Unsupported parameter \"' + parameter_name + '\" provided.', reason)


class MissingMetaProp(MissingValue):
    def __init__(self, name, reason = None):
        ClientError.__init__(self, 'Missing meta_prop with name: \'{}\'.'.format(name), reason)


class NotUrlNorUID(ClientError, ValueError):
    def __init__(self, value_name, value, reason = None):
        ClientError.__init__(self, 'Invalid value of \'{}\' - it is not url nor uid: \'{}\''.format(value_name, value), reason)


class InvalidCredentialsProvided(MissingValue):
    def __init__(self, reason = None):
        MissingValue.__init__(self, 'WML credentials', reason)


class ApiRequestFailure(ClientError):
    def __init__(self, error_msg, response, reason = None):
        self.response = response
        ClientError.__init__(self, '{} ({} {})\nStatus code: {}, body: {}'.format(error_msg, response.request.method, response.request.url, response.status_code, response.text if response.apparent_encoding is not None else '[binary content, ' + str(len(response.content)) + ' bytes]'), reason)


class ApiRequestWarning(ClientError):
    def __init__(self, error_msg, response):
        ClientError.__init__(self, '{}\nStatus code: {}, body: {}'.format(error_msg, response.status_code,
                                                         response.text if response.apparent_encoding is not None else '[binary content, ' + str(
                                                             len(response.content)) + ' bytes]'))

    @staticmethod
    def print_msg(error_msg, response):
        print('{}\nStatus code: {}, body: {}'.format(error_msg, response.status_code,
                                                         response.text if response.apparent_encoding is not None else '[binary content, ' + str(
                                                             len(response.content)) + ' bytes]'))


class UnexpectedType(ClientError, ValueError):
    def __init__(self, el_name, expected_type, actual_type):
        ClientError.__init__(self, 'Unexpected type of \'{}\', expected: {}, actual: \'{}\'.'.format(el_name, '\'{}\''.format(expected_type) if type(expected_type) == type else expected_type, actual_type))


class ForbiddenActionForPlan(ClientError):
    def __init__(self, operation_name, expected_plans, actual_plan):
        ClientError.__init__(self, 'Operation \'{}\' is available only for {} plan, while this instance has \'{}\' plan.'.format(operation_name, ('one of {} as'.format(expected_plans) if len(expected_plans) > 1 else '\'{}\''.format(expected_plans[0])) if type(expected_plans) is list else '\'{}\''.format(expected_plans), actual_plan))


class UnsupportedActionForEngine(ClientError):
    def __init__(self, operation_name, expected_engine, actual_engine):
        ClientError.__init__(self, 'Operation \'{}\' is available only for {} engine, while this instance has \'{}\' bound.'.format(operation_name, ('one of {} as'.format(expected_engine) if len(expected_engine) > 1 else '\'{}\''.format(expected_engine[0])) if type(expected_engine) is list else '\'{}\''.format(expected_engine), actual_engine))


class UnsupportedActionForDataType(ClientError):
    def __init__(self, operation_name, expected_type, actual_type):
        ClientError.__init__(self, 'Operation \'{}\' is available only for {} data type, while this instance has \'{}\' provided.'.format(operation_name, expected_type, actual_type))


class UnsupportedEngine(ClientError):
    def __init__(self, operation_name, expected_engine, expected_region='all'):
        ClientError.__init__(self, 'Operation \'{}\' is supported for {} in {} regions'.format(operation_name, expected_engine, expected_region))

    @staticmethod
    def print_msg(operation_name, expected_engine, expected_region='all'):
        print('Operation \'{}\' is supported for {} in {} regions'.format(operation_name, expected_engine, expected_region))
