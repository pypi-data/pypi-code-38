from smartcloudadmin.enums import AddressType
from smartcloudadmin.utils.qol import parse_time
import logging
from smartcloudadmin.config import BssConfig

logging.basicConfig(level=BssConfig.log_level)
logger = logging.getLogger(__name__)


class AddressSet:

    """
    Represents an Address Set used within IBM Social CLoud.
    Contains details about the physical location of the Organization headquarters.

    Attributes
    ----------
    state_code : enumerate
        State where Organization resides.
    postal_code : str
        Postal code of Organization
    city : str
        City where Organization resides.
    modified : Datetime
        Modification date of the Address Set record
    address_line_1 : str
        Language preference when interacting with BSS through UI.
    address_line_2 : str
        State where Organization resides.
    state : str
        State where Organization resides.
    country : enumerate
        Country where Organization resides.
    country_code : str
        Country Code where Organization resides.
    address_type : enumerate
        Type of Address for record.
   """

    def __init__(self, *, state_code, postal_code, city, state, country, country_code, address_type, modified,
                 address_line_1="", address_line_2=""):
        self.state_code = state_code
        self.postal_code = postal_code
        self.city = city
        self.modified = parse_time(modified)
        self.address_line_1 = address_line_1
        self.address_line_2 = address_line_2
        self.state = state
        self.country = country
        self.country_code = country_code
        self.address_type: AddressType = AddressType.BILLING  # todo : enum for this.

    @classmethod
    def not_provided(cls, *, modified):
        pass

    @classmethod
    def from_json(cls, *, modified):
        """
        Creates a dummy address set object for situations where no address set exists.
        Modified value passed through to see if an address set is added at a later date.

        :param modified:
        :return: address_set
        """
        my_address_set = cls(state_code="",
                             postal_code="",
                             city="",
                             state="",
                             country="",
                             country_code="",
                             address_type="",
                             modified="01/01/1970 00:00:00",
                             address_line_1="",
                             address_line_2="")
        my_address_set.modified = modified
        return my_address_set

    def __repr__(self):
        return f"""{self.address_line_1} , {self.address_line_2} , {self.city} , {self.state} ({self.state_code}) {self.postal_code}. {self.country} ({self.country_code})  {self.modified}"""

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def _dump_details(self):
        return f"""
        State Code : {self.state_code}
        Postal Code : {self.postal_code}
        City : {self.city}
        Created : created
        Modified : {self.modified}
        Address Line 1 : {self.address_line_1}
        Address Line 2 : {self.address_line_2}
        State : {self.state}
        Country : {self.country}
        Country Code : {self.country_code}
        Address Type : {self.address_type.value}"""
