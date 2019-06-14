# -*- coding: utf-8 -*-
# Copyright (c) 2017  Red Hat, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Written by Chenxiong Qi <cqi@redhat.com>


from threading import Lock
from sqlalchemy.orm import attributes

from logging import getLogger

log = getLogger()

_cache_lock = Lock()
_cached_composes = {}


def cache_composes_if_state_changed(session, flush_context):
    """Prepare outgoing messages when compose state is changed"""

    from odcs.server.models import Compose

    composes = (item for item in (session.new | session.dirty)
                if isinstance(item, Compose))
    composes_state_changed = (
        compose for compose in composes
        if not attributes.get_history(compose, 'state').unchanged)

    with _cache_lock:
        for comp in composes_state_changed:
            if comp.id not in _cached_composes:
                _cached_composes[comp.id] = []
            _cached_composes[comp.id].append(comp.json())

    log.debug('Cached composes to be sent due to state changed: %s',
              _cached_composes.keys())


def start_to_publish_messages(session):
    """Publish messages after data is committed to database successfully"""
    import odcs.server.messaging as messaging

    with _cache_lock:
        msgs = []
        for compose_jsons in _cached_composes.values():
            for compose_json in compose_jsons:
                msgs.append({
                    'event': 'state-changed',
                    'compose': compose_json,
                })
        log.debug('Sending messages: %s', msgs)
        if msgs:
            try:
                messaging.publish(msgs)
            except Exception:
                log.exception("Cannot publish message to bus.")
        _cached_composes.clear()
