class EvaluationError(Exception):
    def __init__(self, message, errorCode):
        super(EvaluationError, self).__init__(message)
        self.errorCode = errorCode