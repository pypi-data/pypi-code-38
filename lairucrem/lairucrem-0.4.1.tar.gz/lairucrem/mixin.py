# Copyright (C) 2016 Alain Leufroy
#
# Author: Alain Leufroy <alain@leufroy.fr>
# Licence: WTFPL, grab your copy here: http://sam.zoy.org/wtfpl/
"""UI widgets for lairucrem."""

import asyncio
import re
import sys
from functools import reduce
from operator import or_
from typing import List, Text, Tuple

import urwid
from urwid.canvas import apply_text_layout
from urwid.command_map import ACTIVATE

from . import config, widgets
from .utils import apply_mixin, ensure_one


class NotFound(ValueError):
    """Raised when not found"""


class _mixin:

    def __init__(self, *args, **kwargs):
        # look up mixin attributes that are in kwargs and apply them to self
        cls = self.__class__
        classes = (c for c in cls.__bases__ if issubclass(c, _mixin))
        names = reduce(or_, [set(vars(c)) for c in classes], set(vars(cls)))
        for name in names & set(kwargs):
            setattr(self, name, kwargs.pop(name))
        super().__init__(*args, **kwargs)


class changeable_listbox(_mixin):
    """Emits 'changed' when the focus changed in the widget."""

    signals = ['changed']

    def change_focus(self, *args, **kwargs):
        out = super().change_focus(*args, **kwargs)
        self._emit('changed')
        return out


class one_line_widget(_mixin):
    """Force the widget to fit in a single line."""

    def set_layout(self, align, wrap, layout=None):
        return super().set_layout(align, urwid.CLIP, layout)


