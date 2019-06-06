import asyncio
import itertools
import re
from concurrent.futures import FIRST_COMPLETED
from string import ascii_letters

import urwid
from urwid import AttrWrap, CheckBox, Filler, LineBox, Padding, Pile, Text

from . import lightbutton
from .. import config, open_popup
from ..utils import ensure_one, slicer


class ReservedShortcut(ValueError):
    """Raised when a shortcut is already reserved."""


class InvalidShortcut(ValueError):
    """Raised when an invalid shortcut is found."""


class _shortcuts_handler:
    """Deduct key shortcut from texts.

    >>> hdl = _shortcuts_handler()
    >>> hdl.find('hello')
    'h'
    >>> hdl.find('hi')
    'i'
    >>> hdl.find('cio')
    'c'
    >>> hdl.find('chic')
    'a'
    >>> hdl.reserved
    ['h', 'i', 'c', 'a']

    """

    valid_shortcuts = ascii_letters + r'1234567890~!@#$%^&*()_+,./\<>?{}|;:'

    def __init__(self):
        self._availables = list(self.valid_shortcuts[:])
        self._reserved = []

    def reserve(self, shortcut):
        """Reserve a shortcut.

        :raises ReservedShortcut: if the shortcut is already reserved
        :raises InvalidShortcut: if the shortcut is not valid
        """
        if shortcut in self._reserved:
            raise ReservedShortcut('shortcut not available: %r' % shortcut)
        if shortcut not in self._availables:
            raise InvalidShortcut('not a shortcut: %r' % shortcut)
        else:
            self._availables.remove(shortcut)

    def find(self, text):
        for shortcut in text:
            try:
                self.reserve(shortcut)
            except (ReservedShortcut, InvalidShortcut):
                continue
            else:
                break
        else:
            shortcut = next(self)
        self._reserved.append(shortcut)
        return shortcut

    def __next__(self):
        shortcut = self._availables.pop(0)
        self._reserved.append(shortcut)

    @property
    def reserved(self):
        return self._reserved


def _divider():
    return urwid.AttrWrap(urwid.Divider(), 'ui.dialog')


class _pile(Pile):
    """Patched urwid.Pile fixing focus when the content is added afterward."""

    def _set_widget_list(self, widgets):
        super()._set_widget_list(widgets)
        self._invalidate()
        if self.focus_position == 0:
            for position, widget in enumerate(widgets):
                if widget.selectable():
                    self.focus_position = position
                    break


class simple(urwid.AttrWrap):
    """A simple dialog box that displays a content widget."""
    signals = ['close', 'message']
    close = 'after'

    def __init__(self, content, title: str, message: str='',
                 *, min_height: int=0, focus_content=False):
        self.min_height = min_height
        self._future = asyncio.Future()
        self._keyactions = {}
        self._commandactions = {}
        self._buttons = []
        self._title = title
        self._message = Text(message)
        self._content = Text(content) if isinstance(content, str) else content
        self._add_buttons()
        super().__init__(self._setup_ui(focus_content), 'ui.dialog')
        urwid.connect_signal(self, 'message', self.display_message)

    def get_rows(self):
        """Return the prefered height of the dialog"""
        if getattr(self._content, 'get_rows', None):
            return self._content.get_rows() + 6
        return 10 + self.min_height

    def _setup_ui(self, focus_content=False):
        btn_container = urwid.Columns(self._buttons, dividechars=2)
        self._buttons = btn_container.widget_list  # allow auto update
        pile = _pile([
            Padding(btn_container, align=urwid.CENTER, width=70),
            _divider(),
            self._content,
            _divider(),
            self._message])
        if focus_content:
            pile.set_focus(self._content)
        return LineBox(
            Filler(pile, min_height=20),
            tline='━', bline='━', lline='┃', rline='┃', title=self._title)

    def _add_buttons(self):
        """build the dialog buttons"""
        self.append_button(text='Close', value=None, key='esc', command=config.CMD_ESCAPE)

    def append_button(self, text, value, key, close=True, command=None):
        self._buttons.append(self._build_button(text, value, key, close, command))

    def _build_button(self, text, value, key='', close=True, command=None):

        def action(*args):
            self.resolve(value, close)

        if key:
            self._keyactions[key] = action
        if command:
            key = next(
                key for key, cmd in self._command_map._command.items()
                if cmd == command)
            self._commandactions[command] = action
        if key:
            text = f'[{key}] {text}'
        btn = lightbutton(text)
        urwid.connect_signal(btn, 'click', action)
        return btn

    def display_message(self, message):
        self._message.set_text(message)

    def resolve(self, value, close=True):
        if self._future and not self._future.done():
            self._future.set_result(value)
        if close:
            self._emit('close')

    def keypress(self, size, key):
        """process keypress"""
        key = super().keypress(size, key)
        if key is None:
            return None
        command = self._command_map[key]
        if command in self._commandactions:
            self._commandactions[command]()
            return None
        if key in self._keyactions:
            self._keyactions[key]()
            return None
        return key

    def __await__(self):
        self._future = asyncio.Future()  # before open_popup for easy testing
        open_popup(self)
        return (yield from self._future)

    def done(self):
        return self._future.done()

    def result(self):
        return self._future.result()

    def close(self):
        if self._future and not self._future.done():
            self._future.cancel()
        self._emit('close')


