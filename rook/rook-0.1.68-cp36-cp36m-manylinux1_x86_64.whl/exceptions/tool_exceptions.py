class ToolException(Exception):

    def __init__(self, *args):
        super(ToolException, self).__init__(*args)

    def get_type(self):
        return self.__class__.__name__

    def get_message(self):
        try:
            return self.args[0]
        except IndexError:
            return ""

    def get_parameters(self):
        try:
            return self.args[1]
        except IndexError:
            return ()


class RookException(ToolException):
    pass


class RookCommunicationException(RookException):
    pass


class RookInputException(ToolException):
    pass


class WebHookProcessingException(Exception):
    def __init__(self, status_code, content):
        super(WebHookProcessingException, self).__init__("Problem sending webhook %s" % status_code,
                                                         {
                                                             "status_code": status_code,
                                                             "content": content
                                                         })


class WebHookRetryLevelException(Exception):
    def __init__(self, retry_level, valid_levels):
        super(WebHookRetryLevelException, self).__init__("Invalid retry level for webhook %s" % retry_level,
                                                         {
                                                        "retry_level": retry_level,
                                                        "valid_levels": valid_levels}
                                                         )


class RookInvalidArithmeticPath(RookInputException):
    def __init__(self, configuration, error=None):
        super(RookInvalidArithmeticPath, self).__init__("Invalid arithmetic path configuration. configuration: %s, innerException: %s" % (configuration, error),
                                                        {'configuration': configuration, 'error': error})



class RookAugInvalidKey(RookInputException):
    def __init__(self, key, configuration):
        super(RookAugInvalidKey, self).__init__("Failed to get key %s from configuration %s" % (key, configuration),
                                                {'key': key,
                                                 'configuration': configuration})


class RookObjectNameMissing(RookInputException):
    def __init__(self, configuration):
        super(RookObjectNameMissing, self).__init__("Failed to find object name %s" % configuration, {'configuration': configuration})


class RookUnknownObject(RookInputException):
    def __init__(self, object_name):
        super(RookUnknownObject, self).__init__("Failed to find object %s" % object_name, {'object_name': object_name})


class RookInvalidObjectConfiguration(RookInputException):
    def __init__(self, object_name, object_config):
        super(RookInvalidObjectConfiguration, self).__init__("Failed to build object %s" % object_name,
                                                             {'object_name': object_name,
                                                              'object_config': object_config})


class RookSendToRookoutDisabledException(RookInputException):
    def __init__(self):
        super(RookSendToRookoutDisabledException, self).__init__()


class RookMonitorException(RookException):
    pass


class RookHashFailedException(RookMonitorException):
    def __init__(self, module_name):
        super(RookHashFailedException, self).__init__("Failed to calculate hash %s" % module_name, {'module': module_name})


class RookHashMismatchException(RookMonitorException):
    def __init__(self, filepath, expected, calculated, gitBlob=None):
        super(RookHashMismatchException, self).__init__("File hashes do not match! path: %s, expected: %s, calculated: %s" % (filepath, expected, calculated),
                                                        {'filepath': filepath,
                                                         'expected': expected,
                                                         'calculated': calculated,
                                                         'gitBlob': gitBlob})


class RookHashCalculationFailed(RookMonitorException):
    def __init__(self, filepath, class_name, exc):
        super(RookHashCalculationFailed, self).__init__("Hash calculation failed due to unknown error",
                                                        {'file_name': filepath,
                                                         'class_name': class_name,
                                                         'throwable': exc})


class RookBdbFailedException(RookMonitorException):
    def __init__(self, result):
        super(RookBdbFailedException, self).__init__("Failed to set breakpoint %s" % result, {'result': result})


class RookInvalidPositionException(RookException):
    def __init__(self, filename, line, alternatives):
        super(RookInvalidPositionException, self).__init__("Code position is not breakable: %s:%s" % (filename, line), {
            'filename': filename,
            'line': line,
            'alternatives': alternatives
        })


class RookBdbCodeNotFound(RookMonitorException):
    def __init__(self, filename):
        super(RookBdbCodeNotFound, self).__init__("Failed to find code object %s" % filename, {'filename': filename})


class RookBdbSetBreakpointFailed(RookMonitorException):
    def __init__(self, msg):
        super(RookBdbSetBreakpointFailed, self).__init__("Failed to set breakpoint! %s" % msg)


