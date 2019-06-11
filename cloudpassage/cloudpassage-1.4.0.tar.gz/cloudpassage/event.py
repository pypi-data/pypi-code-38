"""Event class"""


from .utility import Utility as utility
from .http_helper import HttpHelper
from .halo_endpoint import HaloEndpoint
from .time_series import TimeSeries


class Event(HaloEndpoint):
    """Event class:

    Args:
        session (:class:`cloudpassage.HaloSession`): This will define how you
            interact with the Halo API, including proxy settings and API keys
            used for authentication.

    """

    # pylint: disable=too-few-public-methods
    # This cannot be combined with any other module, and still make sense
    object_name = "event"
    objects_name = "events"
    default_endpoint_version = 1

    def endpoint(self):
        """Return endpoint for API requests."""
        return "/v{}/{}".format(self.endpoint_version, self.objects_name)

    def list_all(self, pages, **kwargs):
        """Return a list of all events.


        Default filter returns ALL events.  This is a very verbose and
        time-consuming operation.

        Filtering is done with keyword arguments, some of which are listed
        below. An exhaustive list of filters can be found at
        https://api-doc.cloudpassage.com/help#events

        Args:
            pages (int): Max number of pages (of ten items each) to retrieve

        Keyword Args:
            group_id (list or str): A list or comma-separated string containing
                the group IDs to retrieve events for.
            server_id (list or str): A list or comma-separated string
                containing the server IDs to retrieve events for.
            server_platform (str): (linux | windows)
            critical (bool): Returns only critical or noncritical events.
            type (list or str): A list or comma-separated string containing the
                event types to query for.  A complete list of event types is
                available here:
                https://api-doc.cloudpassage.com/help#event-types
            since (str): ISO 8601 formatted string representing the starting
                date and time for query
            until (str): ISO 8601 formatted string representing the ending
                date and time for query

        Returns:
            list: List of dictionary objects describing servers

        """

        endpoint = self.endpoint()
        max_pages = pages
        request = HttpHelper(self.session)
        params = utility.sanitize_url_params(kwargs)
        response = request.get_paginated(endpoint, self.objects_name,
                                         max_pages, params=params)
        return response

    def stream(self, start_time, **kwargs):
        """Yield events beginning at ``start_time``.

        This generator supports the same keyword arguments as
        :func:`~cloudpasssage.Event.list_all`
        """
        params = utility.sanitize_url_params(kwargs)
        start_url = self.endpoint()
        streamer = TimeSeries(self.session, start_time, start_url,
                              self.objects_name, params=params)
        for event in streamer:
            yield event

    def create(self):
        """Not implemented for this object."""
        raise NotImplementedError

    def delete(self):
        """Not implemented for this object."""
        raise NotImplementedError

    def update(self):
        """Not implemented for this object."""
        raise NotImplementedError
