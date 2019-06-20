################################################################################
#
# Licensed Materials - Property of IBM
# (C) Copyright IBM Corp. 2017
# US Government Users Restricted Rights - Use, duplication disclosure restricted
# by GSA ADP Schedule Contract with IBM Corp.
#
################################################################################

from watson_machine_learning_client.log_util import get_logger
import sys


class WMLClientError(Exception):
    def __init__(self, error_msg, reason = None):
        self.error_msg = error_msg
        self.reason = reason
        get_logger(__name__).warning(self.__str__())
        get_logger(__name__).debug(str(self.error_msg) + ('\nReason: ' + str(self.reason) if sys.exc_info()[0] is not None else ''))

    def __str__(self):
        return str(self.error_msg) + ('\nReason: ' + str(self.reason) if self.reason is not None else '')


class MissingValue(WMLClientError, ValueError):
    def __init__(self, value_name, reason = None):
        WMLClientError.__init__(self, 'No \"' + value_name + '\" provided.', reason)


class MissingMetaProp(MissingValue):
    def __init__(self, name, reason = None):
        WMLClientError.__init__(self, 'Missing meta_prop with name: \'{}\'.'.format(name), reason)


class NotUrlNorUID(WMLClientError, ValueError):
    def __init__(self, value_name, value, reason = None):
        WMLClientError.__init__(self, 'Invalid value of \'{}\' - it is not url nor uid: \'{}\''.format(value_name, value), reason)


class NoWMLCredentialsProvided(MissingValue):
    def __init__(self, reason = None):
        MissingValue.__init__(self, 'WML credentials', reason)


class ApiRequestFailure(WMLClientError):
    def __init__(self, error_msg, response, reason = None):
        WMLClientError.__init__(self, '{} ({} {})\nStatus code: {}, body: {}'.format(error_msg, response.request.method, response.request.url, response.status_code, response.text if response.apparent_encoding is not None else '[binary content, ' + str(len(response.content)) + ' bytes]'), reason)


class UnexpectedType(WMLClientError, ValueError):
    def __init__(self, el_name, expected_type, actual_type):
        WMLClientError.__init__(self, 'Unexpected type of \'{}\', expected: {}, actual: \'{}\'.'.format(el_name, '\'{}\''.format(expected_type) if type(expected_type) == type else expected_type, actual_type))


class ForbiddenActionForPlan(WMLClientError):
    def __init__(self, operation_name, expected_plans, actual_plan):
        WMLClientError.__init__(self, 'Operation \'{}\' is available only for {} plan, while this instance has \'{}\' plan.'.format(operation_name, ('one of {} as'.format(expected_plans) if len(expected_plans) > 1 else '\'{}\''.format(expected_plans[0])) if type(expected_plans) is list else '\'{}\''.format(expected_plans), actual_plan))

class NoVirtualDeploymentSupportedForICP(MissingValue):
    def __init__(self, reason = None):
        MissingValue.__init__(self, 'No Virtual deployment supported for ICP', reason)