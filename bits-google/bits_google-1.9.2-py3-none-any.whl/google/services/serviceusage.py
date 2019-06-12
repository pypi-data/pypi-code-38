"""Service Usage API class file."""

from bits.google.services.base import Base
from google.auth.transport.requests import AuthorizedSession
# from googleapiclient.discovery import build


class ServiceUsage(Base):
    """ServiceUsage API class."""

    def __init__(self, credentials):
        """Initialize a class instance."""
        self.credentials = credentials

        # settings for requests
        self.alpha_base_url = 'https://serviceusage.googleapis.com/v1alpha'
        self.base_url = 'https://serviceusage.googleapis.com/v1'
        self.headers = {
            'Content-Type': 'application/json',
        }
        self.requests = AuthorizedSession(credentials)

    def get_list(self, url, collection, params={}):
        """Return a list of items from a paginated GET request."""
        params['pageToken'] = None
        response = self.requests.get(url, headers=self.headers).json()
        items = response.get(collection, [])
        pageToken = response.get('nextPageToken')
        while pageToken:
            params['pageToken'] = pageToken
            response = self.requests.get(url, headers=self.headers, params=params).json()
            items.extend(response.get(collection, []))
            pageToken = response.get('nextPageToken')
        return items

    def get_project_services(self, project):
        """Return a list of services enabled in the project."""
        url = '%s/projects/%s/services?filter=state:ENABLED' % (
            self.base_url,
            project,
        )
        return self.get_list(url, 'services')

    def get_folder_service_quotas(self, folder, service):
        """Return a list of quotas for a service in a folder."""
        resource = 'folders/%s' % (folder)
        return self.get_resource_service_quotas(resource, service)

    def get_organization_service_quotas(self, organization, service):
        """Return a list of quotas for a service in an organization."""
        resource = 'organizations/%s' % (organization)
        return self.get_resource_service_quotas(resource, service)

    def get_project_service_quotas(self, project, service):
        """Return a list of quotas for a service in a project."""
        resource = 'projects/%s' % (project)
        return self.get_resource_service_quotas(resource, service)

    def get_operation(self, name):
        """Return an operation by name."""
        url = '%s/%s' % (self.alpha_base_url, name)
        return self.requests.get(url, headers=self.headers).json()

    def get_resource_service_quotas(self, resource, service):
        """Return a list of quotas for a resource."""
        url = '%s/%s/services/%s/quotaMetrics' % (
            self.alpha_base_url,
            resource,
            service,
        )
        return self.get_list(url, 'metrics')

    def set_admin_override(self, resource, value=None, force=False, location=None):
        """Set an admin override on a resource."""
        url = '%s/%s:setAdminOverride' % (
            self.alpha_base_url,
            resource,
        )
        body = {
            'force': force,
            'location': location,
            'override_value': value,
        }
        return self.requests.post(url, headers=self.headers, json=body).json()

    def set_consumer_override(self, resource, value=None, force=False, location=None):
        """Set a consumer override on a resource."""
        url = '%s/%s:setConsumerOverride' % (
            self.alpha_base_url,
            resource,
        )
        body = {
            'force': force,
            'location': location,
            'override_value': value,
        }
        return self.requests.post(url, headers=self.headers, json=body).json()
