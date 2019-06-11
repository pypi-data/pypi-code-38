"""SpecialEventsPolicy class"""


from .halo_endpoint import HaloEndpoint


class SpecialEventsPolicy(HaloEndpoint):
    """Initializing the SpecialEventsPolicy class:

    Args:
        session (:class:`cloudpassage.HaloSession`): This will define how you
            interact with the Halo API, including proxy settings and API keys
            used for authentication.

    Keyword args:
        endpoint_version (int): Endpoint version override.
    """

    object_name = "special_events_policy"
    objects_name = "special_events_policies"
    default_endpoint_version = 1

    def endpoint(self):
        """Return endpoint for API requests."""
        return "/v{}/{}".format(self.endpoint_version, self.objects_name)

    @classmethod
    def pagination_key(cls):
        """Return the pagination key for parsing paged results"""
        return cls.objects_name

    @classmethod
    def object_key(cls):
        """Defines the key used to pull the object from the json document"""
        return cls.object_name

    def create(self, unimportant):
        """Not implemented for this module.  Raises exception."""
        raise NotImplementedError

    def delete(self, unimportant):
        """Not implemented for this module.  Raises exception."""
        raise NotImplementedError

    def update(self, unimportant):
        """Not implemented for this module.  Raises exception."""
        raise NotImplementedError
