"""Google Cloud DNS API."""

from bits.google.services.base import Base
from googleapiclient.discovery import build


class CloudDNS(Base):
    """CloudDNS class."""

    def __init__(self, credentials):
        """Initialize a class instance."""
        self.dns = build('dns', 'v1', credentials=credentials)

    def get_managed_zones(self, project):
        """Return list of DNS managed zones."""
        managedZones = self.dns.managedZones()
        request = managedZones.list(project=project)
        return self.get_list_items(managedZones, request, 'managedZones')

    def get_resource_records(self, project, zone):
        """Return a list of resource records for a specific project/zone."""
        resourceRecordSets = self.dns.resourceRecordSets()
        request = resourceRecordSets.list(project=project, managedZone=zone)
        return self.get_list_items(resourceRecordSets, request, 'rrsets')
