#! /usr/bin/env python
# Copyright (C) 2016 Alain Leufroy
#
# Author: Alain Leufroy <alain@leufroy.fr>
# Licence: WTFPL, grab your copy here: http://sam.zoy.org/wtfpl/
"""Main UI widgets for lairucrem."""

from __future__ import absolute_import, unicode_literals

import urwid
from urwid.canvas import CompositeCanvas
from urwid.command_map import CURSOR_LEFT, CURSOR_RIGHT
from urwid.widget import delegate_to_widget_mixin

from .. import config


class popuplauncher(urwid.PopUpLauncher):
    """
    Main widget that allows to display a popup using the `open_pop_up` method.

    Usage:
    ======

    >>> content = urwid.Filler(urwid.Text('Foo'))
    >>> launcher = popuplauncher(content)
    >>> popup = urwid.Filler(urwid.Text('Bar'))
    >>> launcher.open_pop_up(popup)
    """

    def __init__(self, *args, **kwargs):
        self._screen = None
        self._height = None
        self._pop_up_widgets = []
        super(popuplauncher, self).__init__(*args, **kwargs)

    def open_pop_up(self, widget):
        self._pop_up_widgets.append(widget)
        if getattr(widget, 'signals', None) and 'close' in widget.signals:
            urwid.connect_signal(
                widget, 'close', lambda *a: self.close_pop_up(widget))
        self._invalidate()

    def close_pop_up(self, widget):
        # actual popup could be a newer one
        if widget in self._pop_up_widgets:
            self._pop_up_widgets.remove(widget)
        self._invalidate()

    def render(self, size, focus=False):
        canv = self._original_widget.render(size, focus)
        if self._pop_up_widgets:
            widget = self._pop_up_widgets[-1]
            canv = CompositeCanvas(canv)
            cols, rows = size
            height = rows - 4
            if getattr(widget, 'get_rows', None):
                height = min(height, widget.get_rows())
            top = int((rows - height) / 2)
            canv.set_pop_up(widget,
                            left=2, overlay_width=cols - 4,
                            top=top, overlay_height=height)
        return canv


class mainwidget(urwid.Pile):
    """Main widget with help"""
    _help = "[enter] actions  [/] filter  [left,right] details  [?] help"

    signals = ['open_popup']

    def __init__(self, widget):
        head = urwid.AttrWrap(
            urwid.Filler(urwid.Text(self._help)),
            'highlight',
        )
        super(mainwidget, self).__init__(
            [(1, head), widget],
            focus_item=widget,
        )


class thehelp(urwid.Pile):
    """Help dialog content"""

    @staticmethod
    def get_rows():
        """prefered height"""
        return 20

    def __init__(self):

        def key(keys, help):
            key = ' '.join(keys).rjust(16)
            text = [('ui.keyword', key), (None, '  '), help]
            return urwid.Text(text)

        def title(text):
            return urwid.Text([('ui.title', text)])

        super(thehelp, self).__init__([
            title('Global keys\n'),
            key(['<Tab>'], 'Switch pane'),
            key(['<Esc>'], 'Close dialog box'),
            key(['?'], 'This help'),
            key(['q', 'Q'], 'Quit the application'),
            key(['G'], ('Grep: Search revision history '
                        'for a regular expression')),

            title('\nTREE pane keys\n'),
            key(['<Up>', '<Down>'], 'Goto the previous/next changeset'),
            key(['<Alt Up>', '<Alt Down>'], 'Goto the previous child/parent'),
            key(['ctrl f'], 'Filter the revision tree with a revset'),
            key(['<enter>'], 'Actions related to the selected changset'),
            key(['<ctrl r>'], 'Refresh view content'),

            title('\nPATCH pane keys\n'),
            key(['<Up>', '<Down>'], 'Scroll Up, Down'),
            key(['/'], 'Search pattern in the patch content'),
            key(['n', 'N'], 'Jump to the next/previous matched line'),
            key(['<ctrl r>'], 'Refresh view content'),
        ])


