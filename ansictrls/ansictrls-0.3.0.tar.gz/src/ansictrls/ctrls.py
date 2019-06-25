from contextlib import contextmanager
from enum import Enum
from functools import partial
from types import new_class

import term


_CTRLSEQS = dict(
    ICH='\033[%s@',     # insert character(s)
    CUU='\033[%sA',     # cusor up
    CUD='\033[%sB',     # cursor down
    CUF='\033[%sC',     # cursor foreward
    CUB='\033[%sD',     # cursor backward
    CNL='\033[%sE',     # cursor next line
    CPL='\033[%sF',     # cursor preceding line
    CHA='\033[%sG',     # cursor character absolute
    CUP='\033[%sH',     # cursor position
    CHT='\033[%sI',     # cursor forward tabulation
    ED='\033[%sJ',      # erase in display
    EL='\033[%sK',      # erase in line
    IL='\033[%sL',      # insert line(s)
    DL='\033[%sM',      # delete line(s)
    DCH='\033[%sP',     # delete character(s)
    SU='\033[%sS',      # scroll up
    SD='\033[%sT',      # scroll down
    ECH='\033[%sX',     # erase character(s)
    CBT='\033[%sZ',     # cursor backward tabulation
    HPA='\033[%s`',     # horizontal postion absolute
    VPA='\033[%sd',     # vertical position absolute
    SGR='\033[%sm',     # select graphic rendition
    SCP='\033[s',       # save cursor position
    RCP='\033[u',       # restore cursor position
    SCU='\033[?25h',    # show cursor
    HCU='\033[?25l',    # hide cursor
    EAS='\033[?1049h',  # enable alternate screen buffer
    DAS='\033[?1049l',  # disable alternate screen buffer
    RIS='\033c',        # reset screen to initial state
)


class _CtrlSeq:
    def __init__(self, name, value):
        self._name = name
        self._value = value

    def __mod__(self, other):
        if '%s' in self._value:
            if isinstance(other, int):
                return self._value % int(other)
            if isinstance(other, tuple):
                lst = []
                for x in other:
                    if isinstance(x, tuple):
                        lst.extend(x)
                    else:
                        lst.append(x)
                if all(isinstance(x, int) for x in lst):
                    return self._value % ';'.join(map(str, map(int, lst)))
            raise TypeError('Arguments must be of type int or a tuple of ints')
        else:
            return self._value

    def __repr__(self):
        return '<%s: %r>' % (self._name, self._value)

    def __str__(self):
        if '%s' in self._value:
            return self._value % ''
        else:
            return self._value

    def __add__(self, other):
        return str(self) + str(other)

    def __radd__(self, other):
        return str(other) + str(self)


def _ctrlseqs_cb(ns):
    for k, v in _CTRLSEQS.items():
        ns[k] = _CtrlSeq('CS.' + k, v)


CS = new_class('CS', exec_body=_ctrlseqs_cb)
CS.__doc__ = 'Command sequences.'

_print = partial(print, end='', sep='', flush=True)


def move(row=0, col=0, rel=True):
    """Move the cursor.

    The cursor can be moved relative (``rel=True``) or absolute (``rel=False``).
    If ``row=0`` the cursor will be moved within the current row; if ``col=0``
    the cursor will be moved in the current column. Absolute ``row`` and ``col``
    values start at 1 and cannot be negative. For relative movements negative
    numbers mean to the left or up and positive numbers move the cursor to the
    right or down. If only one of ``row`` or ``col`` is relative and the other
    is absolute, the ``rel`` parameter has to be a tuple: ``rel=(True, False)``
    means relative row and absolute column movement and ``rel=(False, True)``
    absolute row and relative column movement.

    ::

       move(col=2)        # move cursor two columns to the right
                          # and leave the row unchanged
       move(1, 1, False)  # move cursor to the top left corner
       move(-5, 1, (True, False)  # move cursor to the beginning of the
                                  # line five rows up

    :param int row: the row
    :param int col: the column
    :param rel: if ``True`` the cursor will be moved relative to the
                current position
    :type rel: bool or tuple(bool, bool)
    :raises TypeError: if row or col are not of type ``int``
    :raises ValueError: if not at least one of ``row`` or ``col`` is not 0,
                        or if ``rel=False`` and ``row`` or ``col`` are
                        negative
    """
    if not (isinstance(row, int) and isinstance(col, int)):
        raise TypeError('Arguments "row" and "col" must be of type int')
    if row == 0 and col == 0:
        raise ValueError('At least one argument "row/col" != 0 required')
    if isinstance(rel, tuple):
        rel_row, rel_col = map(bool, rel)
    else:
        rel_row = rel_col = bool(rel)
    if (not rel_row and row < 0) or (not rel_col and col < 0):
        raise ValueError('Absolute "row/col" must be positive integers')
    if row and col and rel_row == rel_col is False:
        _print(CS.CUP % (row, col))
    else:
        if row:
            if rel_row:
                _print(CS.CUD % row if row > 0 else CS.CUU % abs(row))
            else:
                _print(CS.VPA % row)
        if col:
            if rel_col:
                _print(CS.CUF % col if col > 0 else CS.CUB % abs(col))
            else:
                _print(CS.HPA % col)