class waitable(_mixin):
    """Mostly an interface definir a waitable object.

    A waitable object has a `wait()` method ensuring that the `_wait` coroutine
    can be called only once.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.wait = ensure_one(self._wait)

    async def _wait(self):
        """function that ensure the task ans kill previous task."""
        return


class ensurable(_mixin):
    """Add `.ensure()` and `.cancel()`

    - `.ensure()`: ensure `._wait()` is called once on the next loop iteration.
    - `.cancel()`: cancel `._wait()` execution or triggerring.
    """

    def ensure(self):
        return self.wait.ensure()

    def cancel(self):
        return self.wait.cancel()


class focusable_widget(_mixin):
    """Add `XXX.focus` style allowing to customize appearance on focus."""

    def render(self, size, focus=False):
        """
        Render contents with wrapping and alignment.  Return canvas.

        See :meth:`Widget.render` for parameter details.

        >>> Text(u"important things").render((18,)).text # ... = b in Python 3
        [...'important things  ']
        >>> Text(u"important things").render((11,)).text
        [...'important  ', ...'things     ']
        """
        (maxcol,) = size
        text, attr = self.get_text()
        if focus:
            attr = [((style or '') + '.focus', length)
                    for style, length in attr]

        trans = self.get_line_translation(maxcol, (text, attr))
        return apply_text_layout(text, attr, trans, maxcol)


class selectable_widget(_mixin):
    """Force widget to be selectable."""

    def selectable(self):
        return True

    def keypress(self, size, key):
        return key


class _key_to_signal(_mixin):

    key_to_signal_map = {}
    mouse_to_signal_map = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._connect_signals()

    def _connect_signals(self):
        return

    def _get_signal_from_key(self, key):
        command = self._command_map[key]
        cls = self.__class__
        if command in cls.key_to_signal_map:
            return cls.key_to_signal_map[command]
        for cls in cls.__mro__:
            keymap = getattr(cls, 'key_to_signal_map', {})
            if command in keymap:
                return keymap[command]

    @classmethod
    def _get_signal_from_mouse(cls, event, button):
        key = (event, button)
        if key in cls.mouse_to_signal_map:
            return cls.mouse_to_signal_map[key]
        for cls in cls.__bases__:
            getter = getattr(cls, '_get_signal_from_mouse', None)
            if getter:
                signal = getter(event, button)
                if signal:
                    return signal

    def keypress(self, size, key):
        if hasattr(self, 'keypress'):
            key = super().keypress(size, key)
        if key is None:
            return None
        signal = self._get_signal_from_key(key)
        if signal:
            self._emit(signal)
            return None
        return key

    def mouse_event(self, size, event, button, col, row, focus=None):
        signal = self._get_signal_from_mouse(event, button)
        if signal:
            self._emit(signal)
            return None
        if hasattr(super(), 'mouse_event'):
            return super().mouse_event(size, event, button, col, row, focus)
        return False


class link(_key_to_signal):
    """Emits 'link' when hitting [enter] or clicking onto the widget."""

    signals = ['link']
    key_to_signal_map = {
        ACTIVATE: 'link',
    }
    mouse_to_signal_map = {
        ('mouse press', 1): 'link',
    }


class filterable_listbox(_key_to_signal):
    """Emit 'filter' when hitting 'ctrl f'."""

    signals = ['filter']
    key_to_signal_map = {
        config.CMD_FILTER: 'filter',
    }


class commandable_listbox(_key_to_signal):
    """Emit 'commandlist' when hitting 'enter'."""

    signals = ['commandlist']
    key_to_signal_map = {
        ACTIVATE: 'commandlist',
    }
    mouse_to_signal_map = {
        ('mouse press', 3): 'commandlist',
    }


class searchable_walker(_mixin):
    """Add search capability to the walker.

    Highlight a regexp in all included widgets and provides helpers to retrieve
    the previous/next widget that matches the regexp.

    This mixin handles cases when a new search regexp is added while:

    1) widgets are already registred into the walker
    2) widgets are added to the walker afterward.

    Note: Only included widgets that have `highlightable_widget` capability is
    searched into.
    """

    _search_regexp = None

    def search(self, regexp):
        """Search for the given regexp."""
        self._search_regexp = regexp
        for widget in self:
            if getattr(widget, 'highlight', None):
                widget.highlight(regexp)
        urwid.signals.emit_signal(self, 'modified')

    def get_next_found(self, pos):
        """Return the next widget matching the registred regexp."""
        widget, pos = self.get_next(pos)
        while widget:
            widget.get_text()   # workaround to update caches
            if getattr(widget, 'ishighlighted', False):
                return widget, pos
            widget, pos = self.get_next(pos)
        return None, None

    def get_previous_found(self, pos):
        """Return the next widget matching the registred regexp."""
        widget, pos = self.get_prev(pos)
        while widget:
            widget.get_text()   # workaround to update caches
            if getattr(widget, 'ishighlighted', False):
                return widget, pos
            widget, pos = self.get_prev(pos)
        return None, None

    def get_next(self, pos):
        """Return the next widget."""
        widget, pos = super().get_next(pos)
        if hasattr(widget, 'highlight'):
            widget.highlight(self._search_regexp)
        return widget, pos

    def get_prev(self, pos):
        """Return the next widget."""
        widget, pos = super().get_prev(pos)
        if hasattr(widget, 'highlight'):
            widget.highlight(self._search_regexp)
        return widget, pos


class searchable_listbox(_key_to_signal):
    """Add search capability to a listbox.

    Add a popup allowing the user to specify a regexp.
    Allow user to jump to the next/previous matching widget.

    Note: searchable_walker is automatically applied to the walker.
    """

    signals = ['search', 'goto_next_found', 'goto_previous_found']
    key_to_signal_map = {
        config.CMD_SEARCH: 'search',
        config.CMD_NEXT_MATCH: 'goto_next_found',
        config.CMD_PREV_MATCH: 'goto_previous_found'
    }
    _search_pattern = ''

    def __init__(self, walker, *args, **kwargs):
        super().__init__(walker, *args, **kwargs)
        apply_mixin(self.body, searchable_walker)

    def _connect_signals(self):
        urwid.signals.connect_signal(
            self, 'search', ensure_one(self._on_search).ensure)
        urwid.connect_signal(self, 'goto_next_found', self.goto_next_found)
        urwid.connect_signal(
            self, 'goto_previous_found', self.goto_previous_found)
        if 'completed' in self.body.signals:
            # Wait for the full content been loaded before firing the focus
            # to the first match. This is necessary because the patch content
            # is splitted into multiple hg commands that fill the listbox
            # asynchronuously. So, if the focus is performed earlier, and the
            # matching line is in the diff part, the description may grow
            # afterward making the matching line invisible.
            urwid.connect_signal(
                self.body, 'completed', self.auto_goto_next_found)

    def auto_goto_next_found(self):
        if self._search_pattern:
            self.goto_next_found()

    def goto_next_found(self, *args):
        widget, pos = self.body.get_next_found(self.focus_position)
        if widget:
            self.set_focus(pos, coming_from='above')
            self._invalidate()

    def goto_previous_found(self, *args):
        widget, pos = self.body.get_previous_found(self.focus_position)
        if widget:
            self.set_focus(pos, coming_from='below')
            self._invalidate()

    async def _on_search(self, *args):
        from .widgets import dialog  # prevent cycling import
        pattern = self._search_pattern or ''
        edit = widgets.edit([('ui.label', 'regexp: ')], pattern)
        answer = await dialog.ask(
            edit, title='SEARCH PATTERN', focus_content=True
        )
        if not answer:
            return
        self.search_pattern(edit.get_edit_text())

    def search_pattern(self, pattern):
        if self._search_pattern == pattern:
            return              # nothing to do
        self._search_pattern = pattern
        regexp = re.compile(self._search_pattern) if pattern else None
        self.body.search(regexp)
        self._invalidate()
        urwid.signals.emit_signal(self, 'goto_next_found')


class refreshable_listbox(_key_to_signal):
    """Emit 'refresh' on [ctrl r]."""

    signals = ['refresh']
    key_to_signal_map = {
        config.CMD_REFRESH: 'refresh'
    }


_Styles = List[Tuple[str, int, int]]  # name, start, end
_Attrib = List[Tuple[str, int]]       # name, length


class highlightable_widget(_mixin):
    """Add highlihgt capability.

    This mixin marks the given widget as searchable (see searchable_walker) but
    it can be used for other purpose.

    Same as urwid.Text but provide a 'highlight(pattern)' method to
    highlight content.
    """

    highlight_style = 'search.highlight'
    default_style = ''
    _highlight = ()
    _original_styles = None
    _original_attrib = None
    _ishighlighted = None

    @staticmethod
    def _merge_styles(
            styles: _Styles,
            maxlength: int,
            defaultstyle: str) -> _Attrib:
        """
        styles: liste of `(name, start, end)`.
        maxlength: the length of the related text
        defaultstyle: the style applied to sections without style from styles

        return: a list of `(name, length)`.
        """
        styles = sorted(styles, key=lambda s: s[0] or '')
        ranges = [(defaultstyle, 0, maxlength)]

        for name, start, end in styles:
            newranges = []
            for n, s, e in ranges:
                if e < start or s > end:
                    newranges.append((n, s, e))
                    continue
                if start >= s:
                    newranges.append((n, s, start))
                newranges.append((name, start, end))
                if end < e:
                    newranges.append((n, end, e))
            ranges = newranges
        oldend = 0
        oldname = 0
        newstyle = []
        for name, start, end in ranges:
            # remove "inner" chunks
            if oldend != start:
                continue
            # merge if previous has the same name
            if oldname == name:
                dummy, length = newstyle.pop()
                start -= length
            newstyle.append((name, end - start))
            oldend = end
            oldname = name

        return newstyle

    @staticmethod
    def _attrib_to_styles(attribs: _Attrib) -> _Styles:
        start = 0
        for name, length in (attribs or ()):
            end = start + length
            yield (name,  start, end)
            start = end

    @staticmethod
    def _compute_styles(text: Text, regexps):
        return [(style, match.regs[-1][0], match.regs[-1][1])
                for pattern, style in regexps
                for match in pattern.finditer(text)
                if match and match.regs[-1][0] != match.regs[-1][1]]

    def _apply_highlight(self):
        if not self._highlight:
            self.ishighlighted = False
            self._attrib[:] = self._original_attrib
        else:
            styles = self._compute_styles(self._text, self._highlight)
            self.ishighlighted = bool(styles)
            attrib = self._merge_styles(
                list(self._attrib_to_styles(self._original_attrib)) + styles,
                len(self._text), self.default_style)
            self._attrib[:] = attrib

    def set_text(self, *args, **kwargs):
        super().set_text(*args, **kwargs)
        self._original_attrib = self._attrib[:]
        self._apply_highlight()

    def highlight(self, regexp, style=None):
        if not regexp:
            highlight = ()
        else:
            highlight = [(regexp, style or self.highlight_style)]
        if highlight == self._highlight:
            return
        self._highlight = highlight
        self._apply_highlight()
        self._invalidate()

    def _get_ishighlighted(self):
        return self._ishighlighted

    def _set_ishihglighted(self, status):
        if self._ishighlighted == status:
            return              # no need to invalidate the widget
        self._selectable = status
        self._ishighlighted = status
        if status and getattr(self, 'keypress', None) is None:
            self.keypress = lambda size, key: key
        self._invalidate()

    ishighlighted = property(_get_ishighlighted, _set_ishihglighted)


class mouse_up_down(_mixin):
    """Convert mouse scroll up/down into keypress up/down."""

    def mouse_event(self, size, event, button, col, row, focus=None):
        key = self.keypress(size, (event, button))
        if not key:
            return True
        return super().mouse_event(
            size, event, button, col, row, focus=None)


class multilist(_mixin):
    """A mixin that combine multiple sequences into one view."""

    __sequences__ = ()

    def _iterseqs(self):
        """iterate over sub-sequences, yielding (startof, seq)."""
        threshold = 0
        for seq in self.__sequences__:
            yield threshold, seq
            threshold += len(seq)

    def __getitem__(self, pos):
        if isinstance(pos, slice):
            indexes = range(*pos.indices(len(self)))
            return [self[idx] for idx in indexes]
        else:
            if pos < 0:
                pos = len(self) + pos
            if pos < 0:  # if it's still neg, we can't do more for him
                raise IndexError('wrong index')
            for thr, seq in self._iterseqs():
                try:
                    return seq[pos - thr]
                except IndexError:
                    continue
            else:
                raise IndexError('wrong index')

    def __len__(self):
        return sum(len(seq) for seq in self.__sequences__)

    def __nonzero__(self):
        return any(len(seq) for seq in self.__sequences__)

    def __setitem__(self, pos, val):
        raise AttributeError('could not set values of a multilist view.')

    def __iter__(self):
        for seq in self.__sequences__:
            for item in seq:
                yield item

    def clear(self, *args, **kwargs):
        for seq in self.__sequences__:
            seq.clear(*args, **kwargs)

    def index(self, item):
        for thr, seq in self._iterseqs():
            try:
                return thr + seq.index(item)
            except ValueError:
                pass

    def startof(self, seq):
        """Global index of first element of the given inner sequence."""
        _seqindex = self.__sequences__.index(seq)
        return sum(len(seq) for seq in self.__sequences__[:_seqindex])


class paginatedlist(_mixin):
    """An hg walker that pauses and resumes the process on demand.

    The walker pauses the hg process when an amount of lines has been added.
    Then it resumes the process when more data is needed.

    :ivar lairucrem.process.hg hgproc: The process to pause/resume

    :ivar ints _amounts: The consecutif amount of entries in each page

    :ivar float _resume_threshold: The percentage of the page on which the
        process shall be resumed

    """

    hgproc = None
    _page_size = 200

    def __init__(self, *args, **kwargs):
        self._next_resume_threshold = 0
        self._widget_futures = []
        super().__init__(*args, **kwargs)

    def _get_transport(self):
        if (self.hgproc and self.hgproc.proc
                and self.hgproc.proc.pid is not None):
            return self.hgproc.proc._transport.get_pipe_transport(1)
        else:
            None

    def _iter_widgets(self, position):
        widget, position = self.get_next(position)
        while widget:
            yield widget, position
            widget, position = self.get_next(position)

    async def _until_widget_added(self):
        if not self.hgproc or not self.hgproc.isrunning():
            return
        self._resume()
        future = asyncio.Future()
        self._widget_futures.append(future)
        try:
            await future
            return True
        except NotFound:
            return False

    async def iter_widgets(self):
        # Iter over already loaded csets
        widget, position = self[0], 0
        if widget:
            yield widget, position
            for widget, position in self._iter_widgets(position):
                yield widget, position
        while (await self._until_widget_added()):
            for widget, position in self._iter_widgets(position):
                yield widget, position

    def append(self, item):
        super().append(item)
        while self._widget_futures:
            # Unlock tasks waiting for new widgets.
            self._widget_futures.pop().set_result(None)
        size = len(self)
        if size > self._next_resume_threshold:
            self._next_resume_threshold = size + self._page_size
            self._pause()

    def __getitem__(self, position):
        if position >= len(self) - 1:
            self._resume()
        # This may raises an IndexError causing the listbox to stop scrolling.
        # But we can expect that the user clicks the down button again. The
        # resumed process should has added more entries allowing to continue
        # scrolling.
        return super().__getitem__(position)

    def _resume(self):
        if self.hgproc and self.hgproc.paused:
            self.hgproc.resume()

    def _pause(self):
        if (self.hgproc and self.hgproc.isrunning
                and not self.hgproc.paused
                and not self._widget_futures):
            self.hgproc.pause()

    async def _wait(self):
        await super()._wait()
        # we reach the end, so cancel pending asked revs
        while self._widget_futures:
            self._widget_futures.pop().set_exception(NotFound('Not Found'))
