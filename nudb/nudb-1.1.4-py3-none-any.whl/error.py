class NudbException(Exception):
    def __init___(self, error_message):
        Exception.__init__(self, error_message)

class ParametersParseException(Exception):
    def __init___(self, error_message):
        Exception.__init__(self, error_message)
