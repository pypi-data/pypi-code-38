# -*- coding: utf-8 -*-
from .grambitcoincommon import GramBitcoinCommon
from aiobitcoin import bitcointools
from .blockchain import Blockchain
from .bitcoinerrors import *


class Wallet(GramBitcoinCommon):
    """
    Methods from `Wallet` section https://bitcoincore.org/en/doc/0.17.0/.

    :param str url (optional):          Node URI in format http://alice:bob@127.0.0.1:18332
    :param object gram (optional):      GramBitcoin object
    :param int read_timeout (20):       Request operations timeout

    Note: You must pass at least one parameter or `url` or `gram` (with active session).
    """

    def __init__(self, url=None, gram=None, read_timeout=20):
        super().__init__(url=url, gram=gram, read_timeout=read_timeout)

    async def import_address(self, addr: str, rescan: bool = False) -> None or PrivateKeyForThisAddressAlreadyInWallet:
        """
        Adds an address or script (in hex) that can be watched as if it were in your wallet but cannot be used to spend.
        :param addr: bitcoin address
        :param rescan: activate rescanning blockchain after importing
        :return: boolean value
        """
        error = (
            await self.call_method('importaddress', addr, '', rescan)
        )['error']

        if error is not None and error['code'] == -4:
            raise PrivateKeyForThisAddressAlreadyInWallet

    async def import_priv_key(self, wif: str) -> None or InvalidPrivateKeyEncoding:
        """
        Adds a private key (as returned by dumpprivkey) to your wallet.
        :param wif: bitcoin private key
        :return: boolean value
        """
        error = (
            await self.call_method('importprivkey', wif, "", False)
        )['error']

        if error is not None and error['code'] == -5:
            raise InvalidPrivateKeyEncoding

    async def get_balance(self) -> float:
        """
        Returns the total available balance.
        :return: total balance
        """
        return (
            await self.call_method('getbalance')
        )['result']

    async def list_transactions(self,
                                count: int = 100,
                                include_watchonly: bool = True,
                                to_list: bool = True) -> list or not list:
        """
        Returns up to 'count' most recent transactions.
        :param count: The number of transactions to return
        :param include_watchonly: Include transactions to watch-only addresses
        :param to_list: will return list or genexpr
        :return: list of transactions
        """
        list_txs = (
            await self.call_method('listtransactions', '*', count, 0, include_watchonly)
        )['result']

        if to_list:
            return list_txs

        return (tx for tx in list_txs)

    async def rescan_blockchain(self, days_ago: int, full_rescan: bool = False) -> bool:
        """
        Rescan the local blockchain for wallet related transactions.
        :param days_ago: how many days the blockchain rescanning will pass
        :param full_rescan: blockchain rescanning will start from block 1
        :return: boolean value
        """
        blocks_ago = await bitcointools.calc_blocks_by_days(days_ago)

        async with Blockchain(url=self.url, read_timeout=self.read_timeout) as blockchain:
            total_blocks = (
                await blockchain.get_blockchain_info()
            )['blocks']

        block_height = 1 if full_rescan else total_blocks - blocks_ago
        error = (
            await self.call_method('rescanblockchain', block_height)
        )['error']

        return True if not error else False

    async def send_to_address(self, addr: str, amount: int or float) -> None or InvalidAddress:
        """
        Send an amount to a given address.
        :param addr: Bitcoin address
        :param amount: amount to send
        :return: tx hash
        """
        error = (
            await self.call_method('sendtoaddress', addr, amount)
        )['error']

        if error is not None and error['code'] == -5:
            raise InvalidAddress
