import re
from pathlib import Path

from urwid.command_map import (
    ACTIVATE, CURSOR_DOWN, CURSOR_LEFT, CURSOR_MAX_LEFT, CURSOR_MAX_RIGHT,
    CURSOR_PAGE_DOWN, CURSOR_PAGE_UP, CURSOR_RIGHT, CURSOR_UP, REDRAW_SCREEN,
    command_map)

__all__ = ['COLOR_REGEXP', 'DEBUG', 'GRAPHNODETEMPLATE', 'PALETTE',
           'SUMMARY_TEMPLATE', 'TEMPLATE', 'get_hg']


DEBUG = False
SCREEN = None


_HGPATH = 'hg'

logger = None


def get_hg():
    """Return the hg executable."""
    return _HGPATH


PALETTE = [
    (None, '', '', '', '#fff', '#000'),
    ('', '', '', '', '#fff', '#000'),
    ('default', '', '', '', '#fff', '#000'),
    ('.focus', 'standout', '', 'standout', '#000', '#ffd'),

    ('log.changeset', '', '', '', '#999', '#000'),
    ('log.changeset.focus', 'standout', '', 'standout', '#000', '#ffd'),

    ('log.cwd', 'brown', '', 'standout', '#000', '#cc0'),
    ('log.cwd.focus', 'brown,standout', '', 'standout', '#000', '#ff4'),

    ('log.tag', 'dark red', '', '', '#f00', '#000'),
    ('log.tag.focus', 'dark red,standout', '', 'standout', '#f00,bold', '#ffd'),

    ('log.bookmark', 'dark blue', '', '', '#0af', '#000'),
    ('log.bookmark.focus', 'dark blue,standout', '', 'standout', '#0af,bold', '#ffd'),

    ('log.activebookmark', 'dark blue,standout', '', '', '#000', '#00f'),
    ('log.activebookmark.focus', 'dark blue,standout', '', 'standout', '#ffd,bold', '#00f'),
    ('bookmarks.active bookmarks.current', 'dark blue,standout', '', '', '#000,bold', '#00f'),

    ('log.node', 'brown', '', '', '#999', '#000'),
    ('log.node.focus', 'brown,standout', '', 'standout', '#666,bold', '#ffd'),

    ('log.user', 'dark blue', '', '', '#aac', '#000'),
    ('log.user.focus', 'dark blue,standout', '', 'standout', '#668,bold', '#ffd'),

    ('log.age', 'dark green', '', '', '#aca', '#000'),
    ('log.age.focus', 'dark green,standout', '', 'standout', '#686,bold', '#ffd'),

    ('log.description', '', '', '', '#fff', '#333'),
    ('log.description.focus', 'standout', '', 'standout', '#fff', '#333'),

    ('log.summary', '', '', '', '#fff', '#000'),
    ('log.summary.focus', 'standout', '', 'standout', '#000', '#ffd'),

    ('log.summary summary.wip', 'brown', '', '', '#000', '#f90'),
    ('log.summary summary.wip.focus', 'brown,standout', '', 'standout', '#000', '#f90'),

    ('log.branch', 'dark green,standout', '', '', '#000', '#0f7'),
    ('log.branch.focus', 'dark green,standout', '', 'standout', '#000', '#0f7'),

    ('branch.0', 'dark red', '', '', '#0f0', '#000'),
    ('branch.0.focus', 'dark red,standout', '', 'standout', '#ffd', '#0f0'),

    ('branch.1', 'dark blue', '', '', '#f00', '#000'),
    ('branch.1.focus', 'dark blue,standout', '', 'standout', '#ffd', '#f00'),

    ('branch.2', 'dark green', '', '', '#00f', '#000'),
    ('branch.2.focus', 'dark green,standout', '', 'standout', '#ffd', '#00f'),

    ('branch.3', 'brown', '', '', '#ff0', '#000'),
    ('branch.3.focus', 'brown,standout', '', 'standout', '#ffd', '#ff0'),

    ('branch.4', 'dark magenta', '', '', '#f0f', '#000'),
    ('branch.4.focus', 'dark magenta,standout', '', 'standout', '#ffd', '#f0f'),

    ('branch.5', 'dark cyan', '', '', '#0ff', '#000'),
    ('branch.5.focus', 'dark cyan,standout', '', 'standout', '#ffd', '#0ff'),

    ('branch.6', 'dark red', '', '', '#f50', '#000'),
    ('branch.6.focus', 'dark red,standout', '', 'standout', '#ffd', '#f50'),

    ('branch.7', 'dark blue', '', '', '#5f0', '#000'),
    ('branch.7.focus', 'dark blue,standout', '', 'standout', '#ffd', '#5f0'),

    ('branch.7', 'dark green', '', '', '#50f', '#000'),
    ('branch.7.focus', 'dark green,standout', '', 'standout', '#ffd', '#50f'),

    ('branch.8', 'brown', '', '', '#f05', '#000'),
    ('branch.8.focus', 'brown,standout', '', 'standout', '#ffd', '#f05'),

    ('branch.9', 'dark magenta', '', '', '#0f5', '#000'),
    ('branch.9.focus', 'dark magenta,standout', '', 'standout', '#ffd', '#0f5'),

    # ('topic.0', 'dark red,underline', '', '', '#0f0,underline', '#000'),
    ('topic.0', 'dark red,standout,underline', '', 'standout', '#0f0,underline', '#000'),
    ('topic.0.focus', 'dark red,standout,underline', '', 'standout', '#0a0,bold,underline', '#ffd'),

    ('topic.1', 'dark blue,underline', '', '', '#f00,underline', '#000'),
    ('topic.1.focus', 'dark blue,underline', '', '', '#a00,bold,underline', '#ffd'),

    ('topic.2', 'dark green,underline', '', '', '#44f,underline', '#000'),
    ('topic.2.focus', 'dark green,underline', '', '', '#44f,bold,underline', '#ffd'),

    ('topic.3', 'brown,underline', '', '', '#ee0,underline', '#000'),
    ('topic.3.focus', 'brown,underline', '', '', '#aa0,bold,underline', '#ffd'),

    ('topic.4', 'dark magenta,underline', '', '', '#e0e,underline', '#000'),
    ('topic.4.focus', 'dark magenta,underline', '', '', '#a0a,bold,underline', '#ffd'),

    ('topic.5', 'dark cyan,underline', '', '', '#0ee,underline', '#000'),
    ('topic.5.focus', 'dark cyan,underline', '', '', '#0aa,bold,underline', '#ffd'),

    ('topic.6', 'dark red,underline', '', '', '#f50,underline', '#000'),
    ('topic.6.focus', 'dark red,underline', '', '', '#a50,bold,underline', '#ffd'),

    ('topic.7', 'dark blue,underline', '', '', '#5f0,underline', '#000'),
    ('topic.7.focus', 'dark blue,underline', '', '', '#5a0,bold,underline', '#ffd'),

    ('topic.7', 'dark green,underline', '', '', '#50f,underline', '#000'),
    ('topic.7.focus', 'dark green,underline', '', '', '#50a,bold,underline', '#ffd'),

    ('topic.8', 'brown,underline', '', '', '#f05,underline', '#000'),
    ('topic.8.focus', 'brown,underline', '', '', '#a05,bold,underline', '#ffd'),

    ('topic.9', 'dark magenta,underline', '', '', '#0f5,underline', '#000'),
    ('topic.9.focus', 'dark magenta,underline', '', '', '#0a5,bold,underline', '#ffd'),

    ('diff.diffline', 'dark magenta,standout', '', '', '#000,bold', '#f0f'),
    ('diff.diffline.focus', 'dark magenta,standout', '', 'standout', '#000,bold', '#fdf'),

    ('diff.file', 'dark magenta', '', '', '#999', '#000'),
    ('diff.file.focus', 'dark magenta,standout', '', 'standout', '#999', '#333'),

    ('diff.hunk', 'dark magenta', '', '', '#f0f', '#000'),
    ('diff.hunk.focus', 'dark magenta,standout', '', 'standout', '#f0f,bold', '#333'),

    ('diff.context', 'white', '', '', '#fff', '#000'),
    ('diff.context.focus', 'white,standout', '', 'standout', '#fff,bold', '#333'),

    ('diff.inserted', 'dark green', '', '', '#0f0', '#000'),
    ('diff.inserted.focus', 'dark green,standout', '', 'standout', '#0f0,bold', '#333'),

    ('diff.deleted', 'dark red', '', '', '#f00', '#000'),
    ('diff.deleted.focus', 'dark red,standout', '', 'standout', '#f00,bold', '#333'),

    ('diffstat.inserted', 'dark green', '', '', '#0f0', '#000'),
    ('diffstat.inserted.focus', 'dark green,standout', '', 'standout', '#080,bold', '#ffd'),

    ('diffstat.deleted', 'dark red', '', '', '#f00', '#000'),
    ('diffstat.deleted.focus', 'dark red,standout', '', 'standout', '#f00,bold', '#ffd'),

    ('bisect.good', 'dark green', '', '', '#0f0', '#000'),
    ('bisect.good.focus', 'dark green,standout', '', 'standout', '#0f0', '#ffd'),

    ('bisect.bad', 'dark red', '', '', '#f00', '#000'),
    ('bisect.bad.focus', 'dark red,standout', '', 'standout', '#f00', '#ffd'),

    ('bisect.untested', 'brown', '', '', '#ff0', '#000'),
    ('bisect.untested.focus', 'brown,standout', '', 'standout', '#ff0', '#ffd'),

    ('ui.warning', 'brown', '', '', '#000,bold', '#f70'),
    ('ui.warning.focus', 'brown,standout', '', 'standout', '#000,bold', '#f92'),

    ('ui.button', 'dark blue,standout', '', '', '#000,bold', '#07b'),
    ('ui.button.focus', 'dark green,standout', '', 'standout', '#000,bold', '#0b7'),
    ('ui.button.disabled', 'dark blue,standout', '', '', '#0ab', '#07b'),

    ('ui.edit', 'dark green', '', '', '#000,bold', '#07b'),
    ('ui.edit.focus', 'white,standout', '', 'standout', '#000,bold', '#ffd'),

    ('ui.dialog', '', '', '', '#ffd', '#333'),
    ('ui.label', '', '', '', '#fff', '#07b'),
    ('ui.title', '', '', '', 'underline,bold', '#333'),
    ('ui.keyword', '', '', '', '#07f', ''),

    ('search.highlight', 'brown,standout', '', '', '#000', '#ff6'),
    ('search.highlight.focus', 'brown,standout', '', '', '#000', '#ff9'),

    ('shelve.age', 'dark green', '', '', '#494', '#000'),
    ('shelve.age.focus', 'dark green,standout', '', 'standout', '#484,bold', '#ffd'),

    ('shelve.newest', 'dark green', '', '', '#090', '#000'),
    ('shelve.newest.focus', 'dark green,standout', '', 'standout', '#090', '#ffd'),

    ('shelve.name', 'dark blue', '', '', '#009', '#000'),
    ('shelve.name.focus', 'dark blue,standout', '', 'standout', '#009', '#ffd'),

    ('shelve.description', '', '', '', '#999', '#000'),
    ('shelve.description.focus', 'standout', '', 'standout', '#999', '#ffd'),

]


