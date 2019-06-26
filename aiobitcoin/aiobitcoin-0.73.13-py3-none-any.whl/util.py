# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
from .grambitcoincommon import GramBitcoinCommon


class Util(GramBitcoinCommon):
    """
    Methods from `Util` section https://bitcoincore.org/en/doc/0.17.0/.

    :param str url (optional):          Node URI in format http://alice:bob@127.0.0.1:18332
    :param object gram (optional):      GramBitcoin object
    :param int read_timeout (20):       Request operations timeout

    Note: You must pass at least one parameter or `url` or `gram` (with active session).
    """

    def __init__(self, url=None, gram=None, read_timeout=20):
        super().__init__(url=url, gram=gram, read_timeout=read_timeout)

    async def validate_address(self, addr: str) -> bool:
        """
        Return information about the given bitcoin address.
        :param addr: bitcoin address
        :return: boolean value
        """
        return (
            await self.call_method('validateaddress', addr)
        )['result']['isvalid']