class packer(delegate_to_widget_mixin('_original_widget')):
    """Pack the given widgets horizontally (Columns)or vertically (Pile)
    depending on the screen size.
    """
    def __init__(self, widgets):
        self._orientation = None
        self._widgets = widgets
        self._original_widget = None

    def render(self, size, focus):
        """render the widget"""
        self._update_container(size)
        return super(packer, self).render(size, focus)

    def _update_container(self, size):
        """update the main container depending on the given size"""
        cols = size[0]
        if cols > 160 and self._orientation != 'horizontal':
            self._original_widget = urwid.Columns(self._widgets)
            self._orientation = 'horizontal'
        elif cols < 160 and self._orientation != 'vertical':
            self._original_widget = urwid.Pile(self._widgets)
            self._orientation = 'vertical'
        # only when screen size change, so mainloop has already invalidate self

    def keypress(self, size, key):
        """Process pressed key"""
        key = super(packer, self).keypress(size, key)
        widget = self._original_widget
        command = self._command_map[key]
        if command == CURSOR_LEFT:
            widget.focus_position = max(0, widget.focus_position - 1)
            return
        if command == CURSOR_RIGHT:
            widget.focus_position = min(len(self._widgets) - 1,
                                        widget.focus_position + 1)
            return
        if command in (config.CMD_NEXT_SELECTABLE, config.CMD_PREV_SELECTABLE):
            nbwidgets = len(self._widgets)
            widget.focus_position = (widget.focus_position + 1) % nbwidgets
            return
        return key


class pane(urwid.LineBox):
    """
    A LineBox that changes surrounding chars accordingly to the focus
    state.
    """

    # pylint: disable=super-init-not-called
    def __init__(self, original_widget, title=""):
        """
        Draw a line around original_widget.

        Use 'title' to set an initial title text with will be centered
        on top of the box.

        You can also override the widgets used for the lines/corners:
            tline: top line
            bline: bottom line
            lline: left line
            rline: right line
            tlcorner: top left corner
            trcorner: top right corner
            blcorner: bottom left corner
            brcorner: bottom right corner

        """
        self.tline = urwid.Divider(' ')
        self.bline = urwid.Divider(' ')
        self.lline = urwid.SolidFill(' ')
        self.rline = urwid.SolidFill(' ')
        (tlcorner, trcorner, blcorner, brcorner,
         self.fill_char_focus, self.fill_char, self.div_char_focus, self.div_char) = config.BORDERS

        self.title_widget = urwid.Text(self.format_title(title))
        self.tline_widget = urwid.Columns([
            self.tline,
            ('flow', self.title_widget),
            self.tline,
        ])

        top = urwid.Columns([
            ('fixed', 1, urwid.Text(tlcorner)),
            self.tline_widget,
            ('fixed', 1, urwid.Text(trcorner))
        ])

        middle = urwid.Columns([
            ('fixed', 1, self.lline),
            original_widget,
            ('fixed', 1, self.rline),
        ], box_columns=[0, 2], focus_column=1)

        bottom = urwid.Columns([
            ('fixed', 1, urwid.Text(blcorner)), self.bline, ('fixed', 1, urwid.Text(brcorner))
        ])

        pile = urwid.Pile(
            [('flow', top), middle, ('flow', bottom)], focus_item=1)

        urwid.WidgetDecoration.__init__(self, original_widget)
        urwid.WidgetWrap.__init__(self, pile)

    def render(self, size, focus=False):
        """Return the canvas that renders the widget content."""
        self.lline.fill_char = self.rline.fill_char = self.fill_char_focus if focus else self.fill_char
        self.tline.div_char = self.bline.div_char = self.div_char_focus if focus else self.div_char
        self.lline._invalidate()
        self.rline._invalidate()
        self.tline._invalidate()
        self.bline._invalidate()
        try:
            return super(pane, self).render(size, focus=True)
        except IndexError:
            # the content is empty, we can't force focus
            return super(pane, self).render(size, focus=False)
