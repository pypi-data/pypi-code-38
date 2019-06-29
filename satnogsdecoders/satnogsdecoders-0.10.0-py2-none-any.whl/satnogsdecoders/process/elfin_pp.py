"""
Preprocessor used in kaitai struct to remove the escape sequences of
an ELFIN STAR telemetry frame
"""
#
# Patrick Dohmen, DL4PD (dl4pd@darc.de)
# With the kind help of Mikhail Yakshin
#
# Usage in 'kaitai struct':
#
# types:
#   preprocessor:
#     seq:
#       - id: databuf
#         process: elfin_pp
#         size-eos: true
#
from __future__ import absolute_import, division, print_function


class ElfinPp(object):  # pylint: disable=too-few-public-methods
    """
    ELFIN preprocessor class
    """

    def __init__(self):
        pass

    def decode(self, in_bindata):  # pylint: disable=no-self-use
        """
        ELFIN preprocessor decoding method
        """
        bindata = bytearray(in_bindata)
        i = 0
        binlen = len(bindata)
        out = bytearray(b'')
        while i < binlen:
            char = bindata[i]
            if char == 0x27 and i + 1 < binlen:
                next_char = bindata[i + 1]
                if next_char in [0x27, 0x5e, 0x93]:
                    i += 1
            out.append(bindata[i])
            i += 1
        return out
