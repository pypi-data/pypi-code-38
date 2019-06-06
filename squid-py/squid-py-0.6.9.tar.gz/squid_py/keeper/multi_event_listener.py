#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

import logging
import time

from datetime import datetime
from threading import Thread, RLock

from squid_py.keeper.contract_handler import ContractHandler
from squid_py.keeper.event_filter import EventFilter

logger = logging.getLogger(__name__)


class MultiEventListener(object):
    """Class representing an event listener."""

    def __init__(self, contract_name, event_name, from_block='latest', to_block='latest',
                 filter_key=None):
        contract = ContractHandler.get(contract_name)
        self.event_name = event_name
        self.event = getattr(contract.events, event_name)
        self.filter_key = filter_key
        self.from_block = from_block
        self.to_block = to_block
        self._timeout = 60  # seconds
        self._stopped = True
        self._event_filters = dict()
        self._pinned_events = dict()
        self._lock = RLock()

    def make_event_filter(self, filter_key, filter_value):
        """Create a new event filter."""
        event_filter = EventFilter(
            self.event_name,
            self.event,
            {filter_key: filter_value},
            from_block=self.from_block,
            to_block=self.to_block
        )
        event_filter.set_poll_interval(0.5)
        return event_filter

    def add_event_filter(self, filter_key, filter_value, callback, timeout_callback,
                         args, timeout, start_time=None, pin_event=False):
        if self.filter_key is not None:
            assert filter_key == self.filter_key, f'This events watcher is restricted to work ' \
                                                  f'with filter key {self.filter_key}.'

        event_filter = self.make_event_filter(filter_key, filter_value)
        if not pin_event:
            if not timeout:
                timeout = self._timeout

            if not start_time:
                start_time = int(datetime.now().timestamp())

        with self._lock:
            events_dict = self._pinned_events if pin_event else self._event_filters
            events_dict[(filter_key, filter_value)] = (
                (event_filter, callback, timeout_callback, args, timeout, start_time)
            )
            if self.is_stopped():
                self.start_watching()

    def is_stopped(self):
        return self._stopped

    def stop_watching(self):
        with self._lock:
            self._stopped = True

    def start_watching(self):
        t = Thread(
            target=self.watch_events,
            daemon=True,
        )
        with self._lock:
            self._stopped = False
            t.start()

    def watch_events(self):
        while True:
            try:
                if self.is_stopped():
                    return

                with self._lock:
                    filters = self._event_filters.copy()
                    filters.update(self._pinned_events.copy())

                for (key, value), \
                    (event_filter, callback, timeout_callback, args, timeout, start_time) \
                        in filters.items():

                    try:
                        done = self.process_event(
                            event_filter,
                            callback,
                            timeout_callback,
                            timeout,
                            args,
                            start_time)
                    except Exception as e:
                        logger.error(f'Error processing event: {str(e)}', exc_info=1)
                        done = True

                    if done:
                        with self._lock:
                            if (key, value) in self._event_filters:
                                self._event_filters.pop((key, value))

                    time.sleep(0.05)

            except Exception as e:
                logger.debug(f'Error processing event: {str(e)}')

            time.sleep(0.05)
            with self._lock:
                if not self._pinned_events and not self._event_filters:
                    self._stopped = True
                    break

    @staticmethod
    def process_event(event_filter, callback, timeout_callback, timeout, args,
                      start_time=None):
        """
        Start to watch one event.

        :param event_filter:
        :param callback:
        :param timeout_callback:
        :param timeout:
        :param args:
        :param start_time:
        :return:
        """
        try:
            events = event_filter.get_new_entries()
            if events and events[0] is not None:
                callback(events[0], *args)
                return True

        except (ValueError, Exception) as err:
            # ignore error, but log it
            # logger.error(f'Got error grabbing keeper events: {str(err)}', exc_info=1)
            pass

        if timeout:
            elapsed = int(datetime.now().timestamp()) - start_time
            if elapsed > timeout:
                if timeout_callback:
                    timeout_callback(*args)
                else:
                    callback(None, *args)

                return True

        return False