GRAPHNODETEMPLATE = (
    r"{ifeq(node, 'ffffffffffffffffffffffffffffffffffffffff',"
    r"  '$',"
    r"  if(bisect,"
    r"    ifcontains('good', bisect, "
    r"      label('bisect.good', '✓'),"
    r"      ifcontains('bad', bisect,"
    r"        label('bisect.bad', 'X'),"
    r"        label('bisect.untested', '?'))),"
    r"    label('branch.{branch}',"
    r"      ifeq(obsolete, 'extinct',"
    r"        '-',"
    r"        ifeq(obsolete, 'suspended',"
    r"          'x',"
    r"          ifeq(obsolete, 'obsolete',"
    r"            '◌',"
    r"            if(troubles,"
    r"              '!',"
    r"              ifeq(phase, 'public',"
    r"              '●',"
    r"              ifeq(phase, 'draft',"
    r"                '◍',"
    r"                ifeq(phase, 'secret',"
    r"                  '○',"
    r"                  graphnode))))))))))}")

GRAPHNODETEMPLATE_ASCII = (
    r"{ifeq(node, 'ffffffffffffffffffffffffffffffffffffffff',"
    r"  '$',"
    r"  if(bisect,"
    r"    ifcontains('good', bisect, "
    r"      label('bisect.good', '*'),"
    r"      ifcontains('bad', bisect,"
    r"        label('bisect.bad', 'X'),"
    r"        label('bisect.untested', '?'))),"
    r"    label('branch.{branch}',"
    r"      ifeq(obsolete, 'extinct',"
    r"        '-',"
    r"        ifeq(obsolete, 'suspended',"
    r"          'x',"
    r"          ifeq(obsolete, 'obsolete',"
    r"            'x',"
    r"            if(troubles,"
    r"              '!',"
    r"              ifeq(phase, 'public',"
    r"              'o',"
    r"              ifeq(phase, 'draft',"
    r"                '#',"
    r"                ifeq(phase, 'secret',"
    r"                  '^',"
    r"                  graphnode))))))))))}")


