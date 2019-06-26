from fedora_messaging import message


class BaseMessage(message.Message):

    def __str__(self):
        return "{sender} sent a happiness packet to {recipient}".format(
            sender=self.sender,
            recipient=self.recipient
        )

    @property
    def summary(self):
        if self.sender != "Anonymous":
            return "{sender}, {recipient}".format(
                sender=self.sender,
                recipient=self.recipient
            )
        else:
            return self.recipient

    @property
    def sender(self):
        return 'Message did not implement "sender" property'

    @property
    def recipient(self):
        return 'Message did not implement "recipient" property'

    @property
    def app_icon(self):
        return "https://pagure.io/fedora-commops/fedora-happiness-packets/blob/master/f/assets/images/logo.png"

    @property
    def usernames(self):
        """List of users affected by the action that generated this message."""
        if self.sender != "Anonymous":
            return [self.sender, self.recipient]
        else:
            return [self.recipient,]


class MessageV1(BaseMessage):

    body_schema = {
        "id": "https://fedoraproject.org/message-schema/happiness_packet",
        "$schema": "http://json-schema.org/draft-04/schema#",
        "description": "Schema for happinesspacket sent",
        "type": "object",
        "properties": {
            "id":{"type": "string"},
            "sender": {"type": "string"},
            "recipient": {"type": "string"}
        },
        "required": ["id", "sender", "recipient"]
    }

    @property
    def sender(self):
        """The sender's name"""
        return self.body["sender"]

    @property
    def recipient(self):
        """The recipient's name"""
        return self.body["recipient"]

