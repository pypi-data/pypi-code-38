#! /usr/bin/env python
# coding: utf-8
# Copyright (C) 2016 Alain Leufroy
#
# Author: Alain Leufroy <alain@leufroy.fr>
# Licence: WTFPL, grab your copy here: http://sam.zoy.org/wtfpl/
"""Commands that can be processed depending on a given changeset."""

import asyncio
import asyncio.tasks
import os
import re
import tempfile
from datetime import datetime
from functools import lru_cache, partial
from pathlib import Path

from . import process
from .process import hg_plain
from .utils import async_contextmanager, nodestr, shelvestr
from .widgets import dialog

#


@lru_cache()
async def get_rootpath():
    """Return the repository root path as a pathlib.Path object."""
    root = await process.hg_plain('root')
    return Path(root.strip())


async def _hg_monitored(*cmd, message='Please wait.', title='Processing…'):
    """Execute an Hg command and display a poup while processing."""
    coro = hg_plain(*cmd)
    return await dialog.popup_processing(
        task=coro,
        message=message, title=title)


class selection:

    def __init__(self):
        self._tasks = {}

    async def _isnode(selectors, node):
        return isinstance(node, nodestr)

    async def _isshelve(selectors, node):
        return isinstance(node, shelvestr)

    async def _iscwd(selectors, node):
        return node is None

    async def _isclean(selectors, _node):
        """Return True is CWD is clea"""
        res = await hg_plain(
            'status', '--modified', '--added', '--removed', '--deleted', '--print0')
        return not res

    async def _phase(selectors, node):
        """Return the phase name of the given cset."""
        if not (await selectors.isnode):
            return False
        phaseinfo = await hg_plain('phase', '--rev', node)
        return phaseinfo.split(':')[-1].strip()

    async def _isotherbranch(selectors, node):
        """Return True if the given cset is on other branch than CWD."""
        if not (await selectors.isnode):
            return False
        revset = 'ancestor(%(c)s,.) and not %(c)s' % {'c': node}
        res = await hg_plain('log', '--rev', revset, '--template', "{node}")
        return bool(res)

    async def _isrebasable(selectors, node):
        """Return True if the given cset can be rebased."""
        if not (await selectors.isnode):
            return False
        if not node or ((await selectors.phase) == 'public'):
            return False
        return await selectors.isotherbranch

    async def _bookmarks(selectors, node):
        if not (await selectors.isnode):
            return []
        bookmarks = ''.join([bkmk async for bkmk in process.hg(
            'log', '--template', r'{join(bookmarks, "\0")}', '--rev', node)])
        if bookmarks:
            bookmarks = bookmarks.split('\0')
        return bookmarks

    selectors = {
        'isnode': _isnode,
        'isshelve': _isshelve,
        'iscwd': _iscwd,
        'isclean': _isclean,
        'phase': _phase,
        'isotherbranch': _isotherbranch,
        'isrebasable': _isrebasable,
        'bookmarks': _bookmarks,
    }

    def __getattr__(self, name):
        if name not in self._tasks:
            raise AttributeError(f'Unkown selector: {name}')
        return self._tasks[name]

    async def fetch(self, node):
        self._tasks = {
            name: asyncio.tasks.Task(coroutine(self, node))
            for name, coroutine in self.selectors.items()
        }
        await asyncio.gather(*self._tasks.values())


@async_contextmanager
async def _auto_manage_durty(description: str, *, selectors):
    """Automatically shelve/unshelve if the cwd is durty.

    Shelve is performed before all, then unshelve is performed after all (if no
    errors).

    description: message used as the shelve description
    """
    isdurty = not await selectors.isclean
    # we simply use the timestamp as shelve hash (a.k.a. `name`)
    name = '%f.3' % datetime.now().timestamp()
    if isdurty:
        res = await _hg_monitored(
            '--config', 'extensions.hgext.shelve=', 'shelve',
            '--message', '[lairucrem operation] ' + description,
            '--name', name,
            message=f'Shelving current changes in "{name}".')
        if not res:
            raise asyncio.CancelledError()
    try:
        yield
    except OSError:
        await dialog.simple(
            f'Could not restore changes automatically shelved in "{name}"',
            title='Restore durty state. Please wait.')
        raise
    else:
        if isdurty:
            try:
                await _hg_monitored(
                    '--config', 'extensions.hgext.shelve=', 'unshelve',
                    name, message='Unshelve changes. Please wait.')
            except OSError as err:
                await _hg_monitored(
                    '--config', 'extensions.hgext.shelve=', 'unshelve',
                    '--abort', message="Abort restoration.")
                await dialog.simple(
                    f'Could not restore changes shelved in "{name}"',
                    title='Restore durty changes')


@async_contextmanager
async def _auto_update():
    """Automatically update the cwd to the current cset `.` or its latest successor if rebased."""
    curnode = await hg_plain('log', '--hidden', '--rev', '.', '--template', '{node}')
    yield
    output = await hg_plain('log', '--hidden', '--rev', f'allsuccessors({curnode})', '--template', '{node},')
    if output:
        curnode = output.rstrip(',').rsplit(',', 1)[-1]
    await process.hg_interactive('update', '--rev', curnode)


async def commit(node, *, selectors):
    """Commit the cwd interactively."""
    if (await selectors.iscwd) and not (await selectors.isclean):
        return 'commit', partial(
            process.hg_interactive, 'commit', '--interactive')
    return None


async def revert(node, *, selectors):
    """revert files interactively."""
    if (await selectors.isshelve):
        return None
    if await (selectors.iscwd) and not (await selectors.isclean):
        return 'revert modified files', partial(
            process.hg_interactive, 'revert', '--interactive')
    if (await selectors.isnode):
        return 'revert', partial(
            process.hg_interactive, 'revert', '--interactive', '--rev', node)
    return None


async def shelve(node, *, selectors):
    """Save and set aside changes from the working directory.

    Shelvinf takes files from the durty working directory, saves the
    modifications to a bundle and reverts files so that their state in
    the working directory becomes clean.
    """
    if not (await selectors.iscwd) or (await selectors.isclean):
        return None
    return 'shelve', partial(
        process.hg_interactive, '--config', 'extensions.hgext.shelve=',
        'shelve', '--interactive', '--edit')


async def update(node, *, selectors):
    """Update working directory (or switch revisions)

    Update the repository's working directory to the specified changeset.
    """
    if not (await selectors.isnode):
        return
    return 'update', partial(_do_update, node, selectors=selectors)


async def _do_update(node, *, selectors):
    bookmarks = await selectors.bookmarks
    if bookmarks:
        title = 'Bookmark selection'
        prolog = ('Bookmark(s) found on this changeset. '
                  'Select the one to be activated or cancel for none of them:')
        choice = await dialog.choices(bookmarks, title, prolog)
        if choice is not None:
            node = bookmarks[choice]
    async with _auto_manage_durty('update', selectors=selectors):
        await process.hg_interactive('update', '--rev', node)


async def histedit(node, *, selectors):
    """perform `histedit' if the repository is clean"""
    if not (await selectors.isnode) or not (await selectors.isclean):
        return None
    return 'histedit', partial(
        process.hg_interactive, '--config', 'extensions.hgext.histedit=',
        'histedit', '--rev', node)


async def rebase(node, *, selectors):
    """Move changeset (and descendants) onto of the working directory"""
    if not (await selectors.isnode) or not (await selectors.isrebasable):
        return None
    return 'rebase', partial(_do_rebase, selectors=selectors, source=node)


async def rebase_one(node, *, selectors):
    """Move changeset onto the working directory"""
    if not (await selectors.isnode) or not (await selectors.isrebasable):
        return None
    return 'rebase one', partial(_do_rebase, selectors=selectors, rev=node)


async def graft_one(node, *, selectors):
    """Move changeset onto the working directory"""
    if not (await selectors.isnode) or not (await selectors.isrebasable):
        return None
    return 'graft one', partial(
        _do_rebase, selectors=selectors, rev=node, keep=True)


async def _do_rebase(*, selectors, dest='.', **kwargs):
    """Rebase the given source cset onto dest and update to tip."""

    cmd = ['--config', 'extensions.hgext.rebase=', 'rebase',
           '--dest', dest]
    for opt, value in kwargs.items():
        if value is True:
            cmd.append('--' + opt)
        elif value:
            cmd += ['--' + opt, value]
    abortion = partial(process.hg_interactive, 'rebase', '--abort')
    continuation = partial(process.hg_interactive, 'rebase', '--continue')
    async with _auto_manage_durty('rebase', selectors=selectors):
        async with _abort_continue(continuation, abortion):
            await process.hg_interactive(*cmd)
        await process.hg_interactive('update', '--rev', 'tip')


@async_contextmanager
async def _abort_continue(continuecoro, abortcoro):
    try:
        yield
    except OSError as err:
        if 'conflicts while' not in err.strerror.lower():
            raise
    else:
        return
    result = await resolve()
    if not result:
        result = await dialog.ask(
            'Remaining unresolved file. Abort?',
            title='Abort')
        if result:
            await abortcoro()
        return
    if result:
        choices = ['continue', 'abort']
        choice = await dialog.choices(
            choices,
            title='Continue',
            prolog='All file resolved!')

        if choice is None:
            return
        if choices[choice] == 'continue':
            await continuecoro()
        else:
            await abortcoro()


async def resolve():
    """Request user to resolve files.

    :return: True if all file have been resolved, False otherwise.
    :rtype: bool
    """
    while True:
        res = await hg_plain('resolve', '--list')
        lines = [line.strip() for line in res.splitlines() if line.strip()]
        if not lines:
            return True         # ok, nothing to resolve
        statuses, filenames = list(
            zip(*(line.split(None, 1) for line in lines)))
        statuses = [status == 'R' for status in statuses]
        if all(statuses):
            return True         # ok, all resolved
        diag = dialog.select(
            filenames, statuses, title='Resolve',
            prolog='Remaining unresolved file.')
        refresh = object()
        diag.append_button('refresh', refresh, 'ctrl r')
        result = await diag
        if result is refresh:
            continue
        if result is None:
            return False
        toresolve = {filenames[index] for index in result}
        tounresolve = set(filenames) - toresolve
        if toresolve:
            await hg_plain('resolve', '--mark', *toresolve)
        if tounresolve:
            await hg_plain('resolve', '--unmark', *tounresolve)


async def merge(node, *, selectors):
    """Merge the focused changeset onto the current changeset."""
    if (not (await selectors.isnode) or not (await selectors.isclean)
            or not (await selectors.isotherbranch)):
        return None
    return 'merge', partial(_do_merge, node, selectors=selectors)


async def _get_node_info_for_merge(node):
    output = await hg_plain(
        'log', '--rev', node,
        '--template', '{tags},{join(topics, ",")},,{join(bookmarks, ",")},{branch}')
    return next(info for info in output.split(',') if info not in ('tip', ''))


async def _do_merge(node, *, selectors):
    """Merge the given cset to the CWD."""
    continuation = partial(process.hg_interactive, 'commit')
    abortion = partial(process.hg_interactive, 'up', '-C', '.')
    target = await _get_node_info_for_merge(node)
    dest = await _get_node_info_for_merge('.')
    default_message = f'merge {target} into {dest}'
    async with _auto_manage_durty('Merge', selectors=selectors):
        async with _abort_continue(continuation, abortion):
            await process.hg_interactive('merge', '--rev', node)
            await process.hg_interactive('commit', '--message', default_message, '--edit')


async def edit_description(node, *, selectors):
    """Edit the commit description of the given cset and rebase children."""
    if (not (await selectors.isnode) or (await selectors.phase) == 'public'):
        return None
    return 'edit description', partial(_do_edit_description, node, selectors)


async def _do_edit_description(node, selectors):
    """Edit the commit description of the given cset and rebase children."""
    async with _auto_manage_durty('update', selectors=selectors):
        async with _auto_update():
            revset = 'children(%s)' % node
            torebases = await hg_plain('log', '--template', r'{node}\0', '--rev', revset)
            await process.hg_interactive('update', '--rev', node)
            await process.hg_interactive('commit', '--edit', '--amend')
            if not torebases:
                return
            newcset = await hg_plain('log', '--limit', '1', '--template', '{node}')
            newcset = newcset.strip()
            for node in torebases.split('\0'):
                node = node.strip()
                if node:
                    await process.hg_interactive(
                        '--config', 'extensions.hgext.rebase=', 'rebase',
                        '--source', node, '--dest', newcset)


