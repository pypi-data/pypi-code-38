import asyncio
from typing import List

import aioxmpp
from aioxmpp import PresenceManagedClient, JID
from aioxmpp.security_layer import SecurityLayer

from serverchecks.alerts import AbstractAlert


class XmppAlert(AbstractAlert):
    """
    XMPP alert class using aioxmpp client library
    https://docs.zombofant.net/aioxmpp/devel/api/public/node.html
    """
    name = 'XMPP'

    def __init__(self, **kwargs):
        self.sender: JID = JID.fromstr(kwargs['sender'])
        self.password: SecurityLayer = aioxmpp.make_security_layer(kwargs['password'])
        self.recipients: List[JID] = [JID.fromstr(r) for r in kwargs['recipients']]

        if not len(self.recipients) > 0:
            raise ValueError(f'{self.name} requires `recipients` to be a list with at least one recipient JID')

        self.client: PresenceManagedClient = PresenceManagedClient(self.sender, self.password)

    async def open(self) -> None:
        self.client.start()

    async def alert(self, message: str):
        tasks = []
        for recipient in self.recipients:
            msg = aioxmpp.Message(to=recipient, type_=aioxmpp.MessageType.CHAT)
            msg.body[None] = message
            tasks.append(self.client.send(msg))

        await asyncio.gather(*tasks)

    async def close(self):
        self.client.stop()

    def __str__(self):
        return f'<{self.name}: {self.sender}, {len(self.recipients)} recipients>'


alert_class = XmppAlert
