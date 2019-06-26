import logging
import os

from googlemaps import Client

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class GoogleGeocodeClient:
    """
    Client that calls the Google geocode API to get the location details of a given address
    """

    def __init__(self,
                 google_maps_key: str = None):
        self.google_maps_key = google_maps_key or os.environ.get('GOOGLE_MAPS_KEY')

    def is_place_a_street_address(self, geocode_result: dict):
        """
        Verifies the input Google geocode result is actually address.
        By inspection, the types that are home addresses are:
        - `street_address`
        - `premise`
        - `subpremise` (This includes apartments and condos)
        :param geocode_result: The individual Google geocoding response entry.
        :return: <b>True</b> If the geocoding result is a home address. <b>False</b> otherwise.
        """
        result_types = geocode_result.get("types", None)
        if result_types is None:
            return False

        google_address_types = [
            "street_address",
            "premise",
            "subpremise",
        ]

        # Are any of the keys in address_types inside the geocode result types.
        is_address = any(key in result_types for key in google_address_types)

        return is_address

    def geocode(self, address: str) -> list:
        logger.info("Google geocoding address: {}".format(address))

        google_maps_client = Client(key=self.google_maps_key)

        geocode_results = google_maps_client.geocode(address)
        logger.info("Google geocoding response length: {}".format(len(geocode_results)))

        filtered_results = list(filter(self.is_place_a_street_address, geocode_results))
        logger.info("Google geocoding filtered response length: {}".format(len(filtered_results)))

        return filtered_results
