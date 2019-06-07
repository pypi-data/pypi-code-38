# -*- coding: utf-8 -*-
# Copyright (c) 2003-2012 LOGILAB S.A. (Paris, FRANCE).
# http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Application utilities.
"""
import threading
import logging
import sys

from urwid import AttrWrap, MainLoop, VERSION as URWID_VERSION

from hgviewlib.application import HgViewApplication, ApplicationError
from hgviewlib.curses.hgrepoviewer import RepoViewer
from hgviewlib.curses import MainFrame, emit_command, activate_delayed_signals

try:
    import pygments
    from pygments.token import Token, _TokenType
except ImportError:
    # pylint: disable=C0103
    pygments = None
    # pylint: enable=C0103
# _________________________________________________________________ Application

class HgViewUrwidApplication(HgViewApplication):
    """
    HgView application using urwid.
    """
    HgRepoViewer = RepoViewer

    def __init__(self, *args, **kwargs):
        super(HgViewUrwidApplication, self).__init__(*args, **kwargs)
        self.viewer = AttrWrap(self.viewer, 'body')
        mainframe = MainFrame('repoviewer', self.viewer)
        screen = self.get_screen()
        self.mainloop = MainLoop(mainframe, PALETTE, screen)
        connect_logging(self.mainloop, level=logging.DEBUG)
        mainframe.register_commands()
        self.enable_inotify()
        activate_delayed_signals(self.mainloop)
        self.mainframe = mainframe

#        register_command('alarm', 'process callback in a given seconds',

    def get_screen(self):
        """return the screen instance to use"""
        if self.opts.interface == 'curses' and URWID_VERSION < (1, 0, 0):
            raise ApplicationError('The "curses" interface can not be used '
                                   'with old installed urwid version '
                                   '%s < 1.0.0. Use the "raw" interface'
                                   % (URWID_VERSION, ))
        if self.opts.interface == 'raw':
            from urwid.raw_display import Screen
        elif self.opts.interface == 'curses':
            from urwid.curses_display import Screen

        if pygments:
            return patch_screen(Screen)()
        return Screen()

    def enable_inotify(self):
        """enable inotify watching"""
        enable_inotify = True # XXX config
        optimize_inotify = True # XXX config
        if enable_inotify:
            if optimize_inotify:
                import ctypes.util
                orig = ctypes.util.find_library
                ctypes.util.find_library = lambda lib: None # dirty optimization
            inotify(self.mainloop)
            if optimize_inotify:
                ctypes.util.find_library = orig

    def exec_(self):
        '''main entry point'''
        if '--profile' in sys.argv or '--time' in sys.argv:
            self.mainloop._run = self.mainloop.draw_screen
        out = self.mainloop.run()
        self.mainframe.unregister_commands()
        return out

# _____________________________________________________________________ inotify
def inotify(mainloop):
    """add inotify watcher to the mainloop"""
    try:
        from hgviewlib.inotify import Inotify as Inotify
    except ImportError:
        return

    class UrwidInotify(Inotify):
        """Inotify handler that can be connected to as urwid mainloop."""
        def __init__(self, *args, **kwargs):
            super(UrwidInotify, self).__init__(*args, **kwargs)
            self._input_timeout = None

        def process_finally(self):
            """Really process the inotify event"""
            self._input_timeout = None
            super(UrwidInotify, self).process()

        def process_on_any_event(self):
            """Process all inotify events and prevent over-processing"""
            # get all events on every files.
            # Ignore files that shall be ignored be mercurial
            # Also ignore hg-checkexec* files that are created by mercurial
            # to check available file status.
            for fname in self.read_events():
                if fname.startswith(('hg-checkexec', 'hg-checklink')):
                    break
                if self.repo.dirstate._dirignore(fname):
                    break
            else:
            # use the urwid mainloop to schedule the screen refreshing in 0.2s
            # and ignore events received during this time.
            # It prevents over-refreshing (See ../inotify.py comments).
                if self._input_timeout is None:
                    self._input_timeout = mainloop.set_alarm_in(
                            0.2, lambda *args: self.process_finally())
    try:
        refresh = lambda: emit_command('refresh')
        inot = UrwidInotify(mainloop.widget.get_body().repo, refresh)
    except:
        return
    mainloop.event_loop.watch_file(inot.get_fd(), inot.process_on_any_event)
    # add watchers thought a thread to reduce start duration with a big repo
    threading.Thread(target=inot.update).start()

# ________________________________________________________________ patch screen
def patch_screen(screen_cls):
    """
    Return a patched screen class that allows parent token inheritance in
    the palette
    """
    class Palette(dict):
        """Special dictionary that take into account parent token inheritance.
        """
        def __contains__(self, key):
            if super(Palette, self).__contains__(key):
                return True
            if (not isinstance(key, _TokenType)) or (key.parent is None):
                return False
            if key.parent in self: # function is now recursive
                self[key] = self[key.parent] # cache + __getitem__ ok
                return True
            return False
        has_key = __contains__

    class PatchedScreen(screen_cls, object):
        """hack Screen to allow parent token inheritance in the palette"""
        # Use a special container for storing style definition. This container
        # take into account parent token inheritance
        # raw_display.Screen store the palette definition in the container
        # ``_pal_escape``, web_display and curses display in ``palette`` and
        # ``attrconv``

        def __init__(self, *args):
            self._hgview_palette = None
            self._hgview_attrconv = None
            # mro problem with web_display, so do not use super
            screen_cls.__init__(self)


        def _hgview_get_palette(self):
            """Return the palette"""
            return self._hgview_palette
        def _hgview_set_palette(self, value):
            """Set the palette"""
            self._hgview_palette = Palette()
            if value:
                self._hgview_palette.update(value)
        # pylint: disable=E0602
        _pal_escape = property(_hgview_get_palette, _hgview_set_palette)
        palette = _pal_escape

        def _hgview_get_attrconv(self):
            """Return the palette"""
            return self._hgview_attrconv
        def _hgview_set_attrconv(self, value):
            """Set the palette"""
            self._hgview_attrconv = Palette()
            if value:
                self._hgview_attrconv.update(value)
        # pylint: disable=E0602
        attrconv = property(_hgview_get_attrconv, _hgview_set_attrconv)
    return PatchedScreen

# _____________________________________________________________________ logging
def connect_logging(mainloop, level=logging.INFO):
    '''Connect logging to the hgview console application.
    (The widget of the mainloop must be a ``MainFrame`` instance)

    You may add 'DEBUG', 'WARNING', 'ERROR' and 'CRITICAL' styles in the
    palette.
    '''
    class ConsoleHandler(logging.Handler):
        '''Handler for logging to the footer of a ``MainFrame`` instance.

        You shall prefer to link logging and you application by using the
        ``connect_logging(...)`` function.
        '''
        def __init__(self, callback, redraw, redraw_levelno=logging.CRITICAL):
            """
            :param callback: A function called to display a message as
                ``callback(style, levelname, message)`` where:

                * ``levelname`` is the name of the message level
                * ``message`` is the message to display

                Mostly, it is the ``set`` method of a ``Footer`` instance.

            :param redraw: a function that performs the screen redrawing

            """
            self.callback = callback
            self.redraw = redraw
            self.redraw_levelno = redraw_levelno
            logging.Handler.__init__(self)

        def emit(self, record):
            """emit a record"""
            if isinstance(record.msg, list): # urwid style
                name = 'default'
                msg = record.msg
            else:
                name = record.levelname
                msg = self.format(record)
            self.callback(name, msg)
            if record.levelno >= self.redraw_levelno:
                self.flush()

        def flush(self):
            try:
                self.redraw()
            except AssertionError:
                pass

    logger = logging.getLogger()
    logger.setLevel(level)
    display = lambda style, msg: mainloop.widget.footer.set(style, msg, '')
    handler = ConsoleHandler(display, mainloop.draw_screen)
    logger.addHandler(handler)

# ________________________________________________________________ patch screen
PALETTE = [
    ('default','default','default'),
    ('body','default','default', 'standout'),
    ('banner','black','light gray', 'bold'),
    ('focus','black','dark cyan', 'bold'),
    ('focus.alternate','black','dark magenta', 'bold'),
    ('current', 'black', 'dark green', 'bold'),
    ('modified', 'black', 'brown', 'bold'),

    # logging
    ('DEBUG', 'dark magenta', 'default'),
    ('INFO', 'dark gray', 'default'),
    ('WARNING', 'brown', 'default'),
    ('ERROR', 'dark red', 'default'),
    ('CRITICAL', 'light red', 'default'),

    # graphlog
    ('ID', 'brown', 'default', 'standout'),
    ('Log', 'default', 'default'),
    ('GraphLog', 'default', 'default', 'bold'),
    ('GraphLog.node', 'default', 'default', 'bold'),
    ('Author', 'dark blue', 'default', 'bold'),
    ('Date', 'dark green', 'default', 'bold'),
    ('Tags', 'yellow', 'dark red', 'bold'),
    ('Bookmarks', 'default', 'dark blue'),
    ('Branch', 'yellow', 'default', 'bold'),
    ('Filename', 'white', 'default', 'bold'),
    ('obsolete', 'dark cyan', 'default'),

    # filelist
    ('+', 'dark green', 'default'),
    ('-', 'dark red', 'default'),
    ('=', 'default', 'default'),
    ('?', 'brown', 'default'),
]

if pygments:
    PALETTE += [
        (Token, 'default', 'default'),
        (Token.Text, 'default', 'default'),
        (Token.Comment, 'dark gray', 'default'),
        (Token.Punctuation, 'white', 'default', 'bold'),
        (Token.Operator, 'light blue', 'default'),
        (Token.Literal, 'dark magenta', 'default'),
        (Token.Name, 'default', 'default'),
        (Token.Name.Builtin, 'dark blue', 'default'),
        (Token.Name.Namespace, 'dark blue', 'default'),
        (Token.Name.Builtin.Pseudo, 'dark blue', 'default'),
        (Token.Name.Exception, 'dark blue', 'default'),
        (Token.Name.Decorator, 'dark blue', 'default'),
        (Token.Name.Class, 'dark blue', 'default'),
        (Token.Name.Function, 'dark blue', 'default'),
        (Token.Keyword, 'light green', 'default'),
        (Token.Generic.Deleted, 'dark red', 'default'),
        (Token.Generic.Inserted, 'dark green', 'default'),
        (Token.Generic.Subheading, 'dark magenta', 'default', 'bold'),
        (Token.Generic.Heading, 'black', 'dark magenta'),
    ]
