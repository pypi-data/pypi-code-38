# TODO: handle file mode?

import io

from ..interface import Contract, ContractNotRespected
from ..syntax import (add_contract, add_keyword, Keyword, W)

file_type = io.IOBase


class File(Contract):
    def __init__(self, where=None):
        Contract.__init__(self, where)

    def check_contract(self, context, value, silent):

        if not isinstance(value, file_type):
            error = 'Expected a file, got %r.' % value.__class__.__name__
            raise ContractNotRespected(contract=self, error=error,
                                       value=value, context=context)

    def __str__(self):
        return 'file'

    def __repr__(self):
        return 'File()'

    @staticmethod
    def parse_action(s, loc, _):
        where = W(s, loc)
        return File(where=where)


file_contract = Keyword('file')

file_contract.setParseAction(File.parse_action)

add_contract(file_contract)
add_keyword('file')
