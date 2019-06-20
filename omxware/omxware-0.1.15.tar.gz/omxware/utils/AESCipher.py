#!/usr/bin/env python

import base64
import hashlib

from Crypto.Cipher import AES
from Crypto import Random

BS = 16
pad = lambda s: bytes(s + (BS - len(s) % BS) * chr(BS - len(s) % BS), 'utf-8')
unpad = lambda s : s[0:-s[-1]]


class AESCipher:

    def __init__( self, key='4D7A734FBE45C8A51A16E315696BFD95' ):
        self.key = hashlib.sha256(key.encode('utf-8')).digest()

    def encrypt( self, raw ):
        raw = pad(raw)
        iv = Random.new().read( AES.block_size )
        cipher = AES.new( self.key, AES.MODE_CBC, iv )
        enc = base64.b64encode( iv + cipher.encrypt( raw ) )
        enc_byte_arr = list(bytes(enc))
        enc_str = "".join(map(chr, enc_byte_arr))

        return enc_str

    def decrypt( self, enc ):
        enc = str.encode(enc)
        enc = base64.b64decode(enc)
        iv = enc[:16]
        cipher = AES.new(self.key, AES.MODE_CBC, iv )
        dec = unpad(cipher.decrypt( enc[16:] ))

        dec_byte_arr = list(bytes(dec))
        dec_str = "".join(map(chr, dec_byte_arr))

        return dec_str
