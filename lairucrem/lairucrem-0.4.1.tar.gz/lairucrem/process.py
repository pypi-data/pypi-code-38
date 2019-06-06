#! /usr/bin/env python
# Copyright (C) 2016 Alain Leufroy
#
# Author: Alain Leufroy <alain@leufroy.fr>
# Licence: WTFPL, grab your copy here: http://sam.zoy.org/wtfpl/
"""The lairucrem librairy."""

import asyncio
import os
import shlex
import sys
from typing import AsyncIterable

from . import config, get_extension_path, interrupt_mainloop
from .config import get_hg

#


async def _wait_process(proc, cmd=''):
    """Wait for the process and handle error.

    Raises:

      OSError: if the process returns a non-zero code.
    """
    await proc.wait()
    if proc.returncode:
        msg = await proc.stderr.read()
        msg = msg.decode(sys.getdefaultencoding())
        msg = cmd + '\n\n' + msg
        raise OSError(proc.returncode, msg)


class hg:
    """Async generator yielding mercurial command outputs.

    args:

      Mercurial command component (without `hg` executable).

    kwargs:

      Their are passed to `asyncio.create_subprocess_exec`.

    Raises:

      OSError: if the process returns a non-zero code.
    """

    def __init__(self, *args, **kwargs):
        self.proc = None
        self.cmd = ''
        self.args = args
        if 'stdout' not in kwargs:
            kwargs['stdout'] = asyncio.subprocess.PIPE
        if 'stder' not in kwargs:
            kwargs['stderr'] = asyncio.subprocess.PIPE
        self.kwargs = kwargs
        self.paused = False

    async def start(self):
        if self.proc is None:
            args = (
                get_hg(),
                '--encoding', 'utf-8',
                '--config', 'extensions.lairucrem=%s' % get_extension_path(),
                '--color', 'debug',
                '--config', 'extensions.pager=',
                '--page', 'never'
            )
            if config.DEBUG:
                args += ('--traceback',)
            args += self.args
            self.cmd = ' '.join(args)
            try:
                self.proc = await asyncio.create_subprocess_exec(
                    *args, loop=asyncio.get_event_loop(), **self.kwargs
                )
            except FileNotFoundError as exc:
                message = ('Could not found a proper `hg` executable.'
                           '\nUse --with-hg to specify the executable path.')
                raise FileNotFoundError(message) from exc
        trans = self.proc._transport.get_pipe_transport(1)
        if trans._loop is None:  # asyncio forgets to set the loop :/
            trans._loop = asyncio.get_event_loop()
        return self.proc

    async def __aiter__(self) -> AsyncIterable:
        await self.start()
        val = await self._read_stdout_line()
        while val:
            yield val.decode('utf-8', 'replace')
            val = await self._read_stdout_line()
        await self.stop()

    async def _read_stdout_line(self):
        """Iter over process stdout lines."""
        # Asyncio raises a ValueError when a line exceeds the buffer limit.
        # We can safely wait for more data.
        while True:
            try:
                return await self.proc.stdout.readline()
            except ValueError:
                continue

    async def stop(self):
        await _wait_process(self.proc, cmd=self.cmd)
        self.proc = None

    def isrunning(self):
        return self.proc and self.proc.pid is not None

    def pause(self):
        """Pause the process if it's running.

        Pause reading the process output. The system will pause the process
        when the output cache is fullfilled.
        """
        if (not self.paused and self.isrunning()):
            trans = self.proc._transport.get_pipe_transport(1)
            trans.pause_reading()
            self.paused = True

    def resume(self):
        """Pause the process if paused.

        Resume reading the process output. The system will restart the the
        process when the output cache is consumed.
        """
        if (self.paused and self.isrunning()):
            trans = self.proc._transport.get_pipe_transport(1)
            if trans._loop is None:  # asyncio forgot to add the loop :/
                trans._loop = asyncio.get_event_loop()
            try:
                trans.resume_reading()
            except OSError:
                if config.DEBUG:
                    raise
            self.paused = False


async def interactive(*args, **kwargs):
    """Coroutine that runs a *shell* command interactively (stdout not piped).

    The main loop is interrupted during the command execution.
    If the return code is not 0, raise an OSError with `strerror` containing
    the stderr message.

    *args:

      Command shell component. `shlex.quote` is used to construct the shell
      command.

    kwargs:

      Their are passed to `asyncio.create_subprocess_shell`

    """
    cmd = ' '.join(shlex.quote(arg) for arg in args)
    with interrupt_mainloop():
        proc = await asyncio.create_subprocess_shell(
            cmd, stderr=asyncio.subprocess.PIPE, **kwargs)
        await _wait_process(proc, cmd=cmd)


async def hg_interactive(*args, **kwargs):
    """Coroutine that runs an hg command interactively (stdout not piped).

    The main loop is interrupted during the command execution.
    If the return code is not 0, raise an OSError with `strerror` containing
    the stderr message.
    """
    await interactive(get_hg(), *args, **kwargs)


async def hg_plain(*cmd):
    """Execute an Hg command in plain mode and return overall results."""
    env = os.environ.copy()
    env['HGPLAIN'] = '1'
    return ''.join([line async for line in hg(*cmd, env=env)])
