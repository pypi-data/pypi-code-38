# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET


def dict_to_xml(dict_info):
    xml = ['<xml>']
    for key, value in dict_info.items():
        xml.append("<{1}>{0}</{1}>".format(value, key))
    xml.append('</xml>')
    return ''.join(xml)


def xml_to_dict(xml_info):
    xml_dict = {}
    root = ET.fromstring(xml_info)
    for child in root:
        xml_dict[child.tag] = child.text
    return xml_dict
