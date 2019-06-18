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
A module to generate reStructuredText tables from json schema files
"""

from jsonschema import RefResolver


class SchemaPrinter(object):
    """
    Object that create a table in reStructuedText from a json schema
    """
    def __init__(self, schema, skipfirst=False):
        """
        Create the printer object

        :param dict schema: the json schema to print
        :param bool skipfirst: flag to indicate that the first line should not be printed
        """
        self.schema = schema
        self.location = []
        self.depth = 0
        self.maxdepth = 0
        self.length = {}
        self.description_length = 12
        self.lines = []
        self.resolver = RefResolver('', self.schema)
        self.skipfirst = skipfirst
        self.parse()

    def __str__(self):
        """
        String representation of json schema (that is the printed table)
        """
        return '\n'.join(self.printlines())

    def descend(self, properties):
        """
        Descend into a subschema

        :param dict properties: the properties in the subschema
        """
        for key, subschema in sorted(properties.items()):
            key = '``{}``'.format(key)
            self.location.append(key)
            self.depth += 1
            self.maxdepth = max(self.maxdepth, self.depth)
            if self.depth not in self.length:
                self.length[self.depth] = len(key) + 2
            else:
                self.length[self.depth] = max(self.length[self.depth], len(key) + 2)

            self.parse(subschema)

            self.location.pop()
            self.depth -= 1

    def parse(self, schema=None):
        """
        Parse a schema

        :param dict schema: the schema to parse
        """
        if schema is None:
            schema = self.schema

        # If it is a reference, follow and write with that instead
        if '$ref' in schema:
            with self.resolver.resolving(schema['$ref']) as newschema:
                return self.parse(newschema)

        if 'type' not in schema:
            return

        datatype = schema['type']

        if 'description' in schema:
            self.description_length = max(self.description_length, len(schema['description']))
            description = schema['description']
        else:
            description = ''

        if datatype == 'array':
            self.location[-1] = '``{}[]``'.format(self.location[-1][2:-2])

        self.lines.append((self.location[:], datatype, description))

        if datatype == 'object':
            self.descend(schema['properties'])
        elif datatype == 'array' and isinstance(schema['items'], dict):
            items = schema['items']
            if '$ref' in items:
                with self.resolver.resolving(items['$ref']) as newschema:
                    if 'properties' in  newschema:
                        return self.descend(newschema['properties'])

            elif 'properties' in items:
                self.descend(items['properties'])

    def printlines(self):
        """
        Given a parsed schema (parsing happens when the object is constructed), print all the lines

        :return: the printed table
        :rtype: str
        """
        output_lines = []
        sepertor = ''.join('+{{keys[{n}]:{{fill[{n}]}}<{length}}}'.format(length=l, n=nr-1)
                           for nr, l in self.length.items())
        sepertor = '{start}+{{desc:{{dfill}}<{length}}}+'.format(start=sepertor, length=self.description_length)
        contentline = ''.join('{{sep[{n}]}}{{keys[{n}]: <{length}}}'.format(length=l, n=nr-1)
                              for nr, l in self.length.items())
        contentline = '{start}|{{desc: <{length}}}|'.format(start=contentline, length=self.description_length)
        lastkey = []
        dummykey = [''] * self.maxdepth
        first = True
        if self.skipfirst:
            lines = self.lines[1:]
        else:
            lines = self.lines

        for line in lines:
            key = line[0]
            limit = min(len(lastkey), len(key))
            same = [key[k] == lastkey[k] if k < limit else False for k in range(self.maxdepth)]
            fill = [' ' if x else '-' for x in same]
            keys = [key[k] if k < len(key) and not same[k] else '' for k in range(self.maxdepth)]
            sep = ['|' if k <= len(key) else ' ' for k in range(self.maxdepth)]
            output_lines.append(sepertor.format(keys=dummykey, fill=fill, desc='', dfill='-'))
            if first:
                headerkey = dummykey[:]
                headerkey[0] = 'Attributes'
                headersep = '|' + ' ' * (self.maxdepth - 1)
                output_lines.append(contentline.format(keys=headerkey, desc='Description', sep=headersep))
                output_lines.append(sepertor.format(keys=dummykey, fill='===', desc='', dfill='='))
            output_lines.append(contentline.format(keys=keys, desc=line[2], sep=sep))
            first = False
            lastkey = key
        fill = '-' * self.maxdepth
        output_lines.append(sepertor.format(keys=dummykey, fill=fill, desc='', dfill='-'))
        return output_lines

