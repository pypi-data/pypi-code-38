import logging

logger = logging.getLogger("stackifyapm.utils")


class TraceParent(object):
    __slots__ = ("version", "trace_id", "span_id")

    def __init__(self, version, trace_id, span_id):
        self.version = version
        self.trace_id = trace_id
        self.span_id = span_id

    @classmethod
    def from_string(cls, traceparent_string):
        try:
            parts = traceparent_string.split("-")
            version, trace_id, span_id = parts[:3]
        except ValueError:
            logger.debug("Invalid traceparent header format, value {}".format(traceparent_string))
            return
        try:
            version = int(version, 16)
            if version == 255:
                raise ValueError()
        except ValueError:
            logger.debug("Invalid version field, value {}".format(version))
            return

        return TraceParent(version, trace_id, span_id)
