"""
    unpaddedbase32. Use base32 without padding in Python
    Copyright (C) 2019 Kevin Froman

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import base64

def b32encode(data):
    """Simply strips out b"=" from a bytes string and returns it"""
    data: bytes
    return base64.b32encode(data).replace(b"=", b"")

def b32decode(data):
    """Repad base32 bytes string, then decode it and return the result"""
    data: bytes
    if b"=" not in data:
        padding = 8 - (len(data) % 8) # base32 encodes 5 bytes to 8 characters
        data = data + (b"=" * padding)
    data = base64.b32decode(data)
    return data