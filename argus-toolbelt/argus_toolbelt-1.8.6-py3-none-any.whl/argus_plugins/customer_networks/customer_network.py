import json
from os.path import isfile
from csv import DictReader

from argus_api.api.customernetworks.v1.network import get_customer_networks, add_customer_network, update_customer_network, delete_customer_network


class CustomerNetwork(dict):
    """A single customer network"""

    FLAG_KEYWORDS = {
        'CLIENT': [
            'CLIENT',
            'KLIENT'
        ],
        'PROXY': [
            'PROXY'
        ],
        'NAT': [
            'NAT',
            'HIDE'
        ],
        'SCANNER': [
            'SKANNER',
            'SCANNER'
        ],
        'DNS': [
            'DNS',
            'NAVNESERVER',
            'NAMESERVER'
        ],
        'GUEST': [
            'GUEST',
            'GJEST'
        ],
        'UNASSIGNED': [
            'UNASSIGNED'
        ],
        'DELETED': [
            'DELETED',
            'FJERNET',
            'SLETTET',
            'REMOVED'
        ]
    }

    def __init__(self,
                 network_address: str,
                 description: str,
                 flags: (list, set) = (),
                 customer: (str, None) = None,
                 zone: str = "UNKNOWN",
                 subnet_mask: (str, None) = None,
                 **kwargs):
        super(CustomerNetwork, self).__init__()
        self._dirty = {}
        self._fresh = True
        self.merge({
            'zone': zone,
            'network_address': network_address.strip(),
            'description': description.strip(),
            'flags': flags,
            'customer': customer,
            'subnet_mask': subnet_mask
            },
            **kwargs
        )

        if self["maskBits"] and not isinstance(self["maskBits"], int):
            self["maskBits"] = int(self["maskBits"])

    def to_json(self) -> dict:
        """
        Converts CustomerNetwork to a JSON object acceptable by Argus

        :return: dict
        """
        _json = dict(**self)
        _json.update(self._dirty)

        json = {
            key: value
            for key, value in _json.items()
            if key in ('customer', 'flagsToEnable', 'flagsToDisable', 'description', 'location', 'zone', 'id')
            # No need to provide flagsToEnable and flagsToDisable if these are empty:
            and not ('flagsTo' in key and not len(value))
        }
        json['networkAddress'] = "%s/%d" % (self['address'],
                                            int(self['maskBits']))

        if 'id' in json:
            json['networkID'] = json['id']

        if 'location' not in json:
            json['location'] = 'Unknown'
        if 'zone' not in json:
            json['zone'] = 'INTERNAL'

        return json

    def merge(self, customer_network: dict, **kwargs) -> object:
        """
        Updates this object with new values

        If any values existed before, and changed after the update, this CustomerNetwork is considered 'dirty'.

        :param dict customer_network: CustomerNetwork structure either as a dict, or as a CustomerNetwork object
        :return:
        """
        # If we have data set already in self, assign this data to _dirty instead, so that
        # we can keep track of which fields changed and only update those fields
        _attributes = self if self._fresh and len(
            self.items()) < 1 else self._dirty

        # If the other object has an ID attribute, reverse this merge instead, and merge this object into
        # the target object instead - that way, we maintain Argus' version as the source of truth
        if isinstance(customer_network, CustomerNetwork) and customer_network.exists():
            return customer_network.merge(self)
        elif isinstance(customer_network, dict) and 'id' in customer_network and customer_network['id']:
            return CustomerNetwork(customer_network).merge(self)

        # Normalize the input
        if isinstance(customer_network, CustomerNetwork):
            network_address = customer_network.to_json()['networkAddress']
            description = customer_network['description']
            flags = customer_network['flags']
            customer = customer_network['customer'] if 'customer' in customer_network else None
            subnet_mask = None
        else:
            network_address = customer_network['network_address']
            description = customer_network['description']
            flags = customer_network['flags']
            customer = customer_network['customer']
            subnet_mask = customer_network['subnet_mask']

        # Check that network address is valid, and parse out /24 subnet bits from it if set
        if '/' in network_address:
            _attributes['address'], _attributes['maskBits'] = network_address.split(
                '/')
        else:
            _attributes['address'] = network_address

        # Set description to _dirty
        _attributes['description'] = description

        # If subnet_mask is provided, check how many bits are set
        if subnet_mask:
            _attributes['maskBits'] = self._subnet_mask_to_bits(subnet_mask)

        # Extract possible flags from description
        flags_from_description = self._flags_from_description(description)

        # If we received flags, and this CustomerNetwork is a fresh one, just assign flags
        if self._fresh:
            _attributes['flags'] = flags or []

            # Parse flags from description and intersect them with the set flags
            self._dirty.update(self._diff_flags(flags_from_description))

        # If this is not a fresh object, just update _attributes with the parsed flags
        else:
            _attributes.update(self._diff_flags(flags_from_description))

        if customer and isinstance(customer, dict):
            _attributes['customer'] = customer['shortName']
            _attributes['customerID'] = customer['id']
        elif customer and isinstance(customer, str):
            _attributes['customer'] = customer

        for arg, value in kwargs.items():
            _attributes[arg] = value

        # Remove values in _dirty that are identical to self
        self._dirty = {k: v for k, v in self._dirty.items()
                       if k not in self or self[k] != v}
        
        # Set _fresh to False if _attributes is _dirty, which it is if _fresh was True
        self._fresh = _attributes is self
        _attributes['flags'] = list(self['flags'])

        if "id" in kwargs:
            _attributes["id"] = int(kwargs["id"])

        return self

    def _diff_flags(self, flags: dict) -> dict:
        """
        Receives a set of flags, and compares them against the current flags, and returns a dict with flagsToEnable
        and flagsToDisable based on the received flags intersected with the existing flags

        :param set|list flags: Set or List of flags
        :return: dict
        """
        _attributes = {}

        # Flags enabled on the server, that are not enabled on file, will be disabled
        _attributes['flagsToDisable'] = set(
            self['flags'] or []).difference(flags or ())

        # Flags enabled in file, but not on server, will be enabled
        _attributes['flagsToEnable'] = set(
            flags or []).difference(self['flags'] or ())

        # Flags existing on both, will be kept
        _attributes['flagsToEnable'] = _attributes['flagsToEnable'] | set(
            self['flags'] or ()).intersection(set(flags))

        # Cast back to list, because Set is not JSON serializable
        _attributes['flagsToEnable'] = list(_attributes['flagsToEnable'])
        _attributes['flagsToDisable'] = list(_attributes['flagsToDisable'])

        return _attributes

    def expected_flags(self) -> list:
        """
        Returns flags this CustomerNetwork will have after updating with flagsToEnable and flagsToDisable

        :return:
        """
        return list(
            set(
                set(self['flags']) | set(self._dirty['flagsToEnable']
                                         if 'flagsToEnable' in self._dirty else [])
            ) - set(self._dirty['flagsToDisable'] if 'flagsToDisable' in self._dirty else [])
        )

    def exists(self) -> bool:
        """
        Checks if we have an ID on Argus, in which case this network currently exists

        :return:
        """
        return 'id' in self and int(self['id']) > 0

    def is_dirty(self) -> bool:
        """
        Checks if this network has been modified and needs to be updated on server, e.g any fields changed, or
        missing ID field

        :return:
        """
        # Compare everything in _dirty - if we're comparing flags/flagsToEnable/flagsToDisable, compare expected
        # flags after update with current flags by merging flagsToEnable / flagsToDisable into flags
        if 'id' not in self or any(list((
            self['flags'] != self.expected_flags()
            if 'flags' in key else value != self[key]
            for key, value in self._dirty.items()
            if key in self
        ))):
            return True

        return False

    @staticmethod
    def from_json(json) -> ('CustomerNetwork', list):
        """
        Converts JSON to CustomerNetwork. If json is a list, it converts all items and returns a list. Otherwise
        converts single item and returns CustomerNetwork

        :param dict[list json: Single object from server
        :return: list<CustomerNetwork>|CustomerNetwork
        """
        if isinstance(json, dict):
            return CustomerNetwork(
                network_address="%s/%d" % (json['networkAddress']
                                           ['address'], int(json['networkAddress']['maskBits'])),
                location=json['location']['name'],
                flags=json['flags'],
                description=json['description'],
                zone=json['zone'],
                id=json['id']
            )
        elif isinstance(json, list):
            return [
                CustomerNetwork.from_json(single_object)
                for single_object in json
            ]
        else:
            return []

    @staticmethod
    def from_csv(file_path: str, header_format: iter = ('address', 'description'), headers_on_first_line: bool = False, delimiter: str = ",", customer: dict = {}) -> list:
        """
        Parses a CSV file and returns a list of networks to be updated/created/replaced to Argus

        :param str file_path: Path to CSV file
        :param str delimiter: Delimiting character in CSV (default: ,)
        :param iterable header_format: List or tuple of headers for CSV file
        :param bool headers_on_first_line: Whether headers are on first line in CSV or not - if they're not, default headers are used
        :return: list[CustomerNetwork]
        """

        # Raise FileError if file does not exist
        if not isfile(file_path):
            raise FileNotFoundError("%s does not exist" % file_path)

        # Parse CSV file to list<network> dict format
        with open(file_path) as network_csv:
            reader = DictReader(
                network_csv,
                fieldnames=None if headers_on_first_line else header_format,
                delimiter=delimiter
            )

            return [
                CustomerNetwork(
                    network_address=row['address'],
                    description=row['description'],
                    subnet_mask=row['subnet_mask'] if 'subnet_mask' in row else None,
                    customer=customer
                )
                for row in reader
            ]

    # Private
    def _flags_from_description(self, description: str = '') -> list:
        """
        Parses a network string and sets flags depending on keywords found in string

        :param str network_string: String to parse
        :param dict flags: dict with { flag: [keyword1, keyword2] }
        :return: list
        """
        return [
            flag
            for flag, keyword_list
            in CustomerNetwork.FLAG_KEYWORDS.items()
            if any((
                keyword.lower() in (description or '').lower()
                for keyword in keyword_list
            ))
        ]

    def _subnet_mask_to_bits(self, subnet_mask: str) -> int:
        """
        Returns the /bits for a subnet mask

        :param str subnet_mask:
        :return int:
        """
        return sum(map(lambda x: bin(int(x)).count("1"), subnet_mask.split('.')))

    def __contains__(self, other: ('CustomerNetwork', dict)) -> bool:
        """
        Checks if this CustomerNetwork contains the same network / bitmask, and, in effect, is a (potentially dirty)
        version of the other

        :param str|CustomerNetwork|dict other:
        :return:
        """
        if isinstance(other, str):
            return super(CustomerNetwork, self).__contains__(other)

        subject = other

        if 'address' not in subject:
            return False

        if '/' in subject['address']:
            subject['address'], subject['maskBits'] = subject['address'].split(
                '/'
            )

        if 'subnet_mask' in subject:
            subject['maskBits'] = self._subnet_mask_to_bits(
                subject['subnet_mask']
            )

        return 'maskBits' in subject and subject['address'] == self['address'] and subject['maskBits'] == self['maskBits']

    def __eq__(self, other: ('CustomerNetwork', dict)) -> bool:
        """
        Compare this CustomerNetwork to another CustomerNetwork

        :param dict|CustomerNetwork other:
        :return:
        """
        return {
            key: value
            for key, value in other.items()
            if key not in ('id', 'location', 'zone')
        } == {
            key: value
            for key, value in self.items()
            if key not in ('id', 'location', 'zone')
        }

    def __ne__(self, other: ('CustomerNetwork', dict)) -> bool:
        """
        Compare this CustomerNetwork to another CustomerNetwork

        :param dict|CustomerNetwork other:
        :return:
        """
        return not self.__eq__(other)
