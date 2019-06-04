__author__ = 'UShareSoft'

from texttable import Texttable

def init_texttable(headers, width=200, align=None, types=None):
    table = Texttable(width)

    if headers is not None:
        table.header(headers)

    if align is not None:
        table.set_cols_align(align)

    if types is not None:
        table.set_cols_dtype(types)

    return table