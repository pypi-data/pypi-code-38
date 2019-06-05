# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
"""Helper classes for runtime storage."""

import threading

import pkg_resources

from .payload_creator import PayloadCreator
from .request_recorder import RequestRecorder
from .utils import HAS_ASYNCIO

if HAS_ASYNCIO:
    from . import async_context


class RuntimeStorage(object):
    """Runtime storage objects."""

    def __init__(self, store=None):
        if store is None:
            store = _ThreadLocalStore()
        self.store = store
        # Let's not set store attributes here: the event loop may not be
        # started yet.
        self.payload_creator = PayloadCreator()
        self.attack_http_code = 403

    def store_request(self, request):
        """Store a request."""
        self.store.set("current_request", request)
        request_recorder = self.store.get("request_recorder")
        if request_recorder is None:
            # First request.
            request_recorder = RequestRecorder()
            self.store.set("request_recorder", request_recorder)
        self.store.delete("whitelist_match")

    def store_request_default(self, request):
        """Store a request, unless a request is already stored."""
        current_request = self.get_current_request()
        if current_request is None:
            self.store_request(request)

    def get_current_request(self):
        """Return the request currently processed.

        Return None if no request is stored.
        """
        return self.store.get("current_request")

    def clear_request(self, queue=None, observation_queue=None):
        """Clear the stored request."""
        current_request = self.store.delete("current_request")
        current_response = self.store.delete("current_response")
        if current_request is None:
            return
        if queue is None and observation_queue is None:
            # Only for tests and retrocompatibility.
            return
        request_recorder = self.store.get("request_recorder")
        request_recorder.flush(
            current_request, current_response,
            self.payload_creator, queue, observation_queue
        )
        self.store.delete("whitelist_match")

    def store_response(self, response):
        """Store a response."""
        self.store.set("current_response", response)

    def get_current_response(self):
        """Returns the current response or None."""
        return self.store.get("current_response")

    def clear_response(self, response):
        """Clear the stored response."""
        self.store.delete("current_response")

    def observe(self, *args, **kwargs):
        request_recorder = self.store.get("request_recorder")
        if request_recorder is None:
            request_recorder = RequestRecorder()
            self.store.set("request_recorder", request_recorder)
        request_recorder.observe(*args, **kwargs)

    def get_whitelist_match(self, runner_settings):
        """Return the whitelisted path or IP matching the current request.

        Return None if the request is not whitelisted.
        """
        # None is a valid value, so let's default to False when not defined.
        whitelist_match = self.store.get("whitelist_match", False)
        if whitelist_match is not False:
            return whitelist_match
        current_request = self.get_current_request()
        if current_request is None:
            whitelist_match = None
        else:
            whitelist_match = runner_settings.whitelist_match(current_request)
        self.store.set("whitelist_match", whitelist_match)
        return whitelist_match

    def store_current_args(self, binding_accessor):
        """For daemon only: store the faked list of arguments."""
        args = {}
        for name, value in binding_accessor.items():
            if name.find("#.args[") == 0:
                idx = int(name[7 : name.rindex("]")])
                args[idx] = value
            elif name.find("#.cargs[") == 0:
                idx = int(name[8 : name.rindex("]")])
                args[idx] = value
        if args:
            self.store.set(
                "arguments", [args.get(i) for i in range(max(args) + 1)]
            )
        else:
            self.store.set("arguments", [])

    def get_current_args(self, args=None):
        """For daemon only: get the faked list of arguments."""
        return self.store.get("arguments", args)

    def store_cmd_arguments(self, cmd_args):
        """Alternative of store_current_args that doesn't destroy data"""
        self.store.set("cmd_args", cmd_args)

    def get_cmd_arguments(self):
        """dict ba expr -> its resolution by the extension"""
        return self.store.get("cmd_args")


class _ThreadLocalStore(object):
    """Wrap a threading.local object into a store interface."""

    def __init__(self):
        self.local = threading.local()

    def get(self, key, default=None):
        """Return the value associated to the key.

        Fallback to default if the key is missing.
        """
        return getattr(self.local, key, default)

    def set(self, key, value):
        """Map a key to a value."""
        setattr(self.local, key, value)

    def setdefault(self, key, value):
        """If a key is not set, map it to a value."""
        self.local.__dict__.setdefault(key, value)

    def delete(self, key):
        """Delete a key."""
        return self.local.__dict__.pop(key, None)


_THREADED_FRAMEWORKS = ("Django", "Flask", "pyramid")

_ASYNC_FRAMEWORKS = ("aiohttp",)


def _get_store():
    """Return a store object suited for the current framework."""
    if HAS_ASYNCIO:
        pkg_names = set(
            pkg_info.project_name for pkg_info in pkg_resources.working_set
        )
        for framework in _THREADED_FRAMEWORKS:
            if framework in pkg_names:
                return _ThreadLocalStore()
        for framework in _ASYNC_FRAMEWORKS:
            if framework in pkg_names:
                return async_context
    return _ThreadLocalStore()


def get_runtime_storage():
    """Return a runtime storage instance suited for the current framework."""
    return RuntimeStorage(_get_store())


runtime = get_runtime_storage()
