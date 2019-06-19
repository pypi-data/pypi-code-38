# Copyright (c) 2013, Combine Control Systems AB
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Combine Control Systems AB nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.
# IN NO EVENT SHALL COMBINE CONTROL SYSTEMS AB BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
Convert workflow files between JSON and XML formats. This tool is intended
to be used internally by the Sympathy platform.
"""
from __future__ import print_function
from xml.etree import ElementInclude
import sys
import os
import json
import argparse
import inspect
import traceback
import logging

import six
from lxml import etree

from . import exceptions


core_logger = logging.getLogger('core')

ns = 'http://www.sysess.org/sympathyfordata/workflow/1.0'


def xml_format_detector(source):
    """Parse source file to discover file format."""
    text = source.read()
    source.seek(0)
    file_format = 'unknown'
    if text.find(ns) >= 0:
        file_format = 'xml-1.0'
    elif (text.find('sympathy-document') >= 0 and
          text.find('gui_graph') >= 0):
        file_format = 'xml-alpha'
    elif text.find('sympathy-document') >= 0:
        file_format = 'xml-0.4'
    print('Detected format {}'.format(file_format))
    return file_format


class ToJsonInterface(object):
    """Interface for converters from XML to JSON/dict"""

    def __init__(self, xml_file):
        self._xml_file = xml_file

    def json(self):
        """Return a JSON representation of the XML file"""
        raise NotImplementedError('Not implemented for interface.')

    def dict(self):
        """Return a dict representation of the XML file"""
        raise NotImplementedError('Not implemented for interface.')


class ToXmlInterface(object):
    """Interface for converters from dict to xml"""

    def xml(self):
        """Return a XML data representation"""
        raise NotImplementedError('Not implemented for interface.')


class JsonToXml(ToXmlInterface):
    """Convert from JSON structure to XML using xml.dom.miniom"""

    def __init__(self):
        super(JsonToXml, self).__init__()

    @classmethod
    def from_file(cls, json_file):
        """Create class instance from a JSON file"""
        instance = cls()
        instance._json_data = json.load(json_file)
        return instance

    @classmethod
    def from_dict(cls, dictionary):
        """Create class instance from a Python dictionary"""
        instance = cls()
        instance._json_data = dictionary
        return instance

    def xml(self):
        flow = self._flow_to_xml(None, self._json_data)
        return etree.tostring(
            flow, xml_declaration=True, pretty_print=True, encoding='US-ASCII')

    def _flow_to_xml(self, parent, data):
        """Flow helper"""
        is_linked = data.get('is_linked', False) and parent is not None
        attribs_ = ['uuid', 'tag', 'x', 'y', 'width', 'height',
                    'cls', 'source_uuid']
        if not is_linked and data.get('is_locked'):
            attribs_.append('is_locked')

        elements_ = ['label', 'description', 'author', 'copyright', 'version',
                     'min_version']

        if not is_linked:
            elements_.append('icon')

        json_elements = ['libraries', 'pythonpaths', 'environment',
                         'overrides']
        if parent is not None:
            flow = etree.SubElement(parent, "flow")
        else:
            flow = etree.Element("flow", attrib={'xmlns': ns})
        self._add_attributes(flow, data, attribs_)

        node_id = data.get('node_id')

        if is_linked:
            if not node_id:
                flow.set('href', six.text_type(data['source']))
            else:
                flow.set('id', six.text_type(node_id))
        else:
            flow.set('id', six.text_type(data.get('id')))

        self._add_text_elements(flow, data, elements_)

        if 'aggregation_settings' in data:
            self._json_element_to_xml(
                'aggregation', flow, data['aggregation_settings'])

        self._add_json_elements(flow, data, json_elements)

        if 'parameters' in data and 'environment' in data['parameters']:
            env = data['parameters']['environment']
            if env:
                self._json_element_to_xml('environment', flow, env)

        if not is_linked and 'parameters' in data:
            self._json_element_to_xml(
                'parameters', flow,
                {k: v for k, v in data['parameters'].items() if v})

        if 'ports' in data:
            self._ports_to_xml(flow, data['ports'])

        if 'basic_ports' in data:
            self._ports_to_xml(flow, data['basic_ports'], 'basic_ports')

        if not is_linked:
            converters = (
                ('flows', self._flow_to_xml),
                ('nodes', self._node_to_xml),
                ('connections', self._connection_to_xml),
                ('textfields', self._textfield_to_xml))

            for field, converter in converters:
                if field == 'textfields':
                    # The textfields cannot be sorted according to uuid,
                    # since the ordering in the flow depends on the saved
                    # order.
                    elements = data.get(field, [])
                else:
                    elements = sorted(
                        data.get(field, []), key=lambda x: x['uuid'])
                for elem in elements:
                    converter(flow, elem)

        return flow

    def _add_text_elements(self, flow, data, element_list):
        """Create text nodes"""
        for elem in element_list:
            if elem in data:
                text_node = etree.SubElement(flow, elem)
                text_node.text = data.get(elem, '')

    def _add_json_elements(self, flow, data, element_list):
        """Create cdata nodes only for existing stuff."""
        for elem in element_list:
            if elem in data:
                self._json_element_to_xml(elem, flow, data[elem])

    def _add_attributes(self, node, data, attribute_list):
        """Attriubute helper"""
        for attrib in sorted(attribute_list):
            if attrib in data:
                node.set(attrib, six.text_type(data[attrib]))

    def _ports_to_xml(self, flow, data, ports_ns='ports'):
        """Port helper"""
        ports = etree.SubElement(flow, ports_ns)

        attribs_ = ['uuid', 'source_uuid', 'index', 'type_base', 'type',
                    'scheme', 'optional', 'x', 'y', 'key', 'parent']

        elements_ = ['label', 'description']

        for tag, port_data_list in zip(('input', 'output'),
                                       (data['inputs'], data['outputs'])):
            for port_data in port_data_list:
                port_data['label'] = port_data['description']
                port_data['key'] = port_data['name']
                port = etree.SubElement(ports, tag)
                self._add_attributes(port, port_data, attribs_)
                self._add_text_elements(port, port_data, elements_)

    def _node_to_xml(self, flow, data):
        """Node helper"""
        attribs_ = ['uuid', 'id', 'x', 'y', 'port_format', 'only_conf']
        elements_ = ['label', 'description', 'author', 'copyright', 'version']

        node = etree.SubElement(flow, 'node')
        self._add_attributes(node, data, attribs_)
        self._add_text_elements(node, data, elements_)

        if 'parameters' in data:
            parameters = etree.SubElement(node, 'parameters')
            parameters.set('type', data['parameters']['type'])
            parameters.text = json.dumps(data['parameters']['data'])
        if 'ports' in data:
            self._ports_to_xml(node, data['ports'])

    def _connection_to_xml(self, flow, data):
        """Connection helper"""
        attribs_con = ['uuid']
        attribs_port = ['node', 'port']
        attribs_route = ['x', 'y']

        # Apparently workflow_operations.update_workflow_configuration cause
        # the type to be None.
        ctype = data.get('type')
        if ctype:
            attribs_con.append('type')
        else:
            core_logger.warn(
                "Invalid or missing connection type for %s is None",
                data.get('uuid'))

        connection = etree.SubElement(flow, 'connection')
        self._add_attributes(connection, data, attribs_con)
        for tag in ['source', 'destination']:
            port_data = data[tag]
            port = etree.SubElement(connection, tag)
            self._add_attributes(port, port_data, attribs_port)

        tag = 'route'
        for route_data in data[tag]:
            route = etree.SubElement(connection, tag)
            self._add_attributes(route, route_data, attribs_route)

    def _textfield_to_xml(self, flow, data):
        """Textfield helper"""
        attribs_ = ['uuid', 'width', 'height', 'x', 'y', 'color']
        textfield = etree.SubElement(flow, 'text')
        self._add_attributes(textfield, data, attribs_)
        if 'text' in data and data['text']:
            textfield.text = data['text']
        else:
            textfield.text = ''

    def _json_element_to_xml(self, name, flow, data):
        element = etree.SubElement(flow, name)
        element.set('type', 'json')
        element.text = json.dumps(data)


def update_link_uuids(parent_dict, child_dict):
    for parent_port in (parent_dict['ports']['inputs'] +
                        parent_dict['ports']['outputs']):
        child_port = None
        for p in (child_dict['ports']['inputs'] +
                  child_dict['ports']['outputs']):
            if ('source_uuid' in parent_port and p['uuid'] ==
                    parent_port['source_uuid']):
                child_port = p
                break
        if child_port:
            child_port['source_uuid'] = child_port['uuid']
            child_port['uuid'] = parent_port['uuid']

    child_dict['source_uuid'] = child_dict['uuid']
    child_dict['uuid'] = parent_dict['uuid']


class XMLToJson(ToJsonInterface):
    """Convert from XML to JSON"""

    type_dict = {
        'uuid': str,
        'id': lambda x: str(x or ''),
        'label': lambda x: six.text_type(x).strip(),
        'description': lambda x: six.text_type(x).strip(),
        'author': lambda x: six.text_type(x).strip(),
        'only_conf': lambda x: x.lower() == 'true',
        'copyright': lambda x: six.text_type(x).strip(),
        'version': lambda x: six.text_type(x).strip(),
        'min_version': lambda x: six.text_type(x).strip(),
        'icon': lambda x: six.text_type(x).strip(),
        'is_locked': lambda x: x.lower() == 'true',
        'source': lambda x: six.text_type(x).strip(),
        'source_uuid': str,
        'x': float,
        'y': float,
        'width': float,
        'height': float,
        'port_format': str,
        'color': str,
        'index': int,
        'type': str,
        'type_base': str,
        'key': lambda x: six.text_type(x).strip(),
        'scheme': str,
        'docs': str,
        'optional': lambda x: x.lower() == 'true',
        'parent': lambda x: x.lower() == 'true',
        'node': str}

    def __init__(self, xml_file):
        super(XMLToJson, self).__init__(xml_file)
        etree.clear_error_log()
        try:
            self._doc = etree.parse(xml_file)
        except etree.XMLSyntaxError as e:
            log_text = six.text_type(
                e.error_log.filter_from_level(etree.ErrorLevels.FATAL))
            raise exceptions.ReadSyxFileError(
                u"Corrupt flow file.", log_text)
        self._file_root = os.path.dirname(xml_file.name)
        self._root = self._doc.getroot()

        self._all_nodes = {}
        self._all_parameters = {}

    def _url_loader(self, href, parse, root, encoding=None):
        """
        Loader for ElementInclude that handles relative paths and http includes
        """
        try:
            return ElementInclude.default_loader(
                os.path.join(root, href), parse, encoding)
        except Exception:
            return None

    def _node_to_dict(self, node, path):
        """
        {
            "uuid": "fbbdc405-bb8a-4ad7-b3ac-a52649941b16",
            "x": 100,
            "y": 200,
            "id": "myid1",
            "label": "MyLabel",
            "author": "Greger Cronquist <greger.cronquist@combine.se>",
            "copyright": "(c) 2013 Combine Control Systems AB",
            "description": "Longer description should that be necessary",
            "docs": "file://document.html",
            "version": "1.0",
            "ports": {
                "inputs": [...],
                "outputs": [..]
            }
            "parameters": ...
        }


        {
            "flow": {
                "nodes": []
            }
        }

        """
        contents = self._get_standard_node_data(node, path)
        self._all_nodes['{}.{}'.format(path, contents['uuid'])] = contents
        return contents

    def _add_ns(self, tag):
        """Add XML namespace to tag"""
        return '{{{}}}{}'.format(ns, tag)

    def _get_standard_node_data(self, element, path):
        """Common attributes helper for nodes and flows."""
        contents = {}
        for tag in ['author', 'label', 'description', 'copyright', 'version',
                    'docs', 'min_version', 'icon']:
            elems = element.findall(self._add_ns(tag))
            if len(elems) > 0:
                if elems[0].text:
                    text = self.type_dict[tag](elems[0].text)
                else:
                    text = ''
                contents[tag] = text

        for attribute in ['uuid', 'id', 'x', 'y', 'only_conf', 'port_format',
                          'is_locked']:
            if attribute in element.attrib:
                contents[attribute] = self.type_dict[
                    attribute](element.attrib[attribute])

        ports_ = element.findall(self._add_ns('ports'))
        if len(ports_) > 0:
            contents['ports'] = self._ports_to_dict(ports_[0])
        basic_ports_ = element.findall(self._add_ns('basic_ports'))
        if len(basic_ports_) > 0:
            contents['basic_ports'] = self._ports_to_dict(basic_ports_[0])
        params = element.findall(self._add_ns('parameters'))
        if len(params) > 0:
            contents['parameters'] = self._parameters_to_dict(
                params[0], '{}.{}'.format(path, contents['uuid']))

        return contents

    def _include_subflow(self, root, href):
        included_flow = self._url_loader(href, 'xml', root)
        return included_flow

    def _get_attrib(self, element, attrib):
        value = element.attrib.get(attrib)
        if value is not None:
            return self.type_dict[attrib](value)

    def _flow_to_dict(self, flow, path, root, is_subflow=False):
        """
        {
            "uuid": "fbbdc405-bb8a-4ad7-b3ac-a52649941b16",
            "x": 100.0,
            "y": 200.0,
            "id": "myid1",
            "label": "MyLabel",
            "author": "Greger Cronquist <greger.cronquist@combine.se>",
            "copyright": "(c) 2013 Combine Control Systems AB",
            "description": "Longer description should that be necessary",
            "min_version": "1.2.3",
            "docs": "file://document.html",
            "source": "file://OriginalSourceFile.syx",
            "is_linked": False,
            "version": "1.0",
            "parameters": {},
            "aggregation_settings": {},
            "overrides": {},
            "ports": {
                "inputs": [...],
                "outputs": [..]
            },
            "flows": [ flows... ],
            "nodes": [ nodes... ],
            "connections": [
                {
                    "uuid": "fbbdc405-bb8a-4ad7-b3ac-a52649941c19",
                    "source": {
                        "node": "fbbdc405-bb8a-4ad7-b3ac-a52649941b17",
                        "port": "fbbdc405-bb8a-4ad7-b3ac-a52649941b17"
                    },
                    "destination": {
                        "node": "fbbdc405-bb8a-4ad7-b3ac-a52649941b11",
                        "index": 0
                    }
                }
            ]
            "parameters": ...
        }
        """
        new_root = root

        # Read linked flow.
        contents_ = self._get_standard_node_data(flow, path)
        attrib_key = 'source_uuid'
        attrib_val = self._get_attrib(flow, attrib_key)
        if attrib_val is not None:
            contents_[attrib_key] = attrib_val

        contents_['tag'] = flow.get('tag', '')
        contents_['is_locked'] = (
            True if (flow.get('is_locked', 'False')) == 'True' else False)
        contents_['cls'] = flow.get('cls', 'Flow')

        source = flow.get('href')
        if is_subflow and (source or flow.get('id')):
            overrides = flow.findall(self._add_ns('overrides'))
            if len(overrides) > 0:
                contents_['overrides'] = self._json_element_to_dict(
                    overrides[0])

        if source and not flow.get('id'):
            linked_flow = self._include_subflow(root, source)

            if linked_flow is None:
                contents = contents_
                contents['broken_link'] = True
                contents['source'] = source
                contents['filename'] = os.path.normpath(
                    os.path.join(root, source))
                contents['is_linked'] = True
            else:
                new_root = os.path.join(root, os.path.dirname(source))
                contents = self._get_standard_node_data(linked_flow, path)

                for key in ('x', 'y'):
                    contents[key] = contents_[key]

                contents['source_label'] = contents['label']
                contents['label'] = contents_['label']
                contents['overrides'] = contents_.get('overrides', {})

                update_link_uuids(contents_, contents)

                contents['source'] = source
                contents['filename'] = os.path.normpath(
                    os.path.join(root, source))
                contents['is_linked'] = True

                flow = linked_flow

                if contents['uuid'] in path:
                    raise exceptions.LinkLoopError(
                        u"Corrupt flow file.",
                        u"Corrupt flow file with duplicate uses of uuid {} in "
                        u"path, likely caused by linked subflow loops."
                        .format(contents['uuid']))
        else:
            contents = contents_

        aggregation_settings = flow.findall(self._add_ns('aggregation'))
        if len(aggregation_settings) > 0:
            contents['aggregation_settings'] = self._json_element_to_dict(
                aggregation_settings[0])

        for elem in ['libraries', 'pythonpaths', 'environment']:
            data = flow.findall(self._add_ns(elem))
            if len(data) > 0:
                contents[elem] = self._json_element_to_dict(data[0])

        if len(path) > 0:
            new_path = '{}.{}'.format(path, contents['uuid'])
        else:
            new_path = contents['uuid']

        try:
            flows = [self._flow_to_dict(flow_, new_path, new_root,
                                        is_subflow=True)
                     for flow_ in flow.findall(self._add_ns('flow'))]
        except exceptions.LinkLoopError:
            contents['broken_link'] = True
            contents['flows'] = []
            contents['nodes'] = []
            contents['connections'] = []
            textfields = []
            contents['textfields'] = []
        else:
            contents['flows'] = flows
            nodes = [self._node_to_dict(node, new_path)
                     for node in flow.findall(self._add_ns('node'))]
            contents['nodes'] = nodes
            connections = [self._connection_to_dict(connection, new_path)
                           for connection in flow.findall(
                               self._add_ns('connection'))]
            contents['connections'] = connections
            textfields = [self._textfield_to_dict(textfield, new_path)
                          for textfield in flow.findall(
                              self._add_ns('text'))]
            contents['textfields'] = textfields

        return contents

    def _ports_to_dict(self, ports):
        """
        "ports": {
            "inputs": [...],
            "outputs": [..]
        }

        input/output:
        {
            "uuid": "fbbdc405-bb8a-4ad7-b3ac-a52649941b16",
            "index": "0",
            "type": "table",
            "scheme": "hdf5",
            "optional": False,
            "label": "Input 1"
            "key": "Input 1"
        }
        """
        contents = {}
        inputs = []
        outputs = []

        for tag, list_ in zip(['input', 'output'], [inputs, outputs]):
            for value in ports.findall(self._add_ns(tag)):
                port = {}
                for attribute in ['uuid', 'type', 'type_base', 'scheme',
                                  'index', 'parent', 'optional', 'x', 'y',
                                  'width', 'height', 'key', 'source_uuid']:
                    if attribute in value.attrib:
                        port[attribute] = self.type_dict[
                            attribute](value.attrib[attribute])
                if 'key' in port:
                    port['name'] = port['key']

                label = value.findall(self._add_ns('label'))
                if len(label) > 0:
                    port['description'] = (
                        self.type_dict['label'](label[0].text))
                list_.append(port)

        contents['inputs'] = inputs
        contents['outputs'] = outputs
        return contents

    def _parameters_to_dict(self, parameters, path):
        """
        {
            "type": "json",
            "data": base64 blob
        }
        """
        contents = {}
        node_path = path
        if 'node' in parameters.attrib:
            node_path += '.{}'.format(parameters.attrib['node'])

        contents['type'] = parameters.attrib['type'].strip()
        data = parameters.text.strip()
        contents['data'] = json.loads(data)

        self._all_parameters[node_path] = contents

        return contents

    def _json_element_to_dict(self, json_element):
        data = json_element.text.strip()
        contents = json.loads(data)
        return contents

    def _connection_to_dict(self, connection, path):
        """
        {
            "uuid": "fbbdc405-bb8a-4ad7-b3ac-a52649941c19",
            "source": {
                "node": "fbbdc405-bb8a-4ad7-b3ac-a52649941b17",
                "port": "fbbdc405-bb8a-4ad7-b3ac-a52649941b18"
            },
            "destination": {
                "node": "fbbdc405-bb8a-4ad7-b3ac-a52649941b18",
                "port": "fbbdc405-bb8a-4ad7-b3ac-a52649981b16"
            }
        }
        """
        contents = {}
        source = {}
        destination = {}
        contents['uuid'] = connection.attrib['uuid']
        contents['type'] = connection.attrib.get('type')

        for dict_, tag in zip([source, destination],
                              ['source', 'destination']):
            port = connection.findall(self._add_ns(tag))[0]
            dict_['node'] = port.attrib['node']
            dict_['port'] = port.attrib['port']
            contents[tag] = dict_

        routes = []
        tag = 'route'
        contents[tag] = routes
        for route in connection.findall(self._add_ns(tag)):
            routes.append({'x': float(route.attrib['x']),
                           'y': float(route.attrib['y'])})
        return contents

    def _textfield_to_dict(self, textfield, path):
        """
        {
            "height", 10.0,
            "text": "Hello world",
            "uuid": "fbbdc405-bb8a-4ad7-b3ac-a52649941c19",
            "width", 10.0,
            "x", 10.0,
            "y", 10.0,
            "color", "yellow"
        }
        """
        contents = {}
        for attrib in ['uuid', 'x', 'y', 'height', 'width', 'color']:
            if attrib in textfield.attrib:
                contents[attrib] = self.type_dict[
                    attrib](textfield.attrib[attrib])
        contents['text'] = textfield.text or ''
        return contents

    def _get_tag(self, element):
        """Tag split helper"""
        return element.tag.split('}', 1)[1]

    def _create_dictionary_from_xml(self, element):
        """Main XML parser loop"""
        tag = self._get_tag(element)
        if not tag == 'flow':
            raise RuntimeError('Not a proper workflow')
        all_contents = self._flow_to_dict(element, '', self._file_root)
        for node_path in self._all_parameters:
            if node_path in self._all_nodes:
                self._all_nodes[node_path]['parameters'] = (
                    self._all_parameters[node_path])
        return all_contents

    def json(self):
        return json.dumps(self._create_dictionary_from_xml(self._root),
                          sort_keys=True, separators=(',', ':'))

    def dict(self):
        return self._create_dictionary_from_xml(self._root)


def xml_file_to_xmltojson_converter(fq_xml_filename):
    """Simple XML to JSON parser helper"""
    to_json_converter = None
    with open(fq_xml_filename, 'r') as source_file:
        source_format = xml_format_detector(source_file)

        if source_format == 'xml-1.0':
            to_json_converter = XMLToJson(source_file)
        else:
            raise NotImplementedError(
                'XML {} not yet supported'.format(source_format))
    assert(to_json_converter is not None)
    return to_json_converter


TO_JSON_FORMAT_CLASSES = {
    'xml-1.0': XMLToJson}


def main():
    """
    Convert between different Sympathy workflow descriptions:

      - From JSON to XML)
      - From XML to JSON
    """
    parser = argparse.ArgumentParser(description=inspect.getdoc(main))
    parser.add_argument('--source-format', action='store',
                        choices=['json', 'xml-1.0',
                                 'detect'], required=True,
                        dest='source_format')
    parser.add_argument('--destination-format', action='store',
                        choices=['json', 'xml-1.0'], required=True,
                        dest='destination_format')
    parser.add_argument('source_file', action='store')
    parser.add_argument('destination_file', action='store')

    session = os.getenv('SY_TEMP_SESSION')
    if session is None:
        session = '.'
    return_code = 0
    with open(os.path.join(session, 'workflow_converter.log'), 'wb') as log:
        stdout = sys.stdout
        sys.stdout = log
        write_is_allowed = False
        arguments = parser.parse_args(sys.argv[1:])
        with open(arguments.source_file, 'rb') as source:
            source_format = arguments.source_format
            destination_format = arguments.destination_format
            try:
                if (source_format == 'detect' and
                        destination_format == 'json'):
                    source_format = xml_format_detector(source)

                if source_format == 'json':
                    if destination_format == 'xml-1.0':
                        to_xml_converter = JsonToXml.from_file(source)
                        output_data = to_xml_converter.xml()
                        write_is_allowed = True
                    else:
                        print('Conversion {} -> {} not yet supported'.
                              format(source_format, destination_format))
                elif destination_format == 'json':
                    if source_format in TO_JSON_FORMAT_CLASSES:
                        to_json_converter = TO_JSON_FORMAT_CLASSES[
                            source_format](source)
                    else:
                        print('Conversion {} -> {} not yet supported'.
                              format(source_format, destination_format))
                    output_data = to_json_converter.json()
                    write_is_allowed = True

                else:
                    print('Conversion {} -> {} not yet supported'.format(
                          source_format,
                          destination_format))

            except Exception as error:
                print('workflow_converter critical error {0}'.format(error))
                print(traceback.format_exc())
                return_code = 1

            if write_is_allowed:
                with open(arguments.destination_file, 'wb') as destination:
                    destination.write(output_data.encode('UTF-8'))

        sys.stdout = stdout
    sys.exit(return_code)


if __name__ == '__main__':
    main()
