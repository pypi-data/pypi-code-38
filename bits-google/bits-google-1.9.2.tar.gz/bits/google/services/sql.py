"""Google SQL API."""

from bits.google.services.base import Base
from googleapiclient.discovery import build
from google.auth.transport.requests import AuthorizedSession


class SQL(Base):
    """Google SQL class."""

    def __init__(self, credentials):
        """Initialize a class instance."""
        self.credentials = credentials

    def get_instances(self, project):
        """Check if group has member."""
        # token = credentials.get_access_token()[0]
        requests = AuthorizedSession(self.credentials)
        base_url = 'https://www.googleapis.com/sql/v1beta4'
        url = '%s/projects/%s/instances' % (
            base_url,
            project,
        )
        headers = {
            # 'Authorization': 'Bearer %s' % (token),
        }
        params = {}

        response = requests.get(url, headers=headers, params=params)
        items = response.json().get('items', [])

        while response.json().get('nextPageToken'):
            params['pageToken'] = response.json().get('nextPageToken')
            response = requests.get(url, headers=headers, params=params)
            items += response.json().get('items', [])

        return items
