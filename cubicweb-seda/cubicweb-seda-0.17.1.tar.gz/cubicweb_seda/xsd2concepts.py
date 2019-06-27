# copyright 2016 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.
"""Extract concepts scheme as Linked CSV from XSD file.

XSD parsing is done using generateDS, which has been copied into the `gends` directory (only the
used bits).
"""
import csv
import os.path as osp

from xsd import seda_xsd, un_camel_case

import sys
sys.exit('broken until pyxst stop using a set for textual_content_values')


def generate_csv(output_dir):
    xschema = seda_xsd()
    for xstype, attr_or_idx in (
            ('Diameter', 'unit'),
            ('Weight', 'unit'),
            ('FinalAction', 0),
            ('FinalAction', 1),
            ('KeywordType', 0),
            ('DescriptionLevel', 0)):
        xselements = xschema.elts_index['{fr:gouv:culture:archivesdefrance:seda:v2.0}' + xstype]
        if isinstance(attr_or_idx, int):
            xselement = xselements[attr_or_idx]
        else:
            assert len(xselements) == 1
            xselement = xselements[0].attributes[attr_or_idx].target
        with open(osp.join(output_dir, un_camel_case(xstype) + '.csv'), 'w') as stream:
            writer = csv.writer(stream, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            _GENERATORS['{0}_{1}'.format(xstype, attr_or_idx)](writer,
                                                               xselement.textual_content_values)


def _generate_pref_alt(writer, values):
    writer.writerow(['#', '$id', 'label', 'alt label'])
    writer.writerow(['type', 'url', 'string', 'string'])
    writer.writerow(['lang', '', 'en', 'en'])
    writer.writerow(['url', 'skos:Concept', 'skos:prefLabel', 'skos:altLabel'])

    def writerow(row):
        assert 1 <= len(row) <= 2, len(row)
        if len(row) == 1:
            row.append('')
        writer.writerow(['', ''] + row)

    row = []
    for value in values:
        if not row or value.isupper():
            row.append(value)
        else:
            writerow(row)
            row = [value]
    writerow(row)


def _generate_pref(writer, values):
    writer.writerow(['#', '$id', 'label'])
    writer.writerow(['type', 'url', 'string'])
    writer.writerow(['lang', '', 'en'])
    writer.writerow(['url', 'skos:Concept', 'skos:prefLabel'])
    for value in values:
        writer.writerow(['', '', value])


_GENERATORS = {
    'Diameter_unit': _generate_pref_alt,
    'Weight_unit': _generate_pref_alt,
    'FinalAction_0': _generate_pref,
    'FinalAction_1': _generate_pref,
    'KeywordType_0': _generate_pref,
    'DescriptionLevel_0': _generate_pref,
}

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 2:
        output_dir = sys.argv[1]
    elif len(sys.argv) < 2:
        output_dir = '.'
    else:
        raise Exception('too much arguments')
    generate_csv(output_dir)
