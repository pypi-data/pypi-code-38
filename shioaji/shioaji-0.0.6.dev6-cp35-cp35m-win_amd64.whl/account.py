from shioaji.base import BaseObj, attrs

__all__ = ('Account StockAccount FutureAccount').split()


@attrs
class Account(BaseObj):
    _defaults = dict(
        account_type='',
        person_id='',
        broker_id='',
        account_id='',
        username='',
    )

    def astype(self):
        return _ACCTTYPE.get(self.account_type, self.__class__)(**self)


class StockAccount(Account):
    _force_def = dict(account_type='S')


class FutureAccount(Account):
    _force_def = dict(account_type='F')


_ACCTTYPE = {'S': StockAccount, 'F': FutureAccount}