class ask(simple):
    """Like simple but contains 2 buttons: Cancel (None) and Vaidate(True)."""

    def _add_buttons(self):
        """build the dialog buttons"""
        self.append_button('Cancel', value=None, key='esc', command=config.CMD_ESCAPE)
        self.append_button('Validate', value=True, key='enter')


class _choices(simple):

    def __init__(self, choices, title='Choices', prolog='Choices:'):
        self._choices = []
        super().__init__(self._setup_content(prolog), title)
        self._add_choices(choices)

    def get_rows(self):
        """Return the prefered height for the dialog"""
        return len(self._choices) * 2 + 5

    def _setup_content(self, prolog):
        """Set up widgets."""
        pile = _pile(
            [AttrWrap(Text(prolog), 'ui.dialog'), _divider()] + self._choices)
        self._choices = slicer(pile.widget_list, 2)  # allow auto update
        return pile

    def _add_choices(self, choices):
        for choice in choices:
            self.append_choice(choice)

    def append_choice(self, choice):
        self._choices.append(self._build_choice(choice))

    def extend_choices(self, choices):
        for choice in choices:
            self.append_choice(choice)

    def _build_choice(self, *choice):
        raise NotImplementedError()


class choices(_choices):
    """A dialog that allows users to choose from a list of choices.

    Choices are displayed as buttons. User can select a
    choice by clicking a button or by hitting an associated key
    shortcut (a letter linked automatically). No more that
    `len(shortcuts)` choices is allowed.

    """

    signals = ['selected']

    def __init__(self, choices, title='Choices', prolog='Choose one of:'):
        self._shortcuts_handler = _shortcuts_handler()
        self._filter_pattern = ''
        super().__init__(choices, title=title, prolog=prolog)
        self._display_fuzzy_filter_help()

    def append_button(self, text, value, key, close=True, command=None):
        try:
            self._shortcuts_handler.reserve(key)
        except InvalidShortcut:  # a.k.a. "ctrl x"
            pass
        super().append_button(text, value, key, close, command)

    def _build_choice(self, choice):
        index = len(self._choices)
        return self._build_button(choice, value=index, key='', close=True)

    def append_choice(self, choice):
        super().append_choice(choice)
        self._filter_choices(reset_on_unmatch=False)

    def _filter_choices(self, reset_on_unmatch=True):
        """Fuzzy filter the choices."""
        first_match = None
        regex = '.*?' + self._filter_pattern.replace(' ', '.*?')
        for choice in self._choices:
            if re.match(regex, choice.get_label()):
                if not first_match:
                    first_match = choice
                choice.disabled = False
            else:
                choice.disabled = True
        if first_match and self._filter_pattern:
            # Focus on the first matching choice if fuzzy filtering.
            self._content.set_focus(first_match)
            self.w.original_widget.original_widget.set_focus(self._content)
        elif reset_on_unmatch:
            # Focus on top button otherwise.
            self.w.original_widget.original_widget.set_focus(0)
        self._invalidate()

    def keypress(self, size, key):
        key = super().keypress(size, key)
        if key is None:
            return None
        if self._command_map[key] == config.CMD_KILL_PREV_CHAR:
            self._filter_pattern = self._filter_pattern[:-1]
        elif key in (ascii_letters + ' '):
            self._filter_pattern += key
        else:
            return key
        self._display_fuzzy_filter_help()
        self._filter_choices()

    def _display_fuzzy_filter_help(self):
        if self._filter_pattern:
            self.display_message(f'Fuzzy patterns: {self._filter_pattern}')
        else:
            self.display_message(
                f'Type characters to fuzzy filter the action list.')


