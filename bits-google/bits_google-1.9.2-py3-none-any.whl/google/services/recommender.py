"""Recommender API class file."""

from bits.google.services.base import Base
from google.auth.transport.requests import AuthorizedSession


class Recommender(Base):
    """Recommender class."""

    def __init__(self, credentials):
        """Initialize a class instance."""
        self.api_version = 'v1alpha1'
        self.base_url = 'https://recommender.googleapis.com/%s' % (
            self.api_version,
        )
        self.credentials = credentials
        self.requests = AuthorizedSession(self.credentials)

    def get_instance_machine_type_recommendations(self, resource, zone):
        """Return VM rightsizing recommendations for a resource."""
        recommender = 'google.compute.instance.MachineTypeRecommender'
        url = '%s/%s/locations/%s/recommenders/%s/recommendations' % (
            self.base_url,
            resource,
            zone,
            recommender,
        )
        return self.requests.get(url).json().get('recommendations', [])

    def get_instance_group_machine_type_recommendations(self, resource, zone):
        """Return VM rightsizing recommendations for a resource."""
        recommender = 'google.compute.instanceGroupManager.MachineTypeRecommender'
        url = '%s/%s/locations/%s/recommenders/%s/recommendations' % (
            self.base_url,
            resource,
            zone,
            recommender,
        )
        return self.requests.get(url).json().get('recommendations', [])

    def get_role_recommendations(self, resource):
        """Return role recommendations for a resource."""
        recommender = 'google.iam.policy.RoleRecommender'
        url = '%s/%s/locations/global/recommenders/%s/recommendations' % (
            self.base_url,
            resource,
            recommender,
        )
        return self.requests.get(url).json().get('recommendations', [])
