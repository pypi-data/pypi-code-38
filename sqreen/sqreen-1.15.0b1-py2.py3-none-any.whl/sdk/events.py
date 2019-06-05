# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#

import logging
import traceback
from datetime import datetime

from ..runtime_storage import runtime
from ..utils import is_string

LOGGER = logging.getLogger(__name__)


_SQREEN_EVENT_PREFIX = "sq."

_TRACK_OPTIONS_FIELDS = frozenset(
    ["properties", "user_identifiers", "timestamp"]
)

_TRACK_PAYLOAD_SECTIONS = ("request", "response", "params", "headers")

STACKTRACE_EVENTS = set()

_MAX_EVENT_PROPERTIES = 16


def _track_unsafe(event, options, storage=runtime):
    """Track an SDK event.

    This function is used internally in the agent to send built-in SDK events,
    e.g. output of security actions. It does not perform any check and is not
    exposed to the user.
    """
    if "timestamp" not in options:
        options = dict(options)
        options["timestamp"] = datetime.utcnow()
    storage.observe(
        "sdk",
        ["track", options["timestamp"], event, options],
        payload_sections=_TRACK_PAYLOAD_SECTIONS,
        report=True,
    )
    return True


def track(event, options=None, storage=runtime):
    """Track an SDK event."""
    # Check event type.
    if not is_string(event):
        raise TypeError(
            "event name must be a string, not {}".format(
                event.__class__.__name__
            )
        )
    # Check event name.
    if event.startswith(_SQREEN_EVENT_PREFIX):
        LOGGER.warning(
            "Event names starting with %r are reserved, "
            "event %r has been ignored",
            _SQREEN_EVENT_PREFIX,
            event,
        )
        return False
    if options is None:
        options = {}
    else:
        options = dict(options)
    # Check option keys.
    for option_key in list(options):
        if option_key not in _TRACK_OPTIONS_FIELDS:
            LOGGER.warning("Invalid option key %r, skipped", option_key)
            del options[option_key]
    timestamp = options.get("timestamp")
    if timestamp and not isinstance(timestamp, datetime):
        raise TypeError(
            "timestamp option must be a datetime object, not {}".format(
                event.__class__.__name__
            )
        )
    properties = options.get("properties")
    # Check the number of properties.
    if properties and len(properties) > _MAX_EVENT_PROPERTIES:
        LOGGER.warning(
            "Event %r has %d properties, "
            "only the first %d ones will be reported",
            event,
            len(properties),
            _MAX_EVENT_PROPERTIES,
        )
        options["properties"] = dict(
            sorted(properties.items())[:_MAX_EVENT_PROPERTIES]
        )
    # Store stacktrace if required.
    if event in STACKTRACE_EVENTS:
        LOGGER.debug("Stacktrace recorded by for event %s", event)
        options["stacktrace"] = traceback.format_stack()
    return _track_unsafe(event, options, storage=storage)


def track_action(action, output, storage=runtime):
    """Track an action output."""
    if not action.send_response:
        return
    return _track_unsafe(
        "sq.action.{}".format(action.name),
        {"properties": {"output": output, "action_id": action.iden}},
        storage=storage,
    )
