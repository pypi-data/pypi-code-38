#!/usr/bin/env python3
#
# Multiprocessing wrapper for miniirc
#

import miniirc
from . import AbstractIRC, Hostmask, utils
from typing import Dict, Tuple, List, Set, Union

_hg = utils.HandlerGroup()

class Message:
    __slots__ = ('command', 'hostmask', 'tags', 'args')
    def __bytes__(self) -> bytes:
        return utils.ircv3_message_unparser(self.command, self.hostmask,
        self.tags, self.args)

    def __str__(self) -> str:
        return bytes(self).decode('utf-8', 'replace')

    def __repr__(self) -> str:
        return '<{} for {}>'.format(type(self).__name__, self)

    def __init__(self, command: str, hostmask: utils._hostmask,
            tags: Dict[str, Union[str, bool]], args: List[str]) -> None:
        """
        Creates a new Message instance. This function's parameters may change
        in the future.
        """
        self.command = command # type: str
        self.hostmask = hostmask # type: utils._hostmask
        self.tags = tags # type: Dict[str, Union[str, bool]]
        self.args = args # type: List[str]

@_hg.CmdHandler(ircv3 = True)
@utils.remove_colon
def _handler(irc, command, hostmask, tags, args):
    msg = Message(command, hostmask, tags, args)
