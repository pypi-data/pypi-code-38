#
# Copyright 2010 Martin Owens
#
# This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>
#
"""
Parse an XML file into a data structure for validation

  Used internally to load xml files for both xsd definitions
  and xml data. For the xml data we use a simple conversion metric which treats each
  tag level as an hash reference and multiple tags witht he same name as an array reference.

  For the xsd defininitions we use the same method as the data to aquire the data but then
  It's converted into a simpler format and any features which arn't available will produce
  warnings.
"""

from collections import OrderedDict
import logging
import xml.sax
from xml.sax.handler import ContentHandler

def islist(lst):
    """Turns lst into a list if it's not already one"""
    if not isinstance(lst, (list, tuple)):
        return [lst]
    return lst

class ParseXML(object):
    """Create a new xml parser"""
    def __init__(self, xml_content):
        self._data = None
        self._xml = xml_content

    @property
    def data(self):
        """Return the parsed data structure."""
        if not self._data:
            parser = CustomParser()
            xml.sax.parse(self._xml, parser)
            self._data = parser.get_root()
        return self._data

    @property
    def definition(self):
        """Convert the data into a definition, assume it's in xsd format."""
        data = self.data.get('schema', None)
        result = OrderedDict()
        if not data:
            return result
        result['complexTypes'] = self._complexes(data.get('complexType', None))
        result['simpleTypes'] = self._simples(data.get('simpleType', None))
        result['root'] = self._elements(data['element'], [])
        return result

    def _complexes(self, data):
        if not data:
            return OrderedDict()
        complexes = OrderedDict()
        for item in islist(data):
            if '_name' in item:
                complexes[item['_name']] = self._complex(item)
            else:
                logging.warn("Complex type without a name!")
        return complexes

    def _complex(self, data, extend=False):
        elements = []
        if 'element' in data:
            self._elements(data['element'], elements)
        if 'attribute' in data:
            self._elements(data['attribute'], elements, '_')
        # Logical And/Or have to be added as arrays of complexes
        for item in islist(data.get('or', [])):
            result = self._complex(item, extend=True)
            if extend:
                elements.extend(result)
            else:
                elements.append(result)
        # Elements can be extended or appended depending on their logic.
        for item in list(data.get('and', [])):
            result = self._complex(item, extend=False)
            if extend:
                elements.extend(result)
            else:
                elements.append(result)
        # Politly return the elements configuration.
        return elements

    def _simples(self, data):
        if not data:
            return OrderedDict()
        simples = OrderedDict()
        if isinstance(data, (tuple, list)):
            for item in data:
                simples.update(self._simples(item))
        else:
            name = data.pop('_name')
            simples[name] = self._simple(name, data)
        return simples

    def _simple(self, name, data):
        if 'enumeration' in data:
            data['enumeration'] = [item['_value'] for item in data['enumeration']]
        for key in data.keys():
            if key[1] == '_':
                data[key[1:]] = data.pop(key)
        return data

    def _elements(self, data, res, prefix=''):
        if not isinstance(data, list):
            data = [data]
        for element in data:
            res.append(self._element(element, prefix))
        return res

    def _element(self, data, prefix=''):
        element = {}
        if 'complexType' in data:
            element['complexType'] = self._complex(data.pop('complexType'))
        elif '_type' in data:
            # Get rid of the namespace, we don't need it.
            element['type'] = data.pop('_type').split(':')[-1]
        # Translate the rest of the element's attributes
        for key in data.keys():
            if key in ('name', '_name'):
                element['name'] = prefix + data[key]
            elif key[0] == '_':
                element[key[1:]] = data[key]
        return element



class CustomParser(ContentHandler, object):
    """Parsing the xml via SAX."""
    def __init__(self):
        """Create a new parser object."""
        self._name = None
        self._root = OrderedDict()
        self._current = self._root
        self._parents = [self._root]
        self._count = 0
        super(CustomParser, self).__init__()

    def get_root(self):
        """Returns the root element as a dictionary"""
        return self._root

    def skippedEntity(self, name):
        """Any elements that are skipped"""
        logging.warn("Skipping element %s", name)

    def startElement(self, name, atrs):
        """Start a new xml element"""
        new = OrderedDict()
        name = name.split(':')[-1]
        current = self._current

        if name not in current or not current[name]:
            current[name] = new
        else:
            if not isinstance(current[name], list):
                current[name] = [current[name]]
            current[name].append(new)

        self._parents.append(current)
        self._count += 1
        self._name = name
        self._current = new

        for key in atrs.keys():
            value = atrs[key]
            key = key.split(':')
            if key[0] != 'xmlns':
                self._current['_' + key[-1]] = value

    def endElement(self, name):
        """Ends an xml element"""
        name = name.split(':')[-1]
        self._count += 1
        self._current = self._parents.pop()

    def characters(self, text):
        """Handle part of a cdata by concatination"""
        # There must be a better way to test char exists.
        if text.strip():
            parent = self._parents[-1]
            elem = parent.get(self._name, '')
            if isinstance(elem, dict):
                if elem:
                    if '+data' in elem:
                        elem['+data'] += text
                    else:
                        elem['+data'] = text

                else:
                    parent[self._name] = text

            elif isinstance(elem, list):
                # Remove an empty end item
                if isinstance(elem[-1], dict) and not elem[-1]:
                    elem.pop()
                elem.append(text)
            elif self._name in parent:
                parent[self._name] += text
            else:
                parent[self._name] = text