async def strip(node, *, selectors):
    """strip the given cset."""
    if not (await selectors.isnode) or (await selectors.phase) == 'public':
        return False
    return 'strip', partial(
        process.hg_interactive, '--config', 'extensions.hgext.strip=', 'strip',
        '--rev', node)


async def addremove(node, *, selectors):
    """add all new files, delete all missing files.
    """
    if not (await selectors.iscwd):
        return None
    status = await hg_plain('status', '--unknown', '--deleted', '--print0')
    status.strip()
    if not status:
        return None
    return 'addremove', partial(_do_addremove, status)


async def _do_addremove(status):
    styles = {'!': 'diff.deleted', '?': None}
    infos = [info for info in status.split('\0') if info]
    infos = list(sorted(infos))
    selects = [[(styles[info[0]], info)] for info in infos]
    states = [info[0] == '!' for info in infos]
    prolog = 'Select files to add (?) and to remove (!):'
    indexes = await dialog.select(
        selects, states, title='add remove', prolog=prolog)
    if not indexes:
        return
    infos = [infos[index] for index in indexes]
    fnames = [info[2:] for info in infos]
    await process.hg_interactive('addremove', *fnames)


async def push(node, *, selectors):
    """push changes to the default destination"""
    if not (await selectors.isnode):
        return None
    return 'push', partial(_do_push, node, selectors=selectors)


async def _do_push(node, *, selectors):
    paths = await _select_remote_path()
    if paths is None:
        return
    if (await selectors.phase) == 'secret':
        await _change_phase(
            node, phases=['public', 'draft'], title='Change phase before push')
    bookmarks = await selectors.bookmarks
    if bookmarks:
        choices = await dialog.select(
            bookmarks, title='Push bookmarks',
            prolog='Select bookmarks to push or cancel to push none:')
        bookmarks = [bookmarks[choice] for choice in choices]
    cmd = ['push', '--rev', node]
    for bookmark in (bookmarks or ()):
        cmd += ['--bookmark', bookmark]
    for path in paths:
        _cmd = cmd + [path]
        await _effective_push(_cmd)


async def _select_remote_path():
    paths = None
    while not paths:
        try:
            paths = await hg_plain('paths')
        except OSError:
            paths = ''
        if not paths:
            answer = await dialog.ask(
                'No remote path found. Would you like to add one?',
                title='Edit remote paths')
            if answer:
                await process.hg_interactive('showconfig', '--edit', '--local')
            else:
                return None
    paths = [re.split(r'\s*=\s*', path) for path in paths.splitlines()]
    _paths = [path[0] for path in paths]
    if len(paths) > 1:
        choices = ['{0} ({1})'.format(*path) for path in paths]
        default = 'default-push' if 'default-push' in _paths else 'default'
        states = [path == default for path in _paths]
        selection = await dialog.select(
            choices, states,
            title='Select remote paths',
            prolog='Select a the remote paths to push to:')
        if selection is None:
            return None
    else:
        selection = [0]
    return [paths[index][0] for index in selection]


async def _change_phase(
        node, phases=('secret', 'draft', 'public'), title=None):
    choice = await dialog.choices(
        phases, title=title or 'Change phase before push',
        prolog='Select a proper phase for the changeset:')
    if choice is None:
        return None
    phase = phases[choice]
    await process.hg_interactive(
        'phase', '--' + phase, '--rev', node, '--force')
    return phase


async def _effective_push(cmd):
    _cmd = cmd[:]
    while True:
        try:
            await process.hg_interactive(*_cmd)
        except OSError as err:
            mess = err.strerror.lower()
            if not mess:
                await dialog.simple('Already pushed!', title='Done')
                return
            elif 'push creates new remote branches' in err.strerror.lower():
                answer = await dialog.ask(
                    err.strerror + '\n\Push the new branch?',
                    title='Push creates new branch')
                if answer:
                    _cmd = cmd[:]
                    _cmd.insert(1, '--new-branch')
                    continue
                else:
                    return
            else:
                answer = await dialog.ask(
                    err.strerror + '\n\nWould you like to force push?',
                    title='Push force')
                if answer:
                    _cmd = cmd[:]
                    _cmd.insert(1, '--force')
                    continue
                else:
                    return
        else:
            return


