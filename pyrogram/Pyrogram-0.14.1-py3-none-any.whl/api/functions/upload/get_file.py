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


class GetFile(TLObject):
    """Attributes:
        LAYER: ``100``

    Attributes:
        ID: ``0xe3a6cfb5``

    Parameters:
        location: Either :obj:`InputFileLocation <pyrogram.api.types.InputFileLocation>`, :obj:`InputEncryptedFileLocation <pyrogram.api.types.InputEncryptedFileLocation>`, :obj:`InputDocumentFileLocation <pyrogram.api.types.InputDocumentFileLocation>`, :obj:`InputSecureFileLocation <pyrogram.api.types.InputSecureFileLocation>`, :obj:`InputTakeoutFileLocation <pyrogram.api.types.InputTakeoutFileLocation>`, :obj:`InputPhotoFileLocation <pyrogram.api.types.InputPhotoFileLocation>`, :obj:`InputPeerPhotoFileLocation <pyrogram.api.types.InputPeerPhotoFileLocation>` or :obj:`InputStickerSetThumb <pyrogram.api.types.InputStickerSetThumb>`
        offset: ``int`` ``32-bit``
        limit: ``int`` ``32-bit``

    Returns:
        Either :obj:`upload.File <pyrogram.api.types.upload.File>` or :obj:`upload.FileCdnRedirect <pyrogram.api.types.upload.FileCdnRedirect>`
    """

    __slots__ = ["location", "offset", "limit"]

    ID = 0xe3a6cfb5
    QUALNAME = "functions.upload.GetFile"

    def __init__(self, *, location, offset: int, limit: int):
        self.location = location  # InputFileLocation
        self.offset = offset  # int
        self.limit = limit  # int

    @staticmethod
    def read(b: BytesIO, *args) -> "GetFile":
        # No flags
        
        location = TLObject.read(b)
        
        offset = Int.read(b)
        
        limit = Int.read(b)
        
        return GetFile(location=location, offset=offset, limit=limit)

    def write(self) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        # No flags
        
        b.write(self.location.write())
        
        b.write(Int(self.offset))
        
        b.write(Int(self.limit))
        
        return b.getvalue()