def home():
    """Move the cursor to the top left corner of the screen."""
    _print(CS.CUP)


def clear(reset=False):
    """Clear screen.

    Erase entire screen and move the cursor to the top left corner
    of the screen.

    :param bool reset: if set to `True` the line buffer will be erased too
    """
    erase(EraseMode.SCRN_ALL)
    home()
    if reset:
        erase(EraseMode.SCRN_LINES)


class EraseMode(Enum):
    """Mode parameter for :func:`erase`."""

    SCRN_END = 0    #: From cursor to end of screen
    SCRN_BEGIN = 1  #: From cursor to beginning of screen
    SCRN_ALL = 2    #: Entire screen
    SCRN_LINES = 3  #: All lines in scrollback buffer
    LINE_END = 4    #: From cursor to end of line
    LINE_BEGIN = 5  #: From cursor to beginning of line
    LINE_ALL = 6    #: Entire line


def erase(mode):
    """Erase all or part of line/screen (cursor position does not change).

    :param mode: what to erase
    :type mode: EraseMode
    """
    if not isinstance(mode, EraseMode):
        raise TypeError('Argument "mode" must be an EraseMode enum member')
    if mode.value <= 3:
        _print(CS.ED % mode.value)
    else:
        _print(CS.EL % (mode.value - 4))


@contextmanager
def hide_cursor():
    """Hide the cursor.

    This function is a context manager for use in ``with`` statements.
    It hides the cursor when the context is entered and shows it again
    when the context is exited.
    """
    _print(CS.HCU)
    try:
        yield
    finally:
        _print(CS.SCU)


def nestable_save_pos_possible():
    """Return if nestable :func:`save_pos` context is supported.

    :return: True if supported
    :rtype: bool
    """
    return term.getyx() != (0, 0)


@contextmanager
def save_pos(nestable=False):
    """Save the cursor position.

    This function is a context manager for use in ``with`` statements.
    It saves the cursor position when the context is entered and restores the
    cursor to the saved position when the context is exited.

    If ``nestable=False`` the ANSI control sequences ``ESC[s: SCP - Save Cursor
    Position`` and ``ESC[u: RCP - Restore Cursor Position`` will be used. By
    doing so only the saved cursor position of the innermost context will be
    restored.

    If ``nestable=True`` and :func:`nestable_save_pos_possible` returns
    ``True``, each time the context is entered the position is determined by
    calling ``getyx()`` from the
    `term package <https://pypi.org/project/term/>`_.
    If the terminal does not support the control sequence
    ``ESC[6n: DSR – Device Status Report`` this is not possible.

    :param bool nestable: wether a nestable context should be used
    :raises RuntimeError: if ``nestable=True`` and nestable context not possible
    """
    if nestable:
        pos = term.getyx()
        if pos == (0, 0):
            raise RuntimeError('Nestable save_pos context not supported')
    else:
        _print(CS.SCP)
    try:
        yield
    finally:
        if nestable:
            move(*pos, False)
        else:
            _print(CS.RCP)


@contextmanager
def alternate_screen():
    """Use the `alternate screen buffer`_.

    .. _alternate screen buffer: https://invisible-island.net/xterm/ctlseqs/
       ctlseqs.html#h2-The-Alternate-Screen-Buffer

    This function is a context manager for use in ``with`` statements.
    It switches to the alternate screen buffer when the context is entered and
    back to the normal screen buffer when the context is exited.
    """
    _print(CS.EAS)
    try:
        yield
    finally:
        _print(CS.DAS)
