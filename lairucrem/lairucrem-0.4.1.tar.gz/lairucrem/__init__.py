#! /usr/bin/env python
# Copyright (C) 2016 Alain Leufroy
#
# Author: Alain Leufroy <alain@leufroy.fr>
# Licence: WTFPL, grab your copy here: http://sam.zoy.org/wtfpl/
"""The lairucrem librairy."""

import contextlib
import imp

import urwid
from pkg_resources import DistributionNotFound, get_distribution

from . import config

__all__ = [
    'get_extension_path', 'get_main_loop', 'interrupt_mainloop', 'open_popup']

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    __version__ = 'From sources!'


_MAIN_LOOP = None


def get_extension_path():
    """Search for lairucrem mercurial extension file path and return it.

    The extension file is not loaded so, lazy import feature of
    mercurial is not activated.
    """
    path = __path__  # noqa: E0602
    fid, path = imp.find_module('extension', path)[:2]
    fid.close()
    return path


def _MAIN_WIDGET_FACTORY():
    return urwid.Filler(urwid.Text('default widget.'))


def _get_raw_main_loop():
    from .widgets.mainwidget import popuplauncher
    from urwid.raw_display import Screen
    screen = Screen()
    screen.set_terminal_properties(colors=256)
    screen.set_mouse_tracking()
    return urwid.MainLoop(
        popuplauncher(_MAIN_WIDGET_FACTORY()),
        event_loop=urwid.main_loop.AsyncioEventLoop(),
        screen=screen,
        palette=config.PALETTE, pop_ups=True)


def _get_main_loop():
    from . import patch_urwid
    if config.SCREEN == 'raw':
        return _get_raw_main_loop()
    elif config.SCREEN == 'curses':
        return _get_curses_main_loop()
    else:
        try:
            return _get_raw_main_loop()
        except OSError:
            return _get_curses_main_loop()


def get_main_loop():
    """Get, create if needed, the main loop."""
    global _MAIN_LOOP
    if _MAIN_LOOP:
        return _MAIN_LOOP
    _MAIN_LOOP = loop = _get_main_loop()
    return loop


def set_main_widget_policy(factory):
    """Set up the factory that builds the main widget.

    :factory: a callable returning an urwid box widget.
    """
    global _MAIN_WIDGET_FACTORY
    _MAIN_WIDGET_FACTORY = factory


def open_popup(widget):
    """Open a popup containing the given widget."""
    loop = get_main_loop()
    assert _MAIN_LOOP.widget, 'No main widget found.'
    popuplauncher = loop.widget
    popuplauncher.open_pop_up(widget)


@contextlib.contextmanager
def interrupt_mainloop():
    """Contextmanager inside which the mainloop is stopped."""
    loop = get_main_loop()
    loop.stop()
    loop.screen.stop()
    try:
        yield
    finally:
        loop.screen.start()
        loop.start()


def _get_curses_main_loop():    # noqa: C901
    """hugly workaround to make asyncio works with curses in urwid."""
    from .widgets.mainwidget import popuplauncher
    import urwid.main_loop
    import urwid.curses_display
    import functools
    import heapq
    import time
    import asyncio

    class mainloop(urwid.main_loop.MainLoop):

        def _run(self):
            self.start()
            asyncio.ensure_future(self._run_screen_event_loop_())
            try:
                self.event_loop.run()
            except Exception:
                self.screen.stop()  # clean up screen control
                raise
            self.stop()

        def start(self):
            self.screen.start()
            if self.handle_mouse:
                self.screen.set_mouse_tracking()
            self.idle_handle = self.event_loop.enter_idle(self.entering_idle)

        async def _run_screen_event_loop_(self, *, loop=None):
            """
            This method is used when the screen does not support using
            external event loops.

            The alarms stored in the SelectEventLoop in :attr:`event_loop`
            are modified by this method.
            """
            loop = loop or asyncio.get_event_loop()
            next_alarm = None
            while True:
                self.draw_screen()

                if not next_alarm and self.event_loop._alarms:
                    next_alarm = heapq.heappop(self.event_loop._alarms)

                keys = None
                while not keys:
                    if next_alarm:
                        sec = max(0, next_alarm[0] - time.time())
                        self.screen.set_input_timeouts(sec)
                    else:
                        self.screen.set_input_timeouts(None)
                    keys, raw = await loop.run_in_executor(
                        None, functools.partial(
                            self.screen.get_input, True))
                    if not keys and next_alarm:
                        sec = next_alarm[0] - time.time()
                        if sec <= 0:
                            break

                keys = self.input_filter(keys, raw)

                if keys:
                    self.process_input(keys)

                while next_alarm:
                    sec = next_alarm[0] - time.time()
                    if sec > 0:
                        break
                    tm, callback = next_alarm
                    callback()

                    if self.event_loop._alarms:
                        next_alarm = heapq.heappop(self.event_loop._alarms)
                    else:
                        next_alarm = None

                if 'window resize' in keys:
                    self.screen_size = None

    class screen(urwid.curses_display.Screen):
        hook_event_loop = None

    class eventloop(urwid.main_loop.AsyncioEventLoop):

        def __init__(self, **kwargs):
            self._alarms = []
            self._select_handles = {}
            super().__init__(**kwargs)

        def alarm(self, seconds, callback):
            _handle = urwid.main_loop.SelectEventLoop.alarm(
                self, seconds, callback)

            def cb():
                out = callback()
                urwid.main_loop.SelectEventLoop.remove_alarm(self, _handle)
                return out

            handle = urwid.main_loop.AsyncioEventLoop.alarm(self, seconds, cb)
            self._select_handles[handle] = _handle
            return handle

        def remove_alarm(self, handle):
            _handle = self._select_handles[handle]
            urwid.main_loop.SelectEventLoop.remove_alarm(self, _handle)
            return urwid.main_loop.AsyncioEventLoop.remove_alarm(self, handle)

    return mainloop(
        popuplauncher(_MAIN_WIDGET_FACTORY()),
        event_loop=eventloop(),
        screen=screen(),
        palette=config.PALETTE, pop_ups=True)
