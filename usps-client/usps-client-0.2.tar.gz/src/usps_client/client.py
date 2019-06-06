import io
import itertools
import logging

import certifi
import urllib3

from . import models
from .shims import etree, typing

try:
    T = typing.TypeVar("T")
    M = typing.TypeVar("M", bound=models.Base)
except AttributeError:
    pass

logger = logging.getLogger()


def _grouper(iterable):
    # type: (typing.Iterable[T]) -> typing.Generator[typing.List[T], None, None]
    iterable = iter(iterable)

    def just_five(iterable):
        # type: (typing.Iterable[T]) -> typing.List[T]
        return list(itertools.islice(iterable, 5))

    while True:
        next_group = just_five(iterable)
        if not next_group:
            return
        yield next_group


class APIException(Exception):
    def __init__(self, element):
        # type: (etree.Element) -> None
        if not isinstance(element, type(etree.ElementTree())):
            element = etree.ElementTree(element)
        try:
            error_message = u"{} ({})".format(
                element.find("./Description").text.strip(),
                element.find("./Number").text,
            )
        except AttributeError:
            xml_buffer = io.BytesIO()
            element.write(xml_buffer)
            error_message = xml_buffer.getvalue().decode(Client.ENCODING)
        super(APIException, self).__init__(error_message)


class Client:
    """
    API client for USPS Web Tools API.

    Example::

        >>> usps = Client('[your user id]')
        >>> standardized = usps.standardize_address(
        ...     firm_name="USPS Office of the Consumer Advocate",
        ...     address1="475 LENFANT PLZ SW RM 4012",
        ...     city="Washington",
        ...     state="DC",
        ...     zip5="20260",
        ... )
        >>> standardized
        Address(firm_name='USPS OFFICE OF THE CONSUMER ADVOCATE', address1=None, address2='475 LENFANT PLZ SW RM 4012', city='WASHINGTON', state='DC', zip5='20260', zip4='0004')

    """

    BASE_URL = "https://secure.shippingapis.com/ShippingAPI.dll"
    ENCODING = "iso-8859-1"

    def __init__(self, user_id, pool_manager=None):
        # type: (typing.Text, typing.Optional[urllib3.PoolManager]) -> None
        self.user_id = user_id
        if pool_manager is None:
            self.pool_manager = urllib3.PoolManager(
                headers={"User-Agent": "usps-client"},
                cert_reqs="CERT_REQUIRED",
                ca_certs=certifi.where(),
            )
        else:
            self.pool_manager = pool_manager

    def _send(self, api, element_tree):
        # type: (typing.Text, etree.ElementTree) -> etree.ElementTree
        element_tree.getroot().set("USERID", self.user_id)

        xml_buffer = io.BytesIO()

        element_tree.write(xml_buffer, method="html", encoding=self.ENCODING)
        response = self.pool_manager.request(
            "GET", self.BASE_URL, fields={"API": api, "XML": xml_buffer.getvalue()}
        )
        self.pool_manager.clear()

        response_tree = etree.ElementTree()
        response_tree.parse(
            io.BytesIO(response.data), etree.XMLParser(encoding=self.ENCODING)
        )
        return response_tree

    def _request_list(self, api, model, iterable, wrapping_element=None, revision=2):
        # type: (typing.Text, typing.Type[M], typing.Iterable[models.Base], typing.Optional[typing.Text], typing.Optional[int]) -> typing.Iterable[typing.Optional[M]]
        if wrapping_element is None:
            wrapping_element = api
        request_element_name = "{}Request".format(wrapping_element)
        response_element_name = "{}Response".format(wrapping_element)
        for request_group in _grouper(iterable):
            request_element = etree.Element(request_element_name)
            if revision:
                revision_element = etree.Element("Revision")
                revision_element.text = str(revision)
                request_element.append(revision_element)
            for item_id, item_data in enumerate(request_group):
                item_element = item_data.xml()
                item_element.set("ID", "{}".format(item_id))
                request_element.append(item_element)

            response_tree = self._send(
                api, etree.ElementTree(request_element)
            ).getroot()

            if response_tree.tag != response_element_name:
                raise APIException(response_tree)
            for result_element in response_tree:
                error_number_element = result_element.find("./Error/Number")
                if error_number_element is not None:
                    error_number = error_number_element.text
                    if (
                        error_number
                        == "-2147219399"  # No result for zipcode (such as '00000')
                        or error_number == "-2147219401"  # No result for address
                    ):
                        yield None
                    else:
                        raise APIException(result_element.find("./Error"))
                else:
                    yield model.from_xml(result_element)

    def _request_single(
        self,
        api,
        request_model,
        response_model,
        data,
        wrapping_element=None,
        revision=2,
    ):
        # type: (typing.Text, typing.Type[models.Base], typing.Type[M], typing.Dict[typing.Text, typing.Optional[typing.Text]], typing.Optional[typing.Text], typing.Optional[int]) -> typing.Optional[M]
        [result] = self._request_list(
            api, response_model, [request_model(**data)], wrapping_element, revision
        )
        return result

    ###
    # Address Information
    # https://www.usps.com/business/web-tools-apis/address-information-api.htm
    ###

    def standardize_addresses(self, addresses):
        # type: (typing.Iterable[models.RequestAddress]) -> typing.Iterable[typing.Optional[models.ResponseAddress]]
        return self._request_list(
            "Verify",
            models.ResponseAddress,
            addresses,
            wrapping_element="AddressValidate",
        )

    def standardize_address(self, **address_components):
        # type: (typing.Optional[typing.Text]) -> typing.Optional[models.ResponseAddress]
        return self._request_single(
            "Verify",
            models.RequestAddress,
            models.ResponseAddress,
            address_components,
            wrapping_element="AddressValidate",
        )

    def lookup_zip_codes(self, addresses):
        # type: (typing.Iterable[models.RequestAddress]) -> typing.Iterable[typing.Optional[models.ResponseAddress]]
        return self._request_list("ZipCodeLookup", models.ResponseAddress, addresses)

    def lookup_zip_code(self, **address_components):
        # type: (typing.Optional[typing.Text]) -> typing.Optional[models.ResponseAddress]
        return self._request_single(
            "ZipCodeLookup",
            models.RequestAddress,
            models.ResponseAddress,
            address_components,
        )

    def lookup_cities(self, zip_codes):
        # type: (typing.Iterable[typing.Text]) -> typing.Iterable[typing.Optional[models.ZipCode]]
        return self._request_list(
            "CityStateLookup",
            models.ZipCode,
            (models.ZipCode(zip5=zip_code) for zip_code in zip_codes),
        )

    def lookup_city(self, zip_code):
        # type: (typing.Text) -> typing.Optional[models.ZipCode]
        return self._request_single(
            "CityStateLookup", models.ZipCode, models.ZipCode, {"zip5": zip_code}
        )

    ###
    # Rate Calculator
    # https://www.usps.com/business/web-tools-apis/rate-calculator-api.htm
    ###

    def domestic_rates(self, packages):
        # type: (typing.Iterable[models.RequestPackage]) -> typing.Iterable[typing.Optional[models.ResponsePackage]]
        return self._request_list("RateV4", models.ResponsePackage, packages)

    def domestic_rate(self, **package_components):
        # type: (typing.Optional[typing.Text]) -> typing.Optional[models.ResponsePackage]
        return self._request_single(
            "RateV4", models.RequestPackage, models.ResponsePackage, package_components
        )
