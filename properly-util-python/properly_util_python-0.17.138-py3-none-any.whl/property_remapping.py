import warnings

from properly_util_python.dynamo_utils import get_dynamo_item
from properly_util_python.dynamo_helper import DynamoHelperBase
from properly_util_python.table_helper import TableHelper


class PropertyRemapping:

    def __init__(self, dynamo_helper: DynamoHelperBase):
        self.dynamo_helper = dynamo_helper
        self.table_helper = TableHelper(dynamo_helper)

        # Initialize lazy loading offers
        self.offer_id = None
        self.offer_item = None

    def _get_merged_property_data(self, offer_id):
        """
        Combines the property from the user provided property with verified info.
        The verified info, if the data exists, will always overwrite the user provided info.

        The data from the user provided property and verified info are generally the same shape.
        So simple dictionary updates on top of each other should allow us to merged the data.

        This is the priority order of data. The higher data source will overwrite lower data sources.
        1. From Property --> Verified information
        3. From Offer --> Additional information
        2. From Property --> Offer location information
        4. From Offer --> User provided information

        :param offer_id: The offer ID
        :return: The merged property
        """
        offer_item = self.get_offer(offer_id)

        property_id = offer_item['propertyId']
        property_item = self._get_dynamo_item_from_table(TableHelper.PROPERTY_TABLE_NAME, property_id)

        verified_property_dict = property_item.get('verifiedInfo', {})
        property_location_dict = property_item.get('location', {})
        user_supplied_property_dict = offer_item.get('userSuppliedProperty', {})
        additional_information_dict = offer_item.get('additionalInformation', {})

        # Start with an empty combined data
        combined_property_dict = {}

        # 4. Merge in the user provided property information
        combined_property_dict.update(user_supplied_property_dict)

        # 3. Merge in the location information from the Property table
        normalized_location_dict = self._normalize_location_data(property_location_dict)
        combined_property_dict.update(normalized_location_dict)

        # 2. Merge in the additional information
        # This is automatically calculated information and additional insights
        combined_property_dict.update(additional_information_dict)

        # 1. Merge in the verified property information
        # This will overwrite any information from user provided property
        combined_property_dict.update(verified_property_dict)

        return combined_property_dict

    def _normalize_location_data(self, location_dict):
        """
        This converts the location information from the Property table
        to use the same keys as the Property model (as used by verified info and user supplied property)
        :param location_dict: The location data dictionary in the Property table format
        :return: The normalized location data dictionary to fit with the Property model
        """
        normalized_location_dict = {}

        # Address is a special case as the address is written twice in the property model
        location_address_key = 'formattedAddress'
        normalized_address_keys = ['address', 'googleFormattedAddress']

        location_address_value = location_dict.get(location_address_key, None)
        if location_address_value:
            spanned_value_array = [location_address_value] * len(normalized_address_keys)
            normalized_location_dict.update(zip(normalized_address_keys, spanned_value_array))

        normalization_key_map = {
            'lat': 'latitude',
            'lng': 'longitude',
            'placeId': 'googlePlaceId'
        }

        # Loop through the left side of the normalization key map
        for location_type_key in normalization_key_map.keys():
            # Check if the raw location dictionary has the key we want to translate
            if location_type_key not in location_dict:
                continue

            # We found a key we want to change
            # Get the key from the normalization map to the Property model key
            # (the right side of normalization key map)
            normalized_type_key = normalization_key_map[location_type_key]
            # Transfer the value over
            normalized_location_dict.update({normalized_type_key: location_dict[location_type_key]})

        return normalized_location_dict

    def _get_property_summary_dictionary(self, property_dictionary):
        """
        Creates a summarized version of the property with a lot fewer keys.
        This creates the summarized shape for pop_extra_keys=True

        :param property_dictionary: The full data format of the property
        :return: The summarized property with fewer keys
        """
        location_keys = [
            'address',
            'googleFormattedAddress',
            'latitude',
            'longitude',
            'googlePlaceId',
        ]

        normalized_location_dict = {}
        for key in location_keys:
            if key not in property_dictionary:
                continue
            normalized_location_dict[key] = property_dictionary[key]

        return normalized_location_dict

    def _get_dynamo_item_from_table(self, table_name, item_id):
        table_name_with_environment = self.table_helper.get_table_name(table_name)
        return get_dynamo_item(table_name_with_environment, item_id)

    def get_offer(self, offer_id):
        """
        Gets the offer by ID.
        This will get lazy loaded once per ID.
        If subsequent other calls uses the same offer, it will use the lazy loaded instance.
        This saves multiple calls to the database and allows easy access to the offer from multiple places.
        :param offer_id: The ID of the offer.
        :return: The offer dictionary
        """
        if not self.offer_item or self.offer_id != offer_id:
            self.offer_id = offer_id
            self.offer_item = self._get_dynamo_item_from_table(TableHelper.OFFER_TABLE_NAME, offer_id)
        return self.offer_item

    def get_home_from_offer_id(self, offer_id, *args, **kwargs):
        """
        Gets the merged home property from an offer ID.
        Can accept parameters to return a summarized version of the property.
        Can accept parameters to return the offer in the response.

        If you want to summarized form of the property, use `get_merged_property_summary_from_offer_id()`
        If you want to full form of the property, use `get_merged_property_from_offer_id()`
        If you need the offer, use `get_offer()`.  The offer is cached and will not cause another hit to
        the database if you call `get_offer()`.

        :param offer_id: The offer ID
        :param args: Not used.
        :param kwargs: pop_extra_keys - If true, returns the summarized version of the property.
                                        Otherwise returns all property data.
                       send_offer_data - If true, returns the offer dictionary. Otherwise returns only the property.
        :return: The property and optionally the offer ID.
        """
        # Deprecate this call.  Trying to remove the use of unknown arguments.
        warnings.warn("Call to deprecated function get_home_from_offer_id.",
                      category=DeprecationWarning,
                      stacklevel=2)

        is_summaries = kwargs.get('pop_extra_keys')
        is_sending_offer = kwargs.get('send_offer_data')

        if is_summaries:
            property_data = self.get_merged_property_summary_from_offer_id(offer_id)
        else:
            property_data = self.get_merged_property_from_offer_id(offer_id)

        if is_sending_offer:
            return {
                'offer': self.get_offer(offer_id),
                'home': property_data,
            }
        return property_data

    def get_merged_property_from_offer_id(self, offer_id):
        """
        Returns the merged property data.
        This is the priority order of data. The higher data source will overwrite lower data sources.
        1. From Property --> Verified information
        3. From Offer --> Additional information
        2. From Property --> Offer location information
        4. From Offer --> User provided information

        Use this function instead of `get_home_from_offer_id(offer_id)`

        :param offer_id: The offer ID
        :return: The merged property data
        """
        normalized_property = self._get_merged_property_data(offer_id)
        return normalized_property

    def get_merged_property_summary_from_offer_id(self, offer_id):
        """
        Returns the summarized version of the merged property data.
        This is the priority order of data. The higher data source will overwrite lower data sources.
        1. From Property --> Verified information
        3. From Offer --> Additional information
        2. From Property --> Offer location information
        4. From Offer --> User provided information

        The data that is in the summary are:
        * 'address'
        * 'googleFormattedAddress'
        * 'latitude'
        * 'longitude'
        * 'googlePlaceId'

        Use this function instead of `get_home_from_offer_id(offer_id, pop_extra_keys=True)`

        :param offer_id: The offer ID
        :return: The summary of the merged property data
        """
        normalized_property = self.get_merged_property_from_offer_id(offer_id)
        property_summary = self._get_property_summary_dictionary(normalized_property)
        return property_summary
