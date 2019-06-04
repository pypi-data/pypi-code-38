import aioxmpp
from aioxmpp import PresenceManagedClient

from serverchecks.alerts import AbstractAlert


class XmppAlert(AbstractAlert):
    """
    XMPP alert class using aioxmpp client library
    https://docs.zombofant.net/aioxmpp/devel/api/public/node.html
    """
    name = 'XMPP'

    def __init__(self, **kwargs):
        self.sender = aioxmpp.JID.fromstr(kwargs['sender'])
        self.recipient = aioxmpp.JID.fromstr(kwargs['recipient'])
        self.password = aioxmpp.make_security_layer(kwargs['password'])
        self.client: PresenceManagedClient = PresenceManagedClient(self.sender, self.password)

    async def open(self) -> None:
        self.client.start()

    async def alert(self, message: str):
        msg = aioxmpp.Message(to=self.recipient, type_=aioxmpp.MessageType.CHAT)
        msg.body[None] = message
        await self.client.send(msg)

    async def close(self):
        self.client.stop()

    def __str__(self):
        return f'<{self.name}: From={self.sender} To={self.recipient}>'


alert_class = XmppAlert
