import sys

if sys.version_info >= (3, 0):
    text_type = str
    binary_type = bytes
else:
    text_type = unicode
    binary_type = str

string_types = (text_type, binary_type)
