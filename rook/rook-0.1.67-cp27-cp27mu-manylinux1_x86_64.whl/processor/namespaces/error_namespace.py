from .namespace import Namespace


class ErrorNamespace(Namespace):

    def __init__(self, message, parameters, exception_namespace, traceback_namespace):
        super(ErrorNamespace, self).__init__()
        self.message = message
        self.parameters = parameters
        self.exc = exception_namespace
        self.traceback = traceback_namespace

    def to_dict(self):
        return {
            u'@namespace': self.__class__.__name__,
            u'@common_type': Namespace.__name__,
            u'@value': {
                u'message': self.message.obj,
                u'parameters': self.parameters.to_dict(),
                u'exc': self.exc.to_dict()
            }}

    def to_simple_dict(self):
        return {u'message': self.message.obj, u'parameters': self.parameters.to_simple_dict(), u'exc': self.exc.to_simple_dict()}
