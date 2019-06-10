from .request import request

__all__ = ['Finance', ]


class Finance:
    def __init__(self, config):
        """
        :param config: PRSConfig
        """
        self.config = config

    def get_wallet(self):
        return request(
            self.config.host,
            method='GET',
            path='/finance/wallet',
            auth_opts=self.config.get_auth_opts(),
            debug=self.config.debug,
        )

    def get_transactions(self, offset=0, limit=10):
        """
        :param offset: int
        :param limit: int
        """
        query = {
            'offset': offset,
            'limit': limit,
        }
        return request(
            self.config.host,
            method='GET',
            path='/finance/transactions',
            query=query,
            auth_opts=self.config.get_auth_opts(),
            debug=self.config.debug,
        )

    def withdraw(self, amount):
        """
        :param amount: int
        """
        data = {'amount': amount}
        return request(
            self.config.host,
            method='POST',
            path='finance/withdraw',
            data=data,
            auth_opts=self.config.get_auth_opts(),
            debug=self.config.debug,
        )

    def recharge(self, amount):
        """
        :param amount: int
        """
        data = {'amount': amount}
        return request(
            self.config.host,
            method='POST',
            path='finance/recharge',
            data=data,
            auth_opts=self.config.get_auth_opts(),
            debug=self.config.debug,
        )
