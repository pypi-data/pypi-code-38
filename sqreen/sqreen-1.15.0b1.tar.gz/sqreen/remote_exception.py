# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Remote exception module
"""
import traceback


def traceback_formatter(backtrace):
    """ Accept a backtrace in the format of traceback.extract_tb or
    traceback.extract_stack and returns a list of dictionary matching this
    format::

    {
        'file': FILENAME,
        'line_number': LINE_NUMBER,
        'method': FUNCTION_NAME
    }
    """
    frames = []
    for frame in backtrace:
        filename, line_number, function_name, _ = frame
        frames.append(
            {
                "file": filename,
                "line_number": line_number,
                "method": function_name,
            }
        )
    return frames


def raw_traceback_formatter(raw_backtrace):
    """ Accept a traceback object, convert it to a traceback and returns the
    same format than backtrack_formatter.
    """
    return traceback_formatter(traceback.extract_tb(raw_backtrace))


class RemoteException(object):
    def __init__(
        self,
        exc_info,
        callback_payload=None,
        exception_payload=None,
        request_payload=None,
        stack=None,
    ):
        self.exception_class = exc_info[0].__name__
        self.exception_msg = str(exc_info[1])
        self.raw_backtrace = exc_info[2]
        self.backtrace = raw_traceback_formatter(self.raw_backtrace)

        self.stack = None
        if stack is not None:
            self.stack = traceback_formatter(stack)
            self.backtrace = self.stack + self.backtrace

        if callback_payload is None:
            callback_payload = {}
        self.callback_payload = callback_payload

        self.exception_payload = exception_payload
        self.request_payload = request_payload

    def to_dict(self):
        """ Returns information about exception, backtrace and request merged
        into initial payload
        """
        base_payload = {"infos": {}}

        # Base fields
        base_payload["rule_name"] = self.callback_payload.pop(
            "rule_name", None
        )
        base_payload["rulespack_id"] = self.callback_payload.pop(
            "rulespack_id", None
        )
        base_payload["rule_signature"] = self.callback_payload.pop(
            "rule_signature", None
        )

        if self.callback_payload:
            base_payload["infos"]["callback"] = self.callback_payload

        if self.exception_payload:
            base_payload["infos"]["exception"] = self.exception_payload

        if self.request_payload:
            base_payload.update(self.request_payload)

        base_payload.update(
            {
                "klass": self.exception_class,
                "message": self.exception_msg,
                "context": {"backtrace": self.backtrace},
            }
        )

        return base_payload