BORDERS = '┌┐└┘┃┆━┈'
BORDERS_ASCII = '/\\\\/||=-'


TEMPLATE = (
    # r"{label("
    # r"   ifeq(graphnode, '@', 'log.cwd', 'log.changeset'),"
    r"{if(topics,"
    r"   label('topic.{topics}', topics)"
    r")}"
    r" "
    r'''{if(bookmarks,'''
    r'''    separate(" ", '''
    r'''        label('log.activebookmark', activebookmark),'''
    r'''        label('log.bookmark','''
    r'''              join('''
    r'''                  bookmarks % '{ifeq(bookmark, active, "", bookmark)}','''
    r'''                  ' '))), '''
    r'''    if(tags, '''
    r'''       label('log.tag', word(0, tags)),'''  # the first tag is enougth
    r'''       label('log.node', '{node|short}')))}'''
    r" "
    r"{label("
    r"  'log.summary {if(startswith('wip', lower(desc)), 'summary.wip', '')}',"
    r"  '{desc|firstline}')}"
    r" "
    r"{label('log.user', 'by {(author|user)}')}"
    r" "
    r"{label('log.age', date|age)}\n")


SUMMARY_TEMPLATE = (
    r"{ifeq(branch, 'default', '', label('log.branch', 'branch: {branch}\n'))}"
    r"{if(topics, label('topic.{topics}', 'topic: {topics}\n'))}"
    r"{if (bookmarks, label('log.bookmark', 'bookmark: {bookmarks}\n'))}"
    r"{label('log.changeset', 'rev: {rev}:{node}\n')}"
    r"{if(gitnode, label('log.changeset', 'git: {gitnode}\n'))}"
    r"{if(parents, label('log.changeset', 'parents: {parents}\n'))}"
    r"{if(children, label('log.changeset', 'children: {children}\n'))}"
    r"{label('log.user', 'author: {author}\n')}"
    r"{label('log.age', 'date: {date|isodate}\n')}"
)


