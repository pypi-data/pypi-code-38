
def parse_contract_string_actual(string):
    from .interface import (Contract, ContractDefinitionError, ContractSyntaxError,
        Where)
    from .main import Storage, _cacheable, check_param_is_string
    from .syntax import ParseException, ParseFatalException, contract_expression

    check_param_is_string(string)

    if string in Storage.string2contract:
        return Storage.string2contract[string]
    try:
        c = contract_expression.parseString(string,
                                            parseAll=True)[0]
        assert isinstance(c, Contract), 'Want Contract, not %r' % c
        if _cacheable(string, c):
            Storage.string2contract[string] = c
        return c
    except ContractDefinitionError as e:
        raise
    except ParseException as e:
        where = Where(string, character=e.loc)
        msg = '%s' % e
        raise ContractSyntaxError(msg, where=where)
    except ParseFatalException as e:
        where = Where(string, character=e.loc)
        msg = '%s' % e
        raise ContractSyntaxError(msg, where=where)
