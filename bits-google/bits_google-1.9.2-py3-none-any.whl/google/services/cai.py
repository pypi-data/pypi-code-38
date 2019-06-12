"""Google Cloud Asset Inventory API."""

from bits.google.services.base import Base
from googleapiclient.discovery import build
from google.auth.transport.requests import AuthorizedSession


class CloudAssetInventory(Base):
    """CloudAssetInventory class."""

    def __init__(self, credentials):
        """Initialize a class instance."""
        self.asset = build('cloudasset', 'v1', credentials=credentials)
        self.credentials = credentials

    def export_asset_inventory(self, resource, gcs_uri):
        """Export new asset inventory."""
        # projects = asset.project()
        # return projects.export().execute()

        requests = AuthorizedSession(self.credentials)
        url = 'https://cloudasset.googleapis.com/v1alpha1/%s:export' % (
            resource
        )
        headers = {}
        body = {
            'outputConfig': {
                'gcsDestination': {
                    'uri': gcs_uri
                }
            }
        }
        response = requests.post(
            url,
            headers=headers,
            json=body,
        )
        return response.json()

    def get_operation(self, resource, operation_id):
        """Get the status of an asset inventory export operation."""
        # operations = self.asset.projects().operations()
        # return operations.get().execute()

        requests = AuthorizedSession(self.credentials)
        url = 'https://cloudasset.googleapis.com/v1alpha1/%s/operations/ExportAssets/%s' % (
            resource,
            operation_id,
        )
        headers = {}
        response = requests.get(
            url,
            headers=headers,
        )
        return response.json()
