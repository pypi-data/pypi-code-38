"""Google ResourceSearch API."""

from bits.google.services.base import Base
from googleapiclient.discovery import build


class ResourceSearch(object):
    """ResourceSearch class."""

    def __init__(self, credentials):
        """Initialize a class instance."""
        self.crs = build('cloudresourcesearch', 'v1', credentials=credentials)

    def search(self, query, orderBy=None, pageSize=None, pageToken=None):
        """Return results from a cloud research search."""
        params = {
            'query': query,
            'orderBy': orderBy,
            'pageSize': pageSize,
            'pageToken': pageToken,
        }
        response = self.crs.resources().search(**params).execute()
        pageToken = response.get('nextPageToken')
        results = response.get('results', [])

        while pageToken:
            params['pageToken'] = pageToken
            response = self.crs.resources().search(**params).execute()
            pageToken = response.get('nextPageToken')
            results.extend(response.get('results', []))

        return results
