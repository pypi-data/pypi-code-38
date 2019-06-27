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
"""Generate CubicWeb's entities from XSD file"""

import json

from xsd2yams import MULTIPLE_CHILDREN, CodeGenerator
from xsd2uicfg import ordered_attributes

MULTIPLE_ETYPES = set(etype for etype, _ in MULTIPLE_CHILDREN)

TEMPLATE = '''class {etype}(SEDAAnyEntity):
    __regid__ = '{etype}'
    fetch_attrs, cw_fetch_order = fetch_config({attributes})
    value_attr = {value_attribute}
'''


class EntitiesGenerator(CodeGenerator):

    def _generate(self, mapping, stream):
        stream.write('from cubicweb.entities import AnyEntity, fetch_config\n\n')
        stream.write('''
class SEDAAnyEntity(AnyEntity):
    __abstract__ = True
    value_attr = None

    def dc_title(self):
        if self.value_attr is None:
            return self.dc_type()
        return self.printable_value(self.value_attr)


''')
        self.altetype2rtype = {}  # rtype to children elements for all choices
        self.check_card_etypes = set()  # entity types whose cardinality must be checked
        self.check_card_rtypes = set()  # relation types whose children cardinality must be checked
        for mapping_element in mapping.ordered:
            self._callback('register_alt_rtype_for', mapping_element)
            eclass_code = self._callback('entity_class_for', mapping_element)
            if eclass_code:
                stream.write(eclass_code + '\n')
        # Write pre-computed data structures as constants
        for name, data in [('CHOICE_RTYPE', self.altetype2rtype),
                           ('CHECK_CARD_ETYPES', sorted(self.check_card_etypes)),
                           ('CHECK_CHILDREN_CARD_RTYPES', sorted(self.check_card_rtypes))]:
            stream.write(u'{} = '.format(name))
            stream.write(json.dumps(data, sort_keys=True, indent=2,
                                    separators=(',', ': ')).replace('"', "'") + '\n')

    def entity_class_for_e_type_mapping(self, mapping):
        attributes = ordered_attributes(mapping)
        value_attribute = None
        if mapping.etype in ('SEDAArchiveUnit', 'SEDABinaryDataObject', 'SEDAPhysicalDataObject'):
            pass
        elif mapping.attributes:
            value_attribute = next(iter(mapping.attributes))
        elif mapping.cards and len(mapping.cards) > 1:
            attributes = ['user_cardinality']
        if mapping.etype in MULTIPLE_ETYPES:
            attributes.insert(0, 'ordering')
        return TEMPLATE.format(etype=mapping.etype,
                               attributes=attributes,
                               value_attribute=repr(value_attribute))

    def register_alt_rtype_for_rdef_mapping(self, mapping):
        composite = mapping.composite
        if not composite:
            return
        altetypes = mapping.objtypes if composite == 'object' else [mapping.subjtype]
        for altetype in altetypes:
            if altetype.startswith('SEDAAlt'):
                self.altetype2rtype.setdefault(altetype, []).append((mapping.rtype, composite))

        if mapping.card[1] in '*+':
            self.check_card_etypes.add(mapping.subjtype)
            self.check_card_rtypes.add(mapping.rtype)


if __name__ == '__main__':
    EntitiesGenerator.main()
