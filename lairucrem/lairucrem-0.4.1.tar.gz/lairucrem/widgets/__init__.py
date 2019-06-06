# Copyright (C) 2016 Alain Leufroy
#
# Author: Alain Leufroy <alain@leufroy.fr>
# Licence: WTFPL, grab your copy here: http://sam.zoy.org/wtfpl/
"""UI widgets for lairucrem."""

import re

import urwid
from urwid.canvas import CompositeCanvas
from urwid.decoration import AttrMapError

from .. import config
from ..mixin import _mixin


urwid.set_encoding('utf-8')


class _attrwrap(_mixin):
    """same as urwid.decorations.AttrWrap but as a mixin."""

    _attr_map = {}
    _focus_map = {}

    def _repr_attrs(self):
        # only include the focus_attr when it takes effect (not None)
        d = dict(self.__super._repr_attrs(), attr_map=self._attr_map)
        if self._focus_map is not None:
            d['focus_map'] = self._focus_map
        return d

    def get_attr_map(self):
        return dict(self._attr_map)

    def set_attr_map(self, attr_map):
        for from_attr, to_attr in list(attr_map.items()):
            if not from_attr.__hash__ or not to_attr.__hash__:
                raise AttrMapError(
                    "%r:%r attribute mapping is invalid.  "
                    "Attributes must be hashable" % (from_attr, to_attr))
        self._attr_map = attr_map
        self._invalidate()
    attr_map = property(get_attr_map, set_attr_map)

    def get_focus_map(self):
        if self._focus_map:
            return dict(self._focus_map)

    def set_focus_map(self, focus_map):
        if focus_map is not None:
            for from_attr, to_attr in list(focus_map.items()):
                if not from_attr.__hash__ or not to_attr.__hash__:
                    raise AttrMapError(
                        "%r:%r attribute mapping is invalid.  "
                        "Attributes must be hashable" % (from_attr, to_attr))
        self._focus_map = focus_map
        self._invalidate()
    focus_map = property(get_focus_map, set_focus_map)

    def get_focus_attr(self):
        focus_map = self.focus_map
        if focus_map:
            return focus_map[None]

    def set_focus_attr(self, focus_attr):
        self.set_focus_map({None: focus_attr})
    focus_attr = property(get_focus_attr, set_focus_attr)

    def _render(self, size, focus=False):
        return super().render(size, focus)

    def render(self, size, focus=False):
        attr_map = self._attr_map
        if focus and self._focus_map is not None:
            attr_map = self._focus_map
        canv = self._render(size, focus=focus)
        canv = CompositeCanvas(canv)
        canv.fill_attr_apply(attr_map)
        return canv


class disablable_button_mixin:

    _disabled = False
    _disabled_map = {None: 'ui.button.disabled'}

    def selectable(self):
        return self._label._selectable and not self._disabled

    @property
    def disabled(self):
        return self._disabled

    @disabled.setter
    def disabled(self, value):
        shouldinvalidate = self._disabled != value
        self._disabled = value
        if shouldinvalidate:
            self._invalidate()

    def render(self, size, focus=False):
        if self._disabled:
            attr_map = self._disabled_map
            canv = super().render(size, focus=focus)
            canv = CompositeCanvas(canv)
            canv.fill_attr_apply(attr_map)
            return canv
        return super().render(size, focus)


class lightbutton(_attrwrap, disablable_button_mixin, urwid.Button):
    """Simple button without decoration"""

    _attr_map = {None: 'ui.button'}
    _focus_map = {None: 'ui.button.focus'}
    button_left = urwid.Text("")
    button_right = urwid.Text("")

    def __repr__(self):
        return f'<lightbutton label="{self._label.get_text()}">'

    def keypress(self, size, key):
        if key == ' ':
            return ' '
        else:
            return super().keypress(size, key)


class edit(_attrwrap, urwid.Edit):
    """urwid.Edit with default style."""

    _word_sep_regexp = re.compile('(%s)' % '|'.join((
        r'\s', '\.', ',', ';', ':', '\+', '\-', '\*', '%',
        '/', r'\\', '\(', '\)', '\[', '\]', '\{', '\}')))

    _attr_map = {None: 'ui.edit'}
    _focus_map = {None: 'ui.edit.focus'}

    _command_map = config.edit_command_map

    def keypress(self, size, key):
        key = super().keypress(size, key)
        if key is None:
            return key
        command = self._command_map[key]
        if command == config.CMD_NEXT_WORD:
            self._move_cursor_next_word()
            return None
        if command == config.CMD_PREV_WORD:
            self._move_cursor_prev_word()
            return None
        if command == config.CMD_KILL_LINE:
            self._trim_edit_text_at_cursor()
            return None
        if command == config.CMD_KILL_PREV_WORD:
            self._remove_previous_word()
            return
        if command == config.CMD_KILL_NEXT_WORD:
            self._remove_next_word()
            return
        return key

    def _move_cursor_next_word(self):
        pos = self._find_next_word_start()
        if pos is not None:
            self.set_edit_pos(pos)

    def _move_cursor_prev_word(self):
        pos = self._find_prev_word_start()
        if pos is not None:
            self.set_edit_pos(pos)

    def _trim_edit_text_at_cursor(self):
        text = self.edit_text
        p = self.edit_pos
        self.set_edit_text(text[:p])

    def _remove_previous_word(self):
        text = self.edit_text
        p = self._find_prev_word_start()
        if p is None or p == self.edit_pos:
            return
        after = text[self.edit_pos:]
        p = self._find_prev_word_start()
        before = text[:p]
        self.set_edit_text(before + after)
        self.set_edit_pos(p)

    def _remove_next_word(self):
        text = self.edit_text
        p = self._find_next_word_start()
        if p is None or p == self.edit_pos:
            return
        before = text[:self.edit_pos]
        p = self._find_next_word_start()
        after = text[p:]
        self.set_edit_text(before + after)

    def _find_prev_word_start(self):
        p = self.edit_pos
        if p is None or p <= 0:
            return
        text = self.edit_text[p - 1::-1]
        match = self._word_sep_regexp.search(text)
        if match:
            p -= match.start() + 1
        else:
            p = 0
        return p

    def _find_next_word_start(self):
        p = self.edit_pos
        text = self.edit_text
        if p is None or p >= len(text):
            return
        match = self._word_sep_regexp.search(text[p + 1:])
        if match:
            p += match.start() + 1
        else:
            p = len(text)
        return p
