"""fix urwid bug."""
import sys

from urwid import ExitMainLoop
from urwid.main_loop import AsyncioEventLoop
from urwid.raw_display import Screen

from .utils import monkeypatch


# https://github.com/urwid/urwid/issues/221
@monkeypatch(Screen, 'hook_event_loop')
def fix_issue_221(self, event_loop, callback):
    """
    Register the given callback with the event loop, to be called with new
    input whenever it's available.  The callback should be passed a list of
    processed keys and a list of unprocessed keycodes.

    Subclasses may wish to use parse_input to wrap the callback.
    """
    if hasattr(self, 'get_input_nonblocking'):
        wrapper = self._make_legacy_input_wrapper(event_loop, callback)
    else:
        wrapper = lambda: self.parse_input(
            event_loop, callback, self.get_available_raw_input())
    fds = self.get_input_descriptors()
    handles = [
        event_loop.watch_file(fd, wrapper)
        for fd in fds]
    self._current_event_loop_handles = handles

# Fix exception handling
# https://github.com/urwid/urwid/pull/92 exists but not merged


@monkeypatch(AsyncioEventLoop)
def _exception_handler(self, loop, context):
    exc = context.get('exception')
    if exc:
        if not isinstance(exc, ExitMainLoop):
            self._exc = exc
        else:
            loop.default_exception_handler(context)
        loop.stop()


@monkeypatch(AsyncioEventLoop)
def run(self):
    """
    Start the event loop.  Exit the loop when any callback raises
    an exception.  If ExitMainLoop is raised, exit cleanly.
    """
    self._loop.set_exception_handler(self._exception_handler)
    self._loop.run_forever()
    if getattr(self, '_exc', None):
        raise self._exc
