# -*- coding: utf-8 -*-
# Copyright (c) 2019 Dzmitry Maliuzhenets; MIT License

"""The functionality associated with requests to Telegram Bot Api."""

import jsonpickle

from telegrambotapiwrapper import utils


def json_payload(args: dict) -> str:
    """Get the string containing the object to send to Telegram Bot Api.

    Args:
        args(dict): data dictionary to send
    Returns:
        (str): a json-string containing the object to be sent to Telegram Bot
            Api.
    """

    def remove_none_values(d):
        """Delete None values."""
        if not isinstance(d, (dict, list)):
            return d
        if isinstance(d, list):
            return [remove_none_values(v) for v in d]
        return {
            k: remove_none_values(v)
            for k, v in d.items() if v is not None
        }

    jstr = jsonpickle.encode(args, unpicklable=False)
    py_obj = jsonpickle.decode(jstr)
    py_obj = remove_none_values(py_obj)
    py_obj = utils.replace_from__word(py_obj)
    jstr = jsonpickle.dumps(py_obj)
    return jstr
