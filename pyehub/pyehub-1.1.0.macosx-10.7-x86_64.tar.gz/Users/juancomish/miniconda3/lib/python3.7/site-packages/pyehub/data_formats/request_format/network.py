"""
Provides functionality for handling a request format network_links.
"""
from typing import Union
class Network_links():
    """A wrapper for a request format Network_links."""

    def __init__(self, network_links_request: dict , capacity_link: dict) -> None:
        """Create a new wrapper for a network links.

        Args:
            network_links_request: the request format network links
            capacity_link:
        """
        self._links = network_links_request
        self._capacity = capacity_link


    @property
    def link_id(self) -> int:
        """return network link id"""
        return self._links['id']

    @property
    def start_id(self) -> int:
        """return start node id"""
        return self._links['start_id']

    @property
    def end_id(self) -> int:
        """return end node id"""
        return self._links['end_id']

    @property
    def length(self) -> float:
        """return the length of the link"""
        return self._links['length']

    @property
    def total_thermal_loss(self) -> float:
        """return the thermal loss of the connection"""
        return self._links['total_thermal_loss']

    @property
    def total_pressure_loss(self) -> float:
        """return the pressure loss of the connection"""
        return self._links['total_pressure_loss']

    @property
    def link_capacity(self) -> Union[float, str]:
        """return the capacity of the connection"""
        return self._links['capacity']

    # @property
    # def link_stream(self) -> str:
    #     """return stream associated with link"""
    #     return self._links['link_stream']

    @property
    def link_cost(self)->float:
        return self._links['link_cost']