async def unshelve(shelvename, *, selectors):
    """Check if they are shelved, if so list them"""
    if not (await selectors.isshelve):
        return None
    return 'unshelve', partial(_do_unshelve, shelvename)


async def _do_unshelve(shelvename):
    """Unshelve the specified shelve or the last one."""
    continuation = partial(
        process.hg_interactive, '--config', 'extensions.hgext.shelve=',
        'unshelve', '--continue')
    abortion = partial(
        process.hg_interactive, '--config', 'extensions.hgext.shelve=',
        'unshelve', '--abort')
    async with _abort_continue(continuation, abortion):
        cmd = ['--config', 'extensions.hgext.shelve=', 'unshelve']
        if shelvename:
            cmd.append(shelvename)
        await process.hg_interactive(*cmd)


async def delshelve(shelve, *, selectors):
    """Check if they are shelved, if so list them"""
    if not (await selectors.isshelve):
        return None
    return 'delete shelve', partial(
        process.hg_interactive, 'shelve', '--delete', shelve)


async def edit_bookmarks(node, *, selectors):
    if not (await selectors.isnode):
        return None
    return 'edit bookmarks', partial(_do_edit_bookmarks, node)


async def _do_edit_bookmarks(node):
    # prépare a temporary file for bookmark editing
    bookmarks = await hg_plain(
        'log', '--rev', node, '--template', '{join(bookmarks, "\\0")}')
    bookmarks = {bookmark for bookmark in bookmarks.split('\0') if bookmark}
    content = ('# -*- encoding: utf-8 -*-\n'
               '# Add one bookmark name per line\n'
               '# Leave unchanged to cancel operation\n'
               '# Line starting with "#" and blank lines are ignored\n'
               '# Leading and trailing blanks are trimed.\n')
    content += '\n'.join(sorted(bookmarks))
    with tempfile.NamedTemporaryFile() as fobj:
        fobj.write(content.encode('utf-8'))
        fobj.flush()
        await process.interactive(await _get_editor(), fobj.name)
        fobj.seek(0)
        content = fobj.read().decode('utf-8')
    names = {line for line in content.splitlines()
             if line and not line.strip().startswith('#')}
    deleted = bookmarks - names
    added = names - bookmarks
    if deleted:
        await hg_plain('bookmark', '--delete', *deleted)
    if added:
        await hg_plain('bookmark', '--rev', node, *added)


async def _get_editor():
    """Return the user editor."""
    try:
        editor = await hg_plain('showconfig', 'ui.editor')
        return editor.rstrip('\n')
    except OSError:
        pass
    return os.environ.get('EDITOR') or 'nano'


async def forward_last_bookmark(node, *, selectors):
    if not (await selectors.isnode):
        return None
    return 'forward last bookmark', partial(_do_forward_last_bookmark, node)


async def _do_forward_last_bookmark(node):
    bookmark = await hg_plain(
        'log', '--rev', f'last((last(merge() or 0)::({node}~1)) and bookmark())',
        '--template', r'{bookmarks}')
    bookmark = bookmark.strip()
    if not bookmark:
        await dialog.simple(
            'No bookmark found until the last merge.', title='Not Found')
        return
    answer = await dialog.ask(f'Move {bookmark} to {node}?', title='FORWARD BOOKMARK')
    if answer is None:
        return
    await process.hg_interactive('bookmark', '--rev', node, bookmark)


async def prune(node, *, selectors):
    if not (await selectors.isnode):
        return None
    return 'prune node', partial(process.hg_interactive, 'prune', '--rev', node)


cset_command_getters = [
    commit,
    shelve,
    revert,
    update,
    histedit,
    rebase,
    rebase_one,
    graft_one,
    merge,
    edit_description,
    strip,
    addremove,
    push,
    unshelve,
    delshelve,
    edit_bookmarks,
    forward_last_bookmark,
    prune,
]