SUMMARY_EXTRA_TEMPLATE = (
    r"{if(tags,"
    r"   label('log.tag', 'tags: {tags}\n'),"
    r"   label('log.tag', "
    r"         'lastest tag: {latesttag} ({latesttagdistance})\n'))}"
)


COLOR_REGEXP = re.compile('\x01(.*?)\x02(.*?)\x03+')
TOPIC_NAME_REGEXP = re.compile('.*\x02(.*?)\x03+')


CMD_FILTER = 'filter'
CMD_SEARCH = 'search'
CMD_REFRESH = 'refresh'
CMD_NEXT_MATCH = 'next match'
CMD_PREV_MATCH = 'prev match'
CMD_NEXT_RELATED = 'next related'
CMD_PREV_RELATED = 'prev related'
CMD_NEXT_WORD = 'next word'
CMD_PREV_WORD = 'prev word'
CMD_KILL_LINE = 'kill line'
CMD_KILL_PREV_CHAR = 'kill prev char'
CMD_KILL_PREV_WORD = 'kill prev word'
CMD_KILL_NEXT_WORD = 'kill next word'
CMD_NEXT_SELECTABLE = 'next selectable'
CMD_PREV_SELECTABLE = 'prev selectable'
CMD_MENU = 'menu'
CMD_ESCAPE = 'escape'

