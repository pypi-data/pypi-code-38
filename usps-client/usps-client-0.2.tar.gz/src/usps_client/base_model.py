import re

import attr
import inflection

from .shims import etree, typing, unescape

try:
    T = typing.TypeVar("T", bound="Base")
except AttributeError:
    pass


def add_sub_element(parent, name, text):
    # type: (etree.Element, typing.Text, typing.Optional[typing.Text]) -> etree.Element
    element = etree.SubElement(parent, name)
    if text is not None:
        element.text = text
    return element


def deserialize_value(element, field=None):
    # type: (etree.Element, typing.Optional[attr.Attribute[typing.Any]]) -> typing.Any
    if len(element):
        if field is not None:
            try:
                model = field.metadata["model"]
            except KeyError:
                pass
            else:
                if element.tag == model.TAG:
                    return model.from_xml(element)
                else:
                    return [deserialize_value(e, field) for e in element]
        return [deserialize_value(e) for e in element]
    return (
        re.sub("<[^<]+?>", "", unescape(element.text)) if element.text else element.text
    )


class Base(object):
    @property
    def TAG(self):
        # type: () -> typing.Text
        raise NotImplementedError

    def __init__(self, **data):
        # type: (typing.Union[str, T, None]) -> None
        super().__init__()

    def xml(self):
        # type: () -> etree.Element
        element = etree.Element(self.TAG)
        for field in attr.fields(type(self)):
            field_name = field.name
            value = getattr(self, field_name)
            add_sub_element(
                element,
                inflection.camelize(field_name, uppercase_first_letter=True),
                value,
            )
        return element

    @classmethod
    def from_xml(cls, xml):
        # type: (typing.Type[T], etree.Element) -> typing.Optional[T]
        fields = attr.fields_dict(cls)
        data = {}  # type: typing.Dict[typing.Text, typing.Union[typing.Text, T]]
        for element in xml:
            attribute_name = inflection.underscore(element.tag)
            data[attribute_name] = deserialize_value(element, fields[attribute_name])
        if not data:
            return None
        return cls(**data)
