# Copyright 2011-2014 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from enum import Enum
from typing import Callable
from logging import Handler, LogRecord


class EventType(Enum):
    job_updated = 'job_updated'
    run_started = 'run_started'
    run_finished = 'run_finished'
    log_record_emitted = 'log_record_emitted'


EVENT_LISTENERS = {x: [] for x in EventType}


def register_listener(event_type: EventType, function: Callable[[object], None]):
    """
    Register a listeners to a specific event type

    :param event_type: The EventType to listen on
    :param function: The callable that will be called on each event
    """
    if event_type not in EventType:
        raise ValueError('Trying to register listener to invalid event type: {}'.format(event_type))

    if function not in EVENT_LISTENERS[event_type]:
        EVENT_LISTENERS[event_type].append(function)


def remove_listener(event_type: EventType, function: Callable[[object], None]):
    """
    Remove a listeren from a type of event

    :param event_type: The event type to remove the listeners from
    :param function: The function to remove
    """
    while function in EVENT_LISTENERS[event_type]:
        EVENT_LISTENERS[event_type].remove(function)


def emit_event(event_type: EventType, data):
    """
    Emit an event to all listeners
    :param event_type: The type of event to emit
    :param data: The data object to send along
    """
    for listener in EVENT_LISTENERS[event_type]:
        listener(data)


class FastrLogEventHandler(Handler):
    """
    Logging handler that sends the log records into the event system
    """
    def emit(self, record: LogRecord):
        emit_event(EventType.log_record_emitted, record)

