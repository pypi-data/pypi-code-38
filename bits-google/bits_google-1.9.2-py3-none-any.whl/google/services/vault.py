"""Google Vault API."""

from bits.google.services.base import Base
from googleapiclient.discovery import build


class Vault(Base):
    """Google Vault class."""

    def __init__(self, credentials):
        """Initialize a class instance."""
        self.vault = build('vault', 'v1', credentials=credentials)

    def add_held_accounts(self, matterId, holdId, body):
        """Return a list of matters."""
        return self.vault.matters().holds().addHeldAccounts(
            matterId=matterId,
            holdId=holdId,
            body=body,
        ).execute()

    def get_holds(self, matterId):
        """Return a list of matters."""
        holds = self.vault.matters().holds()
        request = holds.list(matterId=matterId)
        return self.get_list_items(holds, request, 'holds')

    def get_matters(self):
        """Return a list of matters."""
        matters = self.vault.matters()
        request = matters.list()
        return self.get_list_items(matters, request, 'matters')
