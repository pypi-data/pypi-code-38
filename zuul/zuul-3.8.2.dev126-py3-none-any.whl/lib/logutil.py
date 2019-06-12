# Copyright 2019 BMW Group
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import logging


def get_annotated_logger(logger, event, build=None):
    # Note(tobiash): When running with python 3.5 log adapters cannot be
    # stacked. We need to detect this case and modify the original one.
    if isinstance(logger, EventIdLogAdapter):
        extra = logger.extra
    else:
        extra = {}

    if event is not None:
        if hasattr(event, 'zuul_event_id'):
            extra['event_id'] = event.zuul_event_id
        else:
            extra['event_id'] = event

    if build is not None:
        extra['build'] = build

    if isinstance(logger, EventIdLogAdapter):
        return logger

    return EventIdLogAdapter(logger, extra)


class EventIdLogAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        msg, kwargs = super().process(msg, kwargs)
        extra = kwargs.get('extra', {})
        event_id = extra.get('event_id')
        build = extra.get('build')
        new_msg = []
        if event_id is not None:
            new_msg.append('[e: %s]' % event_id)
        if build is not None:
            new_msg.append('[build: %s]' % build)
        new_msg.append(msg)
        msg = ' '.join(new_msg)
        return msg, kwargs
