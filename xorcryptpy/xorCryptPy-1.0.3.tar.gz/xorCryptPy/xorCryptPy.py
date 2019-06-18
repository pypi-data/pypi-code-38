#!/usr/bin/env python
def xorCrypt(str, key=6):
    """Encrypt or decrypt a string with the given XOR key."""
    output = ""
    for x in range(0, len(str)):
        output += chr(key ^ ord(str[x]))
    return output
