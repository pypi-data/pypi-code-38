#!/usr/bin/env python
def xorCryptPy(str, key):
    """Encrypt or decrypt a string with the given XOR key."""
    try:
        key
    except NameError:
        key = 6
    output = ""
    for x in range(0, len(str)):
        output += chr(key ^ ord(str[x]))
    return output
