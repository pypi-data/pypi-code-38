"""Google Identity and Access Management API."""

from bits.google.services.base import Base
from googleapiclient.discovery import build


class IAMCredentials(Base):
    """IAM class."""

    def __init__(self, credentials):
        """Initialize a class instance."""
        self.iamcredentials = build('iamcredentials', 'v1', credentials=credentials)

    def generate_access_token(self, serviceAccount, lifetime='3600s', delegates=[], scope=[]):
        """Return a Google Access Token."""
        # generate service account name
        name = 'projects/-/serviceAccounts/%s' % (serviceAccount)

        # generate delegate names
        delegate_names = []
        for delegate in delegates:
            delegate_names.append('projects/-/serviceAccounts/%s' % (delegate))

        # create body
        body = {
            'lifetime': lifetime,
            'delegates': delegate_names,
            'scope': scope,
        }

        # generate access token
        response = self.iamcredentials.projects().serviceAccounts().generateAccessToken(
            name=name,
            body=body,
        ).execute()

        return response.get('accessToken')

    def generate_id_token(self, serviceAccount, audience, delegates=[], include_email=False):
        """Return a Google Access Token."""
        # generate service account name
        name = 'projects/-/serviceAccounts/%s' % (serviceAccount)

        # generate delegate names
        delegate_names = []
        for delegate in delegates:
            delegate_names.append('projects/-/serviceAccounts/%s' % (delegate))

        # create body
        body = {
            'audience': audience,
            'delegates': delegate_names,
            'include_email': include_email,
        }

        # generate id token
        response = self.iamcredentials.projects().serviceAccounts().generateIdToken(
            name=name,
            body=body,
        ).execute()

        return response.get('token')
