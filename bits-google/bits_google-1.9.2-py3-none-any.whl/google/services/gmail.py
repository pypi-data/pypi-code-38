"""Google Gmail API."""

from bits.google.services.base import Base
from googleapiclient.discovery import build


class Gmail(Base):
    """Gmail class."""

    def __init__(self, credentials):
        """Initialize a class instance."""
        self.gmail = build('gmail', 'v1', credentials=credentials)

    def add_delegate(self, userId, delegate):
        """Add a delegate for a user."""
        params = {
            'userId': userId,
            'body': {
                'delegateEmail': delegate,
            },
        }
        return self.gmail.users().settings().delegates().create(**params).execute()

    def delete_delegate(self, userId, delegate):
        """Delete a delegate for a user."""
        params = {
            'userId': userId,
            'delegateEmail': delegate,
        }
        return self.gmail.users().settings().delegates().delete(**params).execute()

    def get_delegate(self, userId, delegate):
        """Return a list of delegates for a user."""
        params = {
            'userId': userId,
            'delegateEmail': delegate,
        }
        return self.gmail.users().settings().delegates().get(**params).execute()

    def get_delegates(self, userId):
        """Return a list of delegates for a user."""
        return self.gmail.users().settings().delegates().list(userId=userId).execute().get('delegates', [])

    def get_auto_forwarding_settings(self, userId):
        """Return Gmail auto forwarding settings for a Gmail user."""
        settings = self.gmail.users().settings()
        return settings.getAutoForwarding(userId=userId).execute()

    def update_auto_forwarding_settings(
            self,
            userId,
            forwardingEmail,
            enabled=True,
    ):
        """Update Gmail auto forwarding settings for a Gmail user."""
        body = {
            'enabled': enabled,
        }
        if enabled:
            body['disposition'] = 'leaveInInbox'
            body['emailAddress'] = forwardingEmail
        settings = self.gmail.users().settings()
        return settings.updateAutoForwarding(userId=userId, body=body).execute()

    def create_forwarding_address(self, userId, forwardingEmail):
        """Create a new forwarding address for a Gmail user."""
        body = {'forwardingEmail': forwardingEmail}
        forwardingAddresses = self.gmail.users().settings().forwardingAddresses()
        return forwardingAddresses.create(userId=userId, body=body).execute()

    def list_forwarding_addresses(self, userId):
        """List forwarding addresses for a Gmail user."""
        forwardingAddresses = self.gmail.users().settings().forwardingAddresses()
        return forwardingAddresses.list(userId=userId).execute()
