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
console interface for hgview.
"""

# disable lazy import for urwid
from hgviewlib import add_demandimport_ignore
add_demandimport_ignore(
    'urwid.html_fragment', 'urwid.tests', 'urwid', 'urwid.escape',
    'urwid.command_map', 'urwid.signals', 'urwid.version', 'urwid.util',
    'urwid.display_common', 'urwid.font', 'urwid.old_str_util',
    'urwid.lcd_display', 'urwid.raw_display', 'urwid.split_repr',
    'urwid.listbox', 'urwid.decoration', 'urwid.widget', 'urwid.graphics',
    'urwid.wimp', 'urwid.container', 'urwid.web_display',
    'urwid.curses_display', 'urwid.text_layout', 'urwid.compat',
    'urwid.main_loop', 'urwid.monitored_list', 'urwid.__init__',
    'urwid.vterm_test', 'urwid.treetools', 'urwid.canvas', 'urwid.vterm')

# use __all__ in the corresponding modules
# pylint: disable=W0401
from hgviewlib.curses.utils import *
from hgviewlib.curses.exceptions import *
from hgviewlib.curses.widgets import *
from hgviewlib.curses.mainframe import MainFrame
# pylint: enable=W0401

# patching urwid

# patch urwid signals system in order to allow delayed signals
import urwid.signals
urwid.signals.delay_emit_signal = lambda o, n, d, *a: urwid.signals.emit_signal(o, n, *a)
def activate_delayed_signals(mainloop):
    """
    patch urwid signals system in order to allow delayed signals
    """
    import urwid.signals
    emit = urwid.signals.emit_signal
    if mainloop is None:
        urwid.signals.delay_emit_signal = lambda o, n, d, *a: emit(o, n, *a)
        return
    memorizer = {}
    def delay_emit_signal(obj, name, delay, *args):
        """Same as emit_signal but really process the signal in `delay` seconds"""
        emit_hash = (id(obj), name)
        # remove previous alarm even if already processed
        if emit_hash in memorizer:
            mainloop.remove_alarm(memorizer[emit_hash])
        delayed_emit = lambda *ignored: emit(obj, name, *args)
        handle = mainloop.set_alarm_in(delay, delayed_emit)
        memorizer[(id(obj), name)] = handle
    urwid.signals.delay_emit_signal = delay_emit_signal
