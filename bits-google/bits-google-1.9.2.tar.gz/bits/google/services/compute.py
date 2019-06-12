"""Google Compute API."""

from bits.google.services.base import Base
from googleapiclient.discovery import build


class Compute(Base):
    """Compute class."""

    def __init__(self, credentials):
        """Initialize a class instance."""
        self.compute = build('compute', 'v1', credentials=credentials)

    def get_instances(self, project, zone):
        """Return a project's instances."""
        params = {
            'project': project,
            'zone': zone,
        }
        instances = self.compute.instances()
        request = instances.list(**params)
        return self.get_list_items(instances, request, 'items')

    def get_project(self, project):
        """Return a project."""
        return self.compute.projects().get(project=project).execute()

    def get_region(self, project, region):
        """Return a project."""
        return self.compute.regions().get(project=project, region=region).execute()

    def get_regions(self, project):
        """Return a project's regions."""
        params = {'project': project}
        regions = self.compute.regions()
        request = regions.list(**params)
        return self.get_list_items(regions, request, 'items')

    def get_zones(self, project):
        """Return a project's zones."""
        params = {'project': project}
        zones = self.compute.zones()
        request = zones.list(**params)
        return self.get_list_items(zones, request, 'items')
