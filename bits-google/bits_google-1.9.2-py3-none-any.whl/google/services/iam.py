"""Google Identity and Access Management API."""

from bits.google.services.base import Base
from googleapiclient.discovery import build


class IAM(Base):
    """IAM class."""

    def __init__(self, credentials):
        """Initialize a class instance."""
        self.iam = build('iam', 'v1', credentials=credentials)

    def get_service_accounts(self, project):
        """Return list of project service accounts."""
        params = {
            'name': 'projects/%s' % (project)
        }
        accounts = self.iam.projects().serviceAccounts()
        request = accounts.list(**params)
        return self.get_list_items(accounts, request, 'accounts')

    def get_service_accounts_dict(self, project):
        """Return a dict of domain service_accounts."""
        google_service_accounts = self.get_service_accounts(
            project
        )
        service_accounts = {}
        for a in google_service_accounts:
            key = a['email']
            service_accounts[key] = a
        return service_accounts
