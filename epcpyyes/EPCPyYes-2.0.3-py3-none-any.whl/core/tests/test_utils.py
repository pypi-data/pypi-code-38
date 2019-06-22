# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2018 Rob Magee, All rights reserved.

from os.path import abspath, join, dirname
from lxml import etree

def validate_epcis_doc(epcis_doc: str):
    schema_file = abspath(join(dirname(__file__),
                               'schemas/EPCglobal-epcis-1_2.xsd'))
    with open(schema_file, 'r') as f:
        schema_root = etree.XML(f.read().encode('utf-8'))
    schema = etree.XMLSchema(schema_root)
    xml_parser = etree.XMLParser(schema=schema)
    etree.fromstring(epcis_doc, xml_parser)
