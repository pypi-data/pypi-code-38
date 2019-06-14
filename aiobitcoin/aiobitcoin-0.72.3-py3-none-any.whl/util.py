# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
from .grambitcoincommon import GramBitcoinCommon


class Util(GramBitcoinCommon):
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
