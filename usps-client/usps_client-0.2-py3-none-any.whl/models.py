import attr
import inflection

from .base_model import Base
from .shims import typing

try:
    T = typing.TypeVar("T", bound="Base")
except AttributeError:
    pass


@attr.s(slots=True)
class RequestAddress(Base):
    TAG = "Address"
    firm_name = attr.ib(default="")  # type: typing.Optional[typing.Text]
    address1 = attr.ib(default="")  # type: typing.Optional[typing.Text]
    address2 = attr.ib(default="")  # type: typing.Optional[typing.Text]
    city = attr.ib(default="")  # type: typing.Optional[typing.Text]
    state = attr.ib(default="")  # type: typing.Optional[typing.Text]
    zip5 = attr.ib(default="")  # type: typing.Optional[typing.Text]
    zip4 = attr.ib(default="")  # type: typing.Optional[typing.Text]


@attr.s(slots=True)
class ResponseAddress(Base):
    TAG = "Address"
    firm_name = attr.ib(default="")  # type: typing.Optional[typing.Text]
    address1 = attr.ib(default="")  # type: typing.Optional[typing.Text]
    address2 = attr.ib(default="")  # type: typing.Optional[typing.Text]
    city = attr.ib(default="")  # type: typing.Optional[typing.Text]
    city_abbreviation = attr.ib(default="")  # type: typing.Optional[typing.Text]
    state = attr.ib(default="")  # type: typing.Optional[typing.Text]
    zip5 = attr.ib(default="")  # type: typing.Optional[typing.Text]
    zip4 = attr.ib(default="")  # type: typing.Optional[typing.Text]
    return_text = attr.ib(default="")  # type: typing.Optional[typing.Text]
    delivery_point = attr.ib(default="")  # type: typing.Optional[typing.Text]
    carrier_route = attr.ib(default="")  # type: typing.Optional[typing.Text]
    footnotes = attr.ib(default="")  # type: typing.Optional[typing.Text]
    dpv_confirmation = attr.ib(default="")  # type: typing.Optional[typing.Text]
    dpvcmra = attr.ib(default="")  # type: typing.Optional[typing.Text]
    dpv_footnotes = attr.ib(default="")  # type: typing.Optional[typing.Text]
    dpv_false = attr.ib(default="")  # type: typing.Optional[typing.Text]
    business = attr.ib(default="")  # type: typing.Optional[typing.Text]
    central_delivery_point = attr.ib(default="")  # type: typing.Optional[typing.Text]
    vacant = attr.ib(default="")  # type: typing.Optional[typing.Text]


@attr.s(slots=True)
class ZipCode(Base):
    TAG = "ZipCode"
    zip5 = attr.ib(default="")  # type: typing.Optional[typing.Text]
    city = attr.ib(default="")  # type: typing.Optional[typing.Text]
    state = attr.ib(default="")  # type: typing.Optional[typing.Text]
    financenumber = attr.ib(default="")  # type: typing.Optional[typing.Text]
    classificationcode = attr.ib(default="")  # type: typing.Optional[typing.Text]


@attr.s(slots=True)
class SpecialService(Base):
    TAG = "SpecialService"
    service_id = attr.ib(default=None)  # type: typing.Optional[typing.Text]
    service_name = attr.ib(default=None)  # type: typing.Optional[typing.Text]
    available = attr.ib(default=None)  # type: typing.Optional[typing.Text]
    price = attr.ib(default=None)  # type: typing.Optional[typing.Text]
    declared_value_required = attr.ib(
        default=None
    )  # type: typing.Optional[typing.Text]
    due_sender_required = attr.ib(default=None)  # type: typing.Optional[typing.Text]


@attr.s(slots=True)
class Postage(Base):
    TAG = "Postage"
    mail_service = attr.ib(default=None)  # type: typing.Optional[typing.Text]
    rate = attr.ib(default=None)  # type: typing.Optional[typing.Text]
    special_services = attr.ib(
        factory=list, metadata={"model": SpecialService}
    )  # type: typing.List[SpecialService]


@attr.s(slots=True)
class RequestPackage(Base):
    TAG = "Package"
    service = attr.ib(default=None)  # type: typing.Optional[typing.Text]
    zip_origination = attr.ib(default=None)  # type: typing.Optional[typing.Text]
    zip_destination = attr.ib(default=None)  # type: typing.Optional[typing.Text]
    # first_class_mail_type = attr.ib(default=None)  # type: typing.Optional[typing.Text]
    pounds = attr.ib(default=None)  # type: typing.Optional[typing.Text]
    ounces = attr.ib(default=None)  # type: typing.Optional[typing.Text]
    container = attr.ib(default=None)  # type: typing.Optional[typing.Text]
    size = attr.ib(default=None)  # type: typing.Optional[typing.Text]
    width = attr.ib(default=None)  # type: typing.Optional[typing.Text]
    length = attr.ib(default=None)  # type: typing.Optional[typing.Text]
    height = attr.ib(default=None)  # type: typing.Optional[typing.Text]
    girth = attr.ib(default=None)  # type: typing.Optional[typing.Text]
    machinable = attr.ib(default=None)  # type: typing.Optional[typing.Text]


@attr.s(slots=True)
class ResponsePackage(Base):
    TAG = "Package"
    zip_origination = attr.ib(default=None)  # type: typing.Optional[typing.Text]
    zip_destination = attr.ib(default=None)  # type: typing.Optional[typing.Text]
    pounds = attr.ib(default=None)  # type: typing.Optional[typing.Text]
    ounces = attr.ib(default=None)  # type: typing.Optional[typing.Text]
    container = attr.ib(default=None)  # type: typing.Optional[typing.Text]
    size = attr.ib(default=None)  # type: typing.Optional[typing.Text]
    zone = attr.ib(default=None)  # type: typing.Optional[typing.Text]
    postage = attr.ib(
        default=None, metadata={"model": Postage}
    )  # type: typing.Optional[Postage]
