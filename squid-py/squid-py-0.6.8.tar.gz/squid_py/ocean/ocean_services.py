"""Ocean module."""
#  Copyright 2018 Ocean Protocol Foundation
#  SPDX-License-Identifier: Apache-2.0

from squid_py.agreements.service_factory import ServiceDescriptor


class OceanServices:
    """Ocean services class."""

    @staticmethod
    def create_access_service(price, service_endpoint, purchase_endpoint, timeout=None):
        """
        Publish an asset with an `Access` service according to the supplied attributes.

        :param price: Asset price, int
        :param service_endpoint: str URL for initiating service access request
        :param purchase_endpoint: str URL to consume service
        :param timeout: int amount of time in seconds before the agreement expires
        :return: Service instance or None
        """
        timeout = timeout or 3600  # default to one hour timeout
        service = ServiceDescriptor.access_service_descriptor(
            price, service_endpoint, purchase_endpoint, timeout, ''
        )

        return service
