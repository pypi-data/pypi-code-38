import logging

logger = logging.getLogger(__name__)  # Initialize logger


class BalanceClient(object):
    def __init__(self, client):
        self.__client = client

    async def get_nct_balance(self, chain, api_key=None):
        """Get nectar balance from polyswarmd

        Args:
            chain (str): Which chain to operate on
            api_key (str): Override default API key
        Returns:
            Response JSON parsed from polyswarmd containing nectar balance
        """
        path = '/balances/{0}/nct'.format(self.__client.account)
        success, balance = await self.__client.make_request('GET', path, chain, api_key=api_key)
        if not success:
            logger.warning('Unable to get nectar balance for %s', self.__client.account)
            return 0

        return int(balance)

    async def get_eth_balance(self, chain, api_key=None):
        """Get eth balance from polyswarmd

        Args:
            chain (str): Which chain to operate on
            api_key (str): Override default API key
        Returns:
            Response JSON parsed from polyswarmd containing eth balance
        """
        path = '/balances/{0}/eth'.format(self.__client.account)
        success, balance = await self.__client.make_request('GET', path, chain, api_key=api_key)
        if not success:
            logger.warning('Unable to get eth balance for %s', self.__client.account)
            return 0

        return int(balance)
