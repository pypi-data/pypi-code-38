"""Parsing client for symbol_please."""
import asyncio
import logging
import queue

from .line import LogLine
from .spell import SpellEventHandler

_LOGGER = logging.getLogger(__name__)


class ParserClient():
    """The client that reads log lines and manages state."""

    def __init__(self, config):
        """Create the parser client."""
        self.config = config
        self.level = int(self.config['level'])
        self._event_listeners_thread = set()
        self._last_line_id = 0
        self._event_handlers = set()

    def add_event_listener_thread(self):
        """Returns a thread-safe queue which will emit log events."""
        listener = queue.Queue()
        self._event_listeners_thread.add(listener)
        return listener

    def remove_event_listener_thread(self, listener):
        """Deregister a listener thread if it is no longer needed."""
        self._event_listeners_thread.remove(listener)

    def parse_raw_line(self, raw_line):
        """Parse a raw line of input."""
        self._last_line_id += 1
        line_id = self._last_line_id
        try:
            line = LogLine(raw_line, line_id)
        except ValueError as ex:
            _LOGGER.warning("Unable to parse log line '%s'", line, exc_info=ex)
            return

        _LOGGER.debug("Parsing log line: '%s'", line)
        for handler in self._event_handlers:
            if handler.line_queue is None:
                continue
            handler.line_queue.put_nowait(line)

        new_handlers = SpellEventHandler.create_events(self, line)
        if new_handlers:
            self._event_handlers = self._event_handlers.union(new_handlers)
            for handler in new_handlers:
                asyncio.ensure_future(self.run_handler(handler))

    async def run_handler(self, handler):
        """Run the given handler, and deregister when complete."""
        try:
            await handler.run()
        finally:
            self._event_handlers.remove(handler)

    def send_event(self, event):
        """Send an event to registered listeners."""
        _LOGGER.info("Sending event %s", event)
        for handler in self._event_handlers:
            if handler.event_queue is None:
                continue
            handler.event_queue.put_nowait(event)

        for thread_listener in self._event_listeners_thread.copy():
            thread_listener.put_nowait(event)