class RookAttributeNotFound(RookMonitorException):
    def __init__(self, attribute):
        super(RookAttributeNotFound, self).__init__("Failed to get attribute %s" % attribute, {'attribute': attribute})


class RookKeyNotFound(RookMonitorException):
    def __init__(self, key):
        super(RookKeyNotFound, self).__init__("Failed to get key %s" % key, {'key': key})


class RookMethodNotFound(RookMonitorException):
    def __init__(self, namespace_type, method):
        super(RookMethodNotFound, self).__init__("Namespace method not found %s" % method,
                                                 {'namespace': namespace_type.__name__,
                                                  'method': method})


class RookInvalidMethodArguments(RookMonitorException):
    def __init__(self, method, args):
        super(RookInvalidMethodArguments, self).__init__("Bad method arguments: method: %s, args %s" % (method, args),
                                                 {'method': method,
                                                  'arguments': args})


class RookWriteAttributeNotSupported(RookMonitorException):
    def __init__(self, namespace_type, attribute):
        super(RookWriteAttributeNotSupported, self).__init__("Namespace %s does not support write" % namespace_type.__name__,
                                                             {'namespace': namespace_type.__name__,
                                                              'attribute': attribute})


class RookOperationReadOnly(RookMonitorException):
    def __init__(self, operation_type):
        super(RookOperationReadOnly, self).__init__("Operation does not support write: %s" % operation_type.__name__,
                                                    {'operation': operation_type.__name__})


class RookRuleRateLimited(RookException):
    def __init__(self):
        super(RookRuleRateLimited, self).__init__("Breakpoint was disabled due to rate-limiting. "
                                                  "For more information: https://docs.rookout.com/docs/breakpoints-tasks.html#rate-limiting")


class RookRuleMaxExecutionTimeReached(RookException):
    def __init__(self):
        super(RookRuleMaxExecutionTimeReached, self).__init__("Breakpoint was disabled because it has reached its maximum execution time")


class RookNoHttpServiceRegistered(RookException):
    def __init__(self):
        super(RookNoHttpServiceRegistered, self).__init__("No http service registered")


class RookUnsupportedLocation(RookException):
    def __init__(self, location):
        super(RookUnsupportedLocation, self).__init__("Unsupported aug location was specified: %s" % location,
                                                      {'location': location})


class RookInterfaceException(RookException):
    def __init__(self, error_string):
        super(RookInterfaceException, self).__init__(error_string)


class RookVersionNotSupported(RookException):
    def __init__(self, error_string):
        super(RookVersionNotSupported, self).__init__(error_string)


class RookLoadError(RookException):
    def __init__(self, message):
        super(RookLoadError, self).__init__(message)


class RookMissingToken(RookException):
    def __init__(self):
        super(RookMissingToken, self).__init__('No Rookout token was supplied. '
                                               'Make sure to pass the Rookout Token when starting the rook')


class RookInvalidToken(RookException):
    def __init__(self, token):
        super(RookInvalidToken, self).__init__('The Rookout token supplied (%s...) is not valid; '
                                               'please check the token and try again' % token[:6])


class RookServiceMissing(RookException):
    def __init__(self, service):
        super(RookServiceMissing, self).__init__('Rookout service is missing',
                                                 {'service': service})


class RookInvalidOptions(RookException):
    def __init__(self, description):
        super(RookInvalidOptions, self).__init__(description)


class RookInvalidLabel(RookException):
    def __init__(self, label):
        super(RookInvalidLabel, self).__init__("Invalid label: must not start with the '$' character",
                                               {'label': label})


class RookNonPrimitiveObjectType(RookInputException):
    def __init__(self, path):
        super(RookNonPrimitiveObjectType, self).__init__(
            "Object %s must be of primitive type, such as: string, int, long etc" % path,
            {'path': path})


class RookExceptionEvaluationFailed(RookInputException):
    def __init__(self, expression):
        super(RookExceptionEvaluationFailed, self).__init__(
            "Failed to evaluate expression %s" % expression,
            {'expression': expression})


class RookSourceFileNotFound(RookInputException):
    def __init__(self, file_name):
        super(RookSourceFileNotFound, self).__init__(
            "Failed to find file %s" % file_name,
            {'file_name': file_name})


class RookDependencyError(RookException):
    def __init__(self, exc):
        super(RookDependencyError, self).__init__("%s, Make sure to run 'pip install rook' on the same platform/architecture. "
                                                  "For more information: https://docs.rookout.com/docs/sdk-setup.html#building-1" % exc,
                                                        {'throwable': exc})
