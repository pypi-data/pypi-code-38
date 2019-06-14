# -*- coding: utf-8 -*-
from .grambitcoincommon import GramBitcoinCommon
from .bitcoinerrors import BitcoinErrors


class Blockchain(GramBitcoinCommon):
    def __init__(self, url=None, gram=None, read_timeout=20):
        super().__init__(url=url, gram=gram, read_timeout=read_timeout)

    @staticmethod
    async def _check_error(error):
        if error:
            raise BitcoinErrors(error)

    async def get_blockchain_info(self) -> dict:
        """
        Provides information about the current state of the block chain.
        :return: full blockchain information.
        """
        return (
            await self.call_method('getblockchaininfo')
        )['result']

    async def get_block_count(self) -> int:
        """
        :return: Returns the number of blocks in the longest blockchain.
        """
        response = await self.call_method('getblockcount')
        await self._check_error(response['error'])

        return response['result']

    async def get_difficulty(self):
        """
        :return: Returns the proof-of-work difficulty as a multiple of the minimum difficulty.
        """
        return (
            await self.call_method('getdifficulty')
        )['result']

    async def get_mempool_info(self):
        """
        :return: Returns details on the active state of the TX memory pool.
        """
        return (
            await self.call_method('getmempoolinfo')
        )['result']
