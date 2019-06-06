import asyncio
from typing import Optional, List

from telethon import TelegramClient
from telethon.tl.types import User

from serverchecks.alerts import AbstractAlert


class TelegramAlert(AbstractAlert):
    """
    Telegram alert class using Telethon pure-Python MTProto client library


    """
    name = 'Telegram'

    def __init__(self, **kwargs) -> None:
        self.bot_token: str = kwargs.get('bot_token')
        self.api_id: int = int(kwargs.get('api_id'))
        self.api_hash: str = kwargs.get('api_hash')
        self.app_name: str = kwargs.get('app_name')
        self.recipients: List[str] = kwargs.get('recipients')
        self.client: Optional[TelegramClient] = None

    async def open(self) -> None:
        self.client = await TelegramClient(self.app_name, self.api_id, self.api_hash).start(bot_token=self.bot_token)

    async def test(self) -> bool:
        return type(await self.client.get_entity('me')) is User

    async def alert(self, message: str) -> None:
        await asyncio.gather(*[self.client.send_message(recipient, message) for recipient in self.recipients])

    async def close(self) -> None:
        await self.client.disconnect()

    def __str__(self):
        return f'<{self.name}: @{self.app_name}, {len(self.recipients)} recipients>'


alert_class = TelegramAlert