edit_command_map = command_map.copy()


def keybindings_default():
    command_map['tab'] = CMD_NEXT_SELECTABLE
    command_map['shift tab'] = CMD_PREV_SELECTABLE
    command_map['ctrl l'] = REDRAW_SCREEN
    command_map['up'] = CURSOR_UP
    command_map['down'] = CURSOR_DOWN
    command_map['left'] = CURSOR_LEFT
    command_map['right'] = CURSOR_RIGHT
    command_map['page up'] = CURSOR_PAGE_UP
    command_map['page down'] = CURSOR_PAGE_DOWN
    command_map['home'] = CURSOR_MAX_LEFT
    command_map['end'] = CURSOR_MAX_RIGHT
    command_map['enter'] = ACTIVATE
    command_map['ESC'] = CMD_ESCAPE

    command_map['ctrl f'] = CMD_FILTER
    command_map['/'] = CMD_SEARCH
    command_map['n'] = CMD_NEXT_MATCH
    command_map['N'] = CMD_PREV_MATCH
    command_map['ctrl r'] = CMD_REFRESH
    command_map['meta up'] = CMD_PREV_RELATED
    command_map['meta down'] = CMD_NEXT_RELATED
    command_map['backspace'] = CMD_KILL_PREV_CHAR

    edit_command_map['ctrl right'] = CMD_NEXT_WORD
    edit_command_map['ctrl left'] = CMD_PREV_WORD
    edit_command_map['ctrl k'] = CMD_KILL_LINE
    edit_command_map['meta backspace'] = CMD_KILL_PREV_WORD


def keybindings_mouse():
    command_map[('mouse press', 3)] = ACTIVATE
    command_map[('mouse press', 4)] = CURSOR_PAGE_UP
    command_map[('mouse press', 5)] = CURSOR_PAGE_DOWN
    command_map[('meta mouse press', 4)] = CMD_PREV_RELATED
    command_map[('meta mouse press', 5)] = CMD_NEXT_RELATED
    command_map[('ctrl mouse press', 4)] = CMD_PREV_MATCH
    command_map[('ctrl mouse press', 5)] = CMD_NEXT_MATCH


