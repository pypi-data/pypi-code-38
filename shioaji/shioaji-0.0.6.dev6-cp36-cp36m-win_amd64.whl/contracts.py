from shioaji.base import BaseObj, attrs
from shioaji.backend.constant import SecurityType

__all__ = ('Contract Stock Option').split()


@attrs
class Contract(BaseObj):
    """ the base contract object

    Attributes:
        symbol (str):
        security_type (str): {STK, FUT, OPT}
        currency (str):
        exchange (str):
        code (str):
        name (str):
        category (str):
        delivery_month (str)
        strike_price (int or float):
        option_right (str): {C, P}
        underlying_kind (str):
        underlying_code (str)
        unit (int or float):
        multiplier (int):
    """
    _defaults = dict(
        symbol='',
        security_type='',
        currency='TWD',
        exchange='TAIFEX',
        code='',
        name='',
        category='',
        delivery_month='',
        strike_price=0,  # option strike_price
        option_right='',  # option call put
        underlying_kind='',
        underlying_code='',
        unit=0,
        multiplier=0,
    )

    def __init__(self, *args, **kwargs):
        BaseObj.__init__(self, *args, **kwargs)

    def astype(self):
        return _CONTRACTTYPE.get(self.security_type, self.__class__)(**self)

class Index(Contract):
    _force_def = dict(security_type=SecurityType.Index)

class Stock(Contract):
    _force_def = dict(security_type=SecurityType.Stock)


class Future(Contract):
    _force_def = dict(security_type=SecurityType.Future)


class Option(Contract):
    _force_def = dict(security_type=SecurityType.Option)


_CONTRACTTYPE = {
    SecurityType.Index: Index,
    SecurityType.Stock: Stock,
    SecurityType.Future: Future,
    SecurityType.Option: Option,
}


@attrs
class Contracts(BaseObj):
    _defaults = dict(Indexs=None, Stocks=None, Futures=None, Options=None)

    def __init__(self, *args, **kwargs):
        BaseObj.__init__(self, *args, **kwargs)
        self._Indexs = IndexContracts(self.Indexs)
        self._Stocks = StockContracts(self.Stocks)
        self._Futures = FutureContracts(self.Futures)
        self._Options = OptionContracts(self.Options)

    def __iter__(self):
        for prop in self.__slots__:
            if getattr(self, prop[1:]):
                yield getattr(self, prop[1:])


class BaseIterContracts:

    def __iter__(self):
        for key in self.__slots__:
            if not key.startswith('_'):
                yield getattr(self, key)

    def __bool__(self):
        return True if list(self.keys()) else False

    def keys(self):
        return (key for key in self.__slots__ if not key.startswith('_'))

    def __getitem__(self, key):
        return getattr(self, key)

    def get(self, key, default=None):
        return getattr(self, key, default)


class ProductContracts(BaseIterContracts):

    def __init__(self, contracts_dict):
        self._code2contract = {}
        if contracts_dict:
            self.__slots__ = [(
                key,
                setattr(self, key, MultiContract(key, value)),
                self._code2contract.update(getattr(self, key)._code2contract),
            )[0] for key, value in contracts_dict.items()] + ['_code2contract']
        else:
            self.__slots__ = ('_code2contract',)

    def __repr__(self):
        return '({})'.format(', '.join(self.__slots__[:-1]))

    def __getitem__(self, key):
        return getattr(self, key, self._code2contract.get(key, None))

    def get(self, key, default=None):
        return getattr(self, key, self._code2contract.get(key, default))

class IndexContracts(ProductContracts):
    pass

class StockContracts(ProductContracts):
    pass


class FutureContracts(ProductContracts):
    pass


class OptionContracts(ProductContracts):
    pass


class MultiContract(BaseIterContracts):

    def __init__(self, name, contracts):
        self._name = name
        self._code2contract = {}
        self.__slots__ = [(
            cont['symbol'],
            setattr(self, cont['symbol'],
                    Contract(**cont).astype()),
            self._code2contract.update({
                cont['code']: getattr(self, cont['symbol'])
            }),
        )[0] for cont in contracts] + ['_name'] + ['_code2contract']

    def __getitem__(self, key):
        return getattr(self, key, self._code2contract.get(key, None))

    def get(self, key, default=None):
        return getattr(self, key, self._code2contract.get(key, default))

    def __repr__(self):
        return "{}({})".format(self._name, (', ').join(self.__slots__[:-2]))
