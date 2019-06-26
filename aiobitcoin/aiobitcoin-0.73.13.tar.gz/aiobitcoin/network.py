# -*- coding: utf-8 -*-
from .grambitcoincommon import GramBitcoinCommon
from .bitcoinerrors import *


class Network(GramBitcoinCommon):
    """
    Methods from `Network` section https://bitcoincore.org/en/doc/0.17.0/.

    :param str url (optional):          Node URI in format http://alice:bob@127.0.0.1:18332
    :param object gram (optional):      GramBitcoin object
    :param int read_timeout (20):       Request operations timeout

    Note: You must pass at least one parameter or `url` or `gram` (with active session).
    """

    def __init__(self, url=None, gram=None, read_timeout=20):
        super().__init__(url=url, gram=gram, read_timeout=read_timeout)

    async def clear_banned(self) -> None:
        """
        Clear all banned IPs.
        :return: None
        """
        await self.call_method('clearbanned')

    async def get_network_info(self) -> dict:
        """
        :return: Returns an object containing various state info regarding P2P networking.
        """
        return (
            await self.call_method('getnetworkinfo')
        )['result']

    async def get_peer_info(self, to_list: bool = True) -> list or not list:
        """
        :param to_list: will return list or genexpr
        :return: Returns data about each connected network node as a json array of objects.
        """
        peers_info = (
            await self.call_method('getpeerinfo')
        )['result']

        return peers_info if to_list else (peer_info for peer_info in peers_info)

    async def list_banned(self, to_list: bool = True) -> list or not list:
        """
        :param to_list:
        :return: List all banned IPs/Subnets.
        """
        banned_lst = (
            await self.call_method('listbanned')
        )['result']

        return banned_lst if to_list else (el for el in banned_lst)

    async def ping(self) -> None:
        """
        Requests that a ping be sent to all other nodes, to measure ping time.
        Results provided in getpeerinfo, pingtime and pingwait fields are decimal seconds.
        Ping command is handled in queue with all other commands, so it measures processing backlog, not just
        network ping.
        :return: None
        """
        await self.call_method('ping')

    async def set_ban(self, subnet: str, command: str = 'add',
                      bantime: int = 0, absolute: bool = False) -> None or InvalidIpOrSubnet:
        """
        Attempts to add or remove an IP/Subnet from the banned list.
        :param subnet: The IP/Subnet (see getpeerinfo for nodes IP) with an optional netmask
        (default is /32 = single IP)
        :param command: 'add' to add an IP/Subnet to the list, 'remove' to remove an IP/Subnet from the list
        :param bantime: Time in seconds how long (or until when if [absolute] is set) the IP is banned
        (0 or empty means using the default time of 24h which can also be overwritten by the -bantime startup argument)
        :param absolute: If set, the bantime must be an absolute timestamp in seconds since epoch (Jan 1 1970 GMT)
        :return: None
        """
        error = (
            await self.call_method('setban', subnet, command, bantime, absolute)
        )['error']

        if error and error['code'] == -30:
            raise InvalidIpOrSubnet
