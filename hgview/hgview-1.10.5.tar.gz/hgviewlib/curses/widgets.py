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
A module that contains usefull widgets.
"""
from urwid import Frame, Text, AttrWrap, ListBox, signals
from urwid.util import is_mouse_press

try:
    import pygments
    from pygments import lex, lexers
    from pygments.util import ClassNotFound
except ImportError:
    # pylint: disable=C0103
    pygments = None

from hgviewlib.curses.canvas import apply_text_layout

__all__ = ['Body', 'ScrollableListBox', 'SelectableText', 'SourceText']


class SelectableText(Text):
    """A selectable Text widget"""
    _selectable = True
    keypress = lambda self, size, key: key

class Body(Frame):
    """A suitable widget that shall be used as a body for the mainframe.

    +------------------+
    |                  |
    |       Body       |
    |                  |
    +------------------+
    |  Text with title |
    +------------------+

    Use the ``title`` property to change the footer text.

    """
    def __init__(self, body):
        footer = AttrWrap(Text(''), 'banner')
        super(Body, self).__init__(body=body, footer=footer, header=None,
                                   focus_part='body')

    def _get_title(self):
        """return the title"""
        return self._footer.get_text()
    def _set_title(self, title):
        """set the title text"""
        self._footer.set_text(title)
    def _clear_title(self):
        """clear the title text"""
        self._footer.set_title('')
    title = property(lambda self: self.footer.text, _set_title, _clear_title, 
                     'Body title')

    def register_commands(self):
        """register commands"""
        pass

    def unregister_commands(self):
        """unregister commands"""
        pass

class ScrollableListBox(ListBox):
    """Scrollable Content ListBox using mouse buttons 4/5"""

    # pylint: disable=R0913
    def mouse_event(self, size, event, button, col, row, focus):
        """Scroll content"""
        if is_mouse_press(event):
            if button == 4:
                self.keypress(size, 'page up')
                return
            elif button == 5:
                self.keypress(size, 'page down')
                return
        return super(ScrollableListBox, self).mouse_event(size, event, button,
                                                          col, row, focus)
    # pylint: enable=R0913

class SourceText(SelectableText):
    """A widget that display source code content.

    It can number lines and highlight content using pygments.
    """

    signals = ['highlight']

    def __init__(self, text, filename=None, lexer=None, numbering=False,
                 *args, **kwargs):
        self._lexer = lexer
        self.filename = filename
        self.numbering = numbering
        super(SourceText, self).__init__(text, *args, **kwargs)
        signals.connect_signal(self, 'highlight', self._highlight)

    def get_lexer(self):
        """Return the current source highlighting lexer"""
        return self._lexer
    def update_lexer(self, lexer=None):
        """
        Update source highlighting lexer using the given one or by inspecting
        filename or text content if ``lexer`` is None.

        :note: Require pygments, else do nothing.
        """
        if not pygments:
            return
        if not self.text:
            return
        text = self.text
        if lexer is None and self.filename: # try to get lexer from filename
            try:
                lexer = lexers.get_lexer_for_filename(self.filename, text)
            except (ClassNotFound, TypeError): #TypeError: pygments is confused
                pass
        if lexer is None and text: # try to get lexer from text
            try:
                lexer = lexers.guess_lexer(text)
            except (ClassNotFound, TypeError): #TypeError: pygments is confused
                pass
        self._lexer = lexer
        if lexer == None: # No lexer found => finish
            return
        # reduce "lag" while rendering the text as pygments may take a while to
        # highlight the text. So we colorize only the first part of the text
        # and delay coloring the full text. The 3000st chars seems good on my
        # laptop :)
        signals.delay_emit_signal(self, 'highlight', 0.05, self.text)
        colored = list(lex(self.text[:3000], self._lexer))
        #remove the f*@!king \n added by lex
        colored[-1] = (colored[-1][0], colored[-1][1][:-1])
        self.set_text(colored + [self.text[3000:]])

    def _highlight(self, text):
        self.set_text(list(lex(text, self._lexer)))

    def clear_lexer(self):
        """Disable source highlighting"""
        self.set_text(self.text)
    lexer = property(get_lexer, update_lexer, clear_lexer,
                     'source highlighting lexer (require pygments)')

    def render(self, size, focus=False):
        """
        Render contents with wrapping, alignment and line numbers.
        """
        (maxcol,) = size
        text, attr = self.get_text()
        trans = self.get_line_translation(maxcol, (text, attr))
        return apply_text_layout(text, attr, trans, maxcol,
                                 numbering=self.numbering)