class select(_choices):
    """Multiple choices dialog."""

    _validated = object()

    def __init__(self, choices, states=None, title='Select', prolog=''):
        choices = itertools.zip_longest(choices, states or (), fillvalue=False)
        super().__init__(choices, title=title, prolog=prolog)

    def _add_buttons(self):
        """build the dialog buttons"""
        self.append_button('Cancel', value=None, key='esc', command=config.CMD_ESCAPE)
        self.append_button('Validate', value=self._validated, key='v')

    def _add_choices(self, choices):
        for choice, state in choices:
            self.append_choice(choice, state)

    def append_choice(self, choice, state=False):
        self._choices.append(self._build_choice(choice, state))

    def _build_choice(self, choice, state=False):
        return CheckBox(choice, state)

    def _iterselected(self):
        for index, widget in enumerate(self._choices):
            if widget.state:
                yield index

    def resolve(self, value, close=True):
        if value is self._validated:
            value = list(self._iterselected())
        super().resolve(value)


async def async_choices(tasks):
    """Open a choices dialog and fill it with `tasks` results when they arrive.

    This function is useful when computing choices takes sometimes
    and you want to display them early.

    If the user respond before all actions arrive, ignore pending actions.
    """
    _choices = []
    loop = asyncio.get_event_loop()
    prolog = 'Theses action(s) can be applied to the selected changeset:'
    diag = choices([], title='ACTIONS', prolog=prolog)
    # also add the dialog task to break if the user responds early
    tasks.append(diag.__await__())
    while tasks:
        # consum tasks
        dones, tasks = await asyncio.wait(tasks, return_when=FIRST_COMPLETED)
        if diag.done():  # user already answered ⇒ ignore new actions
            break
        _names = []
        for task in dones:   # dialog task already checked ⇒ only commandes
            result = task.result()
            if result:  # skip invalid action
                name, cmd = result
                _choices.append(cmd)
                _names.append(name)
        if _names:
            # please urwid cache validation by adding on the next iteration
            loop.call_soon(diag.extend_choices, _names)
    # cancel remaining as they no more useful
    for task in task:
        task.cancel()
    choice = diag.result()
    return _choices[choice] if choice is not None else None


@ensure_one
async def popup_processing(
        task: asyncio.Future,
        message: str='Processing…. Close this popup to cancel the operation',
        title: str='Processing…'):
    """Display a popup message until the given task is done."""
    from ..utils import popup_error
    if asyncio.iscoroutine(task):
        task = asyncio.ensure_future(task)
    if task.done():  # Do not annoy user if the task is already done.
        error = task.exception()
        if error:
            await popup_error().display_exception(type(error), error, error.__traceback__)
        return       # Especially useful when this task is delayed
    diag = simple(message, title=title)
    try:
        await asyncio.wait([task, diag], return_when=FIRST_COMPLETED)
    finally:
        if not task.done():
            task.cancel()
            return None
        else:
            diag.close()
            from ..utils import popup_error
            async with popup_error(Exception, donotraise=True):
                return task.result()
