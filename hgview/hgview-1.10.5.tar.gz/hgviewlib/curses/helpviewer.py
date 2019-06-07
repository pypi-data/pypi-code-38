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
Module that contains the help body.
"""

import urwid
from urwid import AttrWrap, Text, Padding, ListBox, SimpleListWalker, Divider

from hgviewlib.curses import Body, utils, hg_command_map

class HelpViewer(Body):
    """A body to display a help message (or the global program help)"""

    def __init__(self, messages=None, *args, **kwargs):
        # cut line ?
        if messages is not None:
            contents = [Text(messages)]
        else:
            contents = []
            #keybindings
            contents.extend(section('Keybindings'))
            messages = []
            keys = hg_command_map.keys()
            longest = max(len(key) for key in keys)
            for name, cmd in hg_command_map.items():
                messages.append(('ERROR', name.rjust(longest)))
                messages.append(('WARNING', ' | '))
                messages.append(cmd)
                messages.append('\n')
            contents.append(Text(messages))
            # mouse
            contents.extend(section('Mouse'))
            messages = [('ERROR', 'button 1'), ('WARNING', ' | '),
                         'Show context\n',
                         ('ERROR', 'button 3'), ('WARNING', ' | '),
                         'Hide context\n',
                         ('ERROR', 'button 4'), ('WARNING', ' | '),
                         'Scroll up\n',
                         ('ERROR', 'button 5'), ('WARNING', ' | '),
                         'Scroll down\n',
            ]
            contents.append(Text(messages))
            # commands
            contents.extend(section('Commands List'))
            messages = []
            for name, helpmsg in utils.help_commands():
                messages.append(('ERROR', '\ncommand: "%s"\n'%name))
                messages.extend(helpmsg)
            contents.append(Text(messages))


        listbox = ListBox(SimpleListWalker(contents))
        super(HelpViewer, self).__init__(body=listbox, *args, **kwargs)

    def mouse_event(self, size, event, button, *args, **kwargs):
        """Scroll content"""
        if urwid.util.is_mouse_press(event):
            if button == 4:
                self.keypress(size, 'page up')
                return
            elif button == 5:
                self.keypress(size, 'page down')
                return
        return super(HelpViewer, self).mouse_event(size, event, button,
                                                   *args, **kwargs)

def section(title):
    """Return a list of widgets that may used as separators"""
    contents = []
    contents.append(Divider('-'))
    contents.append(AttrWrap(Padding(Text(title), 'center'), 'CRITICAL'))
    contents.append(Divider('-'))
    return contents

