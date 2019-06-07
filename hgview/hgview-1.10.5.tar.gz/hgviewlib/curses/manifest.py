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

from urwid import AttrWrap, ListWalker
from urwid.signals import emit_signal

from hgviewlib.util import isbfile, bfilepath, exec_flag_changed
from hgviewlib.curses import SelectableText

DIFF = 'diff'
FILE = 'file'


class ManifestWalker(ListWalker):
    """
    Walk through modified files.
    """

    signals = ['focus changed']

    def __init__(self, walker, ctx, manage_description=False, *args, **kwargs):
        """
        :ctx: mercurial context instance
        :manage_description: display context description as a file if True
        """
        self._cached_flags = {}
        self._walker = walker
        self._ctx = ctx
        self.manage_description = manage_description
        if manage_description:
            self._focus = -1
        else:
            self._focus = 0
        if self._ctx:
            self._files = tuple(self._ctx.files())
        else:
            self._files = ()
        super(ManifestWalker, self).__init__(*args, **kwargs)

    def get_filename(self):
        """Return focused file name"""
        if self._focus < 0:
            return
        return self._files[self._focus]
    def set_filename(self, filename):
        """change focus element by giving the corresponding file name"""
        try:
            focus = self._files.index(filename)
        except ValueError: # focus on description
            focus = -1
        self.set_focus(focus)
    filename = property(get_filename, set_filename, None,
                        'File name under focus.')

    def __len__(self):
        return len(self._files)

    def get_ctx(self):
        """Return the current context"""
        return self._ctx
    def set_ctx(self, ctx, reset_focus=True):
        """set the current context (obsolete the content)"""
        self._cached_flags.clear()
        self._ctx = ctx
        self._files = tuple(self._ctx.files())
        if reset_focus:
            del self.focus
        self._modified()
    ctx = property(get_ctx, set_ctx, None, 'Current changeset context')

    def get_focus(self):
        """return (focused widget, position)"""
        try:
            return self.data(self._focus), self._focus
        except IndexError:
            return None, None
    def set_focus(self, focus):
        """set the focused widget giving the position."""
        self._focus = focus
        emit_signal(self, 'focus changed', self.filename)
    def reset_focus(self):
        """Reset focus"""
        if self.manage_description:
            self._focus = -1
        else:
            self._focus = 0
        emit_signal(self, 'focus changed', self.filename)
    focus = property(lambda self: self._focus, set_focus, reset_focus, 
                     'focus index')

    def get_prev(self, pos):
        """return (widget, position) before position `pos` or (None, None)"""
        focus = pos - 1
        try:
            return self.data(focus), focus
        except IndexError:
            return None, None

    def get_next(self, pos):
        """return (widget, position) after position `pos` or (None, None)"""
        focus = pos + 1
        try:
            return self.data(focus), focus
        except IndexError:
            return None, None

    def data(self, focus):
        """return widget a position `focus`"""
        if self._ctx is None:
            raise IndexError('context is None')
        if (focus < -1) or ((not self.manage_description) and (focus < 0)):
            raise IndexError(focus)

        if focus == -1:
            return AttrWrap(SelectableText('-*- description -*-',
                                           align='right', wrap='clip'),
                            'DEBUG', 'focus')
        filename = self._files[focus]

        # Computing the modification flag may take a long time, so cache it.
        flag = self._cached_flags.get(filename)
        if flag is None:
            flag = self._cached_flags.setdefault(filename,
                    self._walker.graph.fileflag(filename, self._ctx.rev()))
        if not isinstance(flag, str): # I don't know why it could occur :P
            flag = '?'
        return  AttrWrap(SelectableText(filename, align='right', wrap='clip'),
                         flag, 'focus')

    def filedata(self, filename):
        '''return (modification flag, file content)'''
        if isbfile(filename):
            filename = bfilepath(filename)
        graph = self._walker.graph
        return graph.filedata(filename, self._ctx.rev(), 'diff',
                              flag=self._cached_flags.get(filename))

    def clear(self):
        """clear content"""
        self._cached_flags.clear()
        self._files = ()
        del self.focus
        self._modified()

