import logging

from .backend_logging import add_backend_specific_logs
from .logging_types import LogType


class KWLogger(logging.LoggerAdapter):

    def __init__(self, name, extra_tags=None):
        self.extra_tags = extra_tags or []
        self.warn = self.warning
        return super(KWLogger, self).__init__(name, {})

    def __getattr__(self, item):
        # in case we don't have a function, delagate it to the logger
        return getattr(self.logger, item)

    def process(self, msg, kwargs):
        return msg, self._handle_rookout_kwargs(msg, kwargs)

    def _handle_rookout_kwargs(self, msg, kwargs):
        rookout_extra = {"extraTags": self.extra_tags} if self.extra_tags else {}
        extra = kwargs.get("extra") or {}
        add_backend_specific_logs(kwargs)
        if "rookout_kw_log" in extra:
            # This allow us to have both normal formatted msgs in local mode, and a json version in kubernetes
            kwargs = extra
            del kwargs["rookout_kw_log"]
        for k, v in kwargs.items():
            if k == "exc_info":
                #Same logic as in the original debugger
                continue
            if k == "extra":
                rookout_extra.update(v)
            else:
                field_type = LogType.get_type(k)
                if field_type:
                    self.convert_value_to_type(field_type, k, rookout_extra, v)
                else:
                    rookout_extra["kw_errors"] = rookout_extra.get("kw_errors", []) + [
                        "Missing Kw field: {}".format(k)]

        if not rookout_extra:
            return kwargs

        return {"extra": {"rookout_extra": rookout_extra}}

    def convert_value_to_type(self, field_type, k, rookout_extra, v):
        try:
            rookout_extra[k] = field_type(v)
        except Exception as e:
            rookout_extra["kw_errors"] = rookout_extra.get("kw_errors", []) + [
                "Error convert field {}".format(v)]
