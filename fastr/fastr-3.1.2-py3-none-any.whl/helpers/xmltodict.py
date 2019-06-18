# Copyright 2011-2014 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This module contains tool for converting python dictionaries into XML object
and vice-versa.
"""
__author__ = 'hachterberg'

import re
import xml.etree.ElementTree as ElementTree
import xml.dom.minidom

import fastr

__list_entry_tag__ = 'li'
__tag_symbol_start__ = 'p_'


def _toxml(data, element=None, key=None):
    """
    Write data to an XML string

    :param data: object to write
    :param element: element to write
    :param key: key to set
    :return: XML string
    :rtype: str
    """
    toplevel = False
    if element is None:
        toplevel = True
        if key is None:
            key = 'root'

    if isinstance(data, dict):
        if element is not None:
            subelement = ElementTree.SubElement(element, key)
        else:
            element = ElementTree.Element(key)
            subelement = element

        for key, value in data.items():
            key = _prepkey(key)

            if _issimpletype(value):
                if isinstance(value, str) and ("\n" in value or len(value) > 48):
                    extra_element = ElementTree.SubElement(subelement, key)
                    extra_element.text = _to_str(value)
                else:
                    subelement.set(key, _to_str(value))
            elif value is None:
                ElementTree.SubElement(subelement, key)
            elif isinstance(value, (list, tuple)):
                _toxml(value, subelement, key)
            elif isinstance(value, dict):
                _toxml(value, subelement, key)
            else:
                raise TypeError('Invalid class to serialize ({})'.format(type(value).__name__))

    elif isinstance(data, (list, tuple)):
        if element is not None:
            subelement = ElementTree.SubElement(element, key)
        else:
            element = ElementTree.Element(key)
            subelement = element

        if key[-1] == 's':
            subkey = key[:-1]
        else:
            subkey = __list_entry_tag__

        for value in data:
            if _issimpletype(value):
                entry_element = ElementTree.SubElement(subelement, subkey)
                entry_element.text = _to_str(value)
            elif isinstance(value, list):
                _toxml(value, subelement, subkey)
            elif isinstance(value, dict):
                _toxml(value, subelement, subkey)
            elif value is None:
                ElementTree.SubElement(subelement, subkey)
            else:
                raise TypeError('Invalid class to serialize ({})'.format(type(value).__name__))

    elif data is None:
        if key is not None:
            element.set(key, '')

    elif _issimpletype(data):
        if key is not None:
            element.set(key, _to_str(data))
        else:
            element.text = _to_str(data)

    else:
        fastr.log.warning('Warning invalid type {}'.format(type(data).__name__))

    if toplevel:
        xml_string = xml.dom.minidom.parseString(ElementTree.tostring(element))
        xml_string = xml_string.toprettyxml(indent='    ').encode('utf-8')
        return xml_string


def _fromxml(root):
    """
    Parse ETree into objects

    :param root: root elemnt to parse
    :return:
    """
    if root.tag == 'root':
        return _parse_elem(root)
    else:
        return _parse_elem(root)


def _issimpletype(data):
    """
    Check if a value is a simple type (str, int, float, bool, unicode)

    :param data: value to check
    :return: flag indicating a simple type
    """
    return isinstance(data, (int, float, bool, str))


def _prepkey(key):
    """
    Prepare a key for use in XML, this means padding it with valid characters
    if needed and encoding special characters.

    :param str key: key to prepare
    :return: prepared key
    :rtype: str
    """
    newstr = []
    for char in key:
        if char.isalnum() or char in '-_':
            newstr.append(char)
        else:
            newstr.append('__{:03d}__'.format(ord(char)))

    key = ''.join(newstr)

    if not key[0].isalpha():
        key = '{}{}'.format(__tag_symbol_start__, key)
    return key


def _parse_elem(element):
    """
    Parse a single element

    :param element: element to parse
    :return: resulting object
    """
    # Prepare text, avoid whitespace issues
    text = element.text
    if text is not None and text.strip() == '':
        text = None

    if text is None and len(element.attrib) == 0 and len(element) == 0:
        # Empty, must be a none
        return None
    elif text is None and len(element.attrib) == 0 and all([x.tag == __list_entry_tag__ or x.tag == element.tag[:-1] for x in element]):
        # Must be list
        return [_parse_elem(x) for x in element]
    elif text is not None:
        # Must be simple text
        return _from_str(element.text)
    else:
        # Must be dict
        result = dict()

        for key, value in element.attrib.items():
            key = _parse_key(key)
            result[key] = _from_str(value)

        # Check if we have list children
        counts = {}
        for child in element:
            key = _parse_key(child.tag)
            if key in counts:
                counts[key] += 1
            else:
                counts[key] = 1

        for child in element:
            key = _parse_key(child.tag)

            if counts[key] == 1:
                # Entry is a single value child
                result[key] = _parse_elem(child)
            else:
                # An entry is a list
                if key not in result:
                    result[key] = []
                result[key].append(_parse_elem(child))

        return result


def _parse_key(key):
    """
    Parse a key, removes padding an special character encoding used for XML

    :param str key: key to parse
    :return: cleaned key
    :rtype: str
    """
    if key.startswith(__tag_symbol_start__):
        key = key[len(__tag_symbol_start__):]

    for match in re.findall(r'__\d\d\d__', key):
        key = re.sub(match, chr(int(match[2:5])), key)

    return key


def _to_str(value):
    """
    Convert a basic type to a str representation

    :param value: value to convert
    :return: string version
    :rtype: str
    """
    if isinstance(value, str):
        try:
            float(value)
            return '___{}'.format(value)
        except ValueError:
            return value
    else:
        return str(value)


def _from_str(text):
    """
    Convert a str to another type

    :param str text: str to parse
    :return: parsed value
    """
    # Convert to Boolean
    if text.lower() == 'true':
        return True
    elif text.lower() == 'false':
        return False
    # Find strings that started with illegal character and get escaped by ___
    elif text.startswith('___'):
        return text[3:]

    # Attempt conversion to numericals
    try:
        out = int(text)
        return out
    except ValueError:
        pass

    try:
        out = float(text)
        return out
    except ValueError:
        pass

    # Must be a str
    return str(text)


def dumps(data):
    """
    Write a dict to an XML string

    :param data: data to write
    :return: the XML data
    :rtype: str
    """
    return _toxml(data)


def dump(data, filehandle):
    """
    Write a dict to an XML file

    :param data: data to write
    :param filehandle: file handle to write to
    """
    filehandle.write(dumps(data))


def loads(data):
    """
    Load an xml string and parse it to a dict

    :param str data: the xml data to load
    :return: the parsed data
    """
    root = ElementTree.fromstring(data)
    return _fromxml(root)


def load(filehandle):
    """
    Load an xml file and parse it to a dict

    :param filehandle: file handle to load
    :return: the parsed data
    """
    tree = ElementTree.parse(filehandle)
    root = tree.getroot()
    return _fromxml(root)
