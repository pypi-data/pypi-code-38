class TracerCollectedException(Exception):
    """Ошибка в приложении, перехватывается трасером"""


class TracerCollectedHTTPException(TracerCollectedException):
    """Ошибка в приложении, код ошибки протокола в HTTP заколовке, перехватывается трасером"""
    def __init__(self, msg, error_code):
        self.error_code = error_code
        self.msg = msg
        super().__init__(self, msg)

    def __str__(self):
        return repr(self.msg)


class TracerCollectedApplicationException(TracerCollectedException):
    """Ошибка в приложении, код ошибки приложения в JSON, перехватывается трасером"""


class ProcessorInitNoneOrWrongTypeVariant(Exception):
    """Variant is not found in provided VariantSchemaMaster
    dependencies"""


class ProcessorInitWrongTypeCustomSchema(Exception):
    """Provided Custom Schema is of wrong type"""


class ProcessorExtractCantSetDestinationAttr(Exception):
    """Invalid destination"""


class NoSpanException(Exception):
    """Attempt to process span without span itself, skipping"""


class SpanIsNotStartedException(Exception):
    """Attempt to fill in or finish span that has not been started"""


class SpanNoParentException(Exception):
    """Outgoing point without parent span,
        it's no error just a normal case flow
    """


class SpanNoStageForMethod(Exception):
    """Method decorated as stage-bound has no stage linked
    """


class HTTPPathSkip(Exception):
    """Skip HTTP path, it's no error just an option"""


class TornadoNotAvailable(Exception):
    """use_tornado_loop does not work without Tornado dependency installed"""


class FuckFuckFuck(Exception):
    """test error"""
