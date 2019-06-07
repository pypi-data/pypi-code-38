# Pyrogram - Telegram MTProto API Client Library for Python
# Copyright (C) 2017-2019 Dan Tès <https://github.com/delivrance>
#
# This file is part of Pyrogram.
#
# Pyrogram is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pyrogram is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

from io import BytesIO

from pyrogram.api.core import *


class CodeSettings(TLObject):
    """Attributes:
        LAYER: ``100``

    Attributes:
        ID: ``0x302f59f3``

    Parameters:
        allow_flashcall (optional): ``bool``
        current_number (optional): ``bool``
        app_hash_persistent (optional): ``bool``
        app_hash (optional): ``str``
    """

    __slots__ = ["allow_flashcall", "current_number", "app_hash_persistent", "app_hash"]

    ID = 0x302f59f3
    QUALNAME = "types.CodeSettings"

    def __init__(self, *, allow_flashcall: bool = None, current_number: bool = None, app_hash_persistent: bool = None, app_hash: str = None):
        self.allow_flashcall = allow_flashcall  # flags.0?true
        self.current_number = current_number  # flags.1?true
        self.app_hash_persistent = app_hash_persistent  # flags.2?true
        self.app_hash = app_hash  # flags.3?string

    @staticmethod
    def read(b: BytesIO, *args) -> "CodeSettings":
        flags = Int.read(b)
        
        allow_flashcall = True if flags & (1 << 0) else False
        current_number = True if flags & (1 << 1) else False
        app_hash_persistent = True if flags & (1 << 2) else False
        app_hash = String.read(b) if flags & (1 << 3) else None
        return CodeSettings(allow_flashcall=allow_flashcall, current_number=current_number, app_hash_persistent=app_hash_persistent, app_hash=app_hash)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.allow_flashcall is not None else 0
        flags |= (1 << 1) if self.current_number is not None else 0
        flags |= (1 << 2) if self.app_hash_persistent is not None else 0
        flags |= (1 << 3) if self.app_hash is not None else 0
        b.write(Int(flags))
        
        if self.app_hash is not None:
            b.write(String(self.app_hash))
        
        return b.getvalue()