def keybindings_vim():
    command_map['ctrl w'] = CMD_NEXT_SELECTABLE
    command_map['shift tab'] = CMD_PREV_SELECTABLE
    command_map['ctrl l'] = REDRAW_SCREEN
    command_map['k'] = CURSOR_UP
    command_map['j'] = CURSOR_DOWN
    command_map['h'] = CURSOR_LEFT
    command_map['l'] = CURSOR_RIGHT
    command_map['ctrl b'] = CURSOR_PAGE_UP
    command_map['ctrl f'] = CURSOR_PAGE_DOWN
    command_map['^'] = CURSOR_MAX_LEFT
    command_map['$'] = CURSOR_MAX_RIGHT
    command_map[':'] = ACTIVATE
    command_map['ESC'] = CMD_ESCAPE
    command_map['ctrl c'] = CMD_ESCAPE

    command_map['ctrl f'] = CMD_FILTER
    command_map['/'] = CMD_SEARCH
    command_map['n'] = CMD_NEXT_MATCH
    command_map['N'] = CMD_PREV_MATCH
    command_map['ctrl r'] = CMD_REFRESH
    command_map['meta k'] = CMD_PREV_RELATED
    command_map['meta j'] = CMD_NEXT_RELATED
    command_map['backspace'] = CMD_KILL_PREV_CHAR

    edit_command_map['down'] = CURSOR_DOWN
    edit_command_map['left'] = CURSOR_LEFT
    edit_command_map['right'] = CURSOR_RIGHT
    edit_command_map['page up'] = CURSOR_PAGE_UP
    edit_command_map['page down'] = CURSOR_PAGE_DOWN
    edit_command_map['home'] = CURSOR_MAX_LEFT
    edit_command_map['end'] = CURSOR_MAX_RIGHT

    edit_command_map['shift right'] = CMD_NEXT_WORD
    edit_command_map['shift left'] = CMD_PREV_WORD
    edit_command_map['ctrl k'] = CMD_KILL_LINE
    edit_command_map['meta backspace'] = CMD_KILL_PREV_WORD
    edit_command_map['meta d'] = CMD_KILL_NEXT_WORD


def keybindings_emacs():
    command_map['ctrl o'] = CMD_NEXT_SELECTABLE
    command_map['meta o'] = CMD_PREV_SELECTABLE
    command_map['ctrl l'] = REDRAW_SCREEN
    command_map['ctrl p'] = CURSOR_UP
    command_map['ctrl n'] = CURSOR_DOWN
    command_map['ctrl b'] = CURSOR_LEFT
    command_map['ctrl f'] = CURSOR_RIGHT
    command_map['meta v'] = CURSOR_PAGE_UP
    command_map['ctrl v'] = CURSOR_PAGE_DOWN
    command_map['ctrl a'] = CURSOR_MAX_LEFT
    command_map['ctrl e'] = CURSOR_MAX_RIGHT
    command_map['meta x'] = ACTIVATE
    command_map['esc'] = CMD_ESCAPE
    command_map['ctrl g'] = CMD_ESCAPE

    command_map['ctrl f'] = CMD_FILTER
    command_map['/'] = CMD_SEARCH
    command_map['n'] = CMD_NEXT_MATCH
    command_map['p'] = CMD_PREV_MATCH
    command_map['f5'] = CMD_REFRESH
    command_map['meta p'] = CMD_PREV_RELATED
    command_map['meta n'] = CMD_NEXT_RELATED
    command_map['backspace'] = CMD_KILL_PREV_CHAR

    edit_command_map['meta f'] = CMD_NEXT_WORD
    edit_command_map['meta b'] = CMD_PREV_WORD
    edit_command_map['ctrl k'] = CMD_KILL_LINE
    edit_command_map['meta d'] = CMD_KILL_NEXT_WORD
    edit_command_map['meta backspace'] = CMD_KILL_PREV_WORD


def keybindings_elinks():
    keybindings_default()

    command_map['>'] = CMD_NEXT_SELECTABLE
    command_map['<'] = CMD_PREV_SELECTABLE
    command_map['ctrl l'] = REDRAW_SCREEN
    command_map['insert'] = CURSOR_UP
    command_map['delete'] = CURSOR_DOWN
    command_map['ctrl p'] = CURSOR_UP
    command_map['ctrl n'] = CURSOR_DOWN


KEYBINDINGS_SETTERS = {
    'default': keybindings_default,
    'mouse': keybindings_mouse,
    'vim': keybindings_vim,
    'emacs': keybindings_emacs,
    'elinks': keybindings_elinks,
}

# Load user defined configuration
CONFIG_FILE_PATH = Path('~/.config/lairucrem/config.py').expanduser()
if CONFIG_FILE_PATH.exists():
    exec(CONFIG_FILE_PATH.read_text())
