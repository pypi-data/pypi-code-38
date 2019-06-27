# copyright 2016-2017 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""Generate CubicWeb's uicfg rules from XSD file.

XSD parsing is done using generateDS, which has been copied into the `gends` directory (only the
used bits).
"""

from six import text_type

from cubicweb import neg_role, _

from xsd import XSDM_MAPPING
from xsd2yams import CodeGenerator


FIRST_LEVEL_ETYPES = set(('SEDAArchiveTransfer',
                          'SEDABinaryDataObject', 'SEDAPhysicalDataObject',
                          'SEDAArchiveUnit'))

RTYPES_IN_TAB = set((
    'seda_binary_data_object',
    'seda_physical_data_object',
    'seda_related_transfer_reference',
    'seda_archive_unit',
    'seda_relationship',
    'seda_storage_rule',
    'seda_appraisal_rule',
    'seda_access_rule',
    'seda_dissemination_rule',
    'seda_reuse_rule',
    'seda_classification_rule',
    'seda_need_authorization',
    'seda_restriction_rule_id_ref',
    'seda_restriction_value',
    'seda_restriction_end_date',
))
for element_name in ('CodeListVersions', 'FormatIdentification', 'FileInfo', 'PhysicalDimensions',
                     'Gps', 'RelatedObjectReference', 'CustodialHistory', 'Coverage'):
    for rtype, role, path in XSDM_MAPPING.iter_rtype_role(element_name):
        RTYPES_IN_TAB.add(rtype)


class UICFGGenerator(CodeGenerator):
    """UICFG rules generator"""

    rtags_info = {
        'actionbox_appearsin_addmenu': {
            'shortname': 'abaa',
            'subject': "abaa.tag_subject_of(('*', '{rtype}', '*'), {value})",
            'object': "abaa.tag_object_of(('*', '{rtype}', '*'), {value})",
        },
        'autoform_section': {
            'shortname': 'afs',
            'subject': "afs.tag_subject_of(('*', '{rtype}', '*'), 'main', '{value}')",
            'object': "afs.tag_object_of(('*', '{rtype}', '*'), 'main', '{value}')",
        },
        'autoform_field_kwargs': {
            'shortname': 'affk',
            'subject': "affk.tag_subject_of(('*', '{rtype}', '*'), {value})",
            'object': "affk.tag_object_of(('*', '{rtype}', '*'), {value})",
        },
        'primaryview_section': {
            'shortname': 'pvs',
            'subject': "pvs.tag_subject_of(('*', '{rtype}', '*'), '{value}')",
            'object': "pvs.tag_object_of(('*', '{rtype}', '*'), '{value}')",
        },
        'reledit_ctrl': {
            'shortname': 'rec',
            'subject': "rec.tag_subject_of(('*', '{rtype}', '*'), "
            "{{'novalue_label': '{value}'}})",
            'object': "rec.tag_object_of(('*', '{rtype}', '*'), "
            "{{'novalue_label': '{value}'}})",
        },
    }

    def _generate(self, mapping, stream):
        self._processed = set()
        stream.write('from cubicweb.web import formwidgets as fw\n')
        stream.write('from cubicweb.web.views import uicfg\n\n')
        # indexview_etype_section configuration
        stream.write('ives = uicfg.indexview_etype_section\n')
        all_etypes = set()
        for mapping_element in mapping.ordered:
            etypes = self._callback('etypes_for', mapping_element)
            all_etypes.update(set(etypes))
        all_etypes.remove('SEDAArchiveTransfer')
        for etype in all_etypes:
            stream.write("ives['{0}'] = 'subobject'\n".format(etype))
        # autoform / primary view relation rtags
        for rtag, rtag_info in sorted(self.rtags_info.items()):
            alias = rtag_info['shortname']
            stream.write('\n\n{0} = uicfg.{1}\n'.format(rtag_info['shortname'], rtag))
            for mapping_element in mapping.ordered:
                for rtype, role, value in self._callback(rtag + '_for', mapping_element):
                    template = rtag_info[role]
                    stream.write(template.format(**locals()) + '\n')
        # fields order
        stream.write('pvds = uicfg.primaryview_display_ctrl\n')
        for mapping_element in mapping.ordered:
            for etype, attributes in self._callback('order_for', mapping_element):
                stream.write("affk.set_fields_order('{0}', {1})\n".format(etype, attributes))
                stream.write("pvds.set_fields_order('{0}', {1})\n".format(etype, attributes))
        # fields documentation
        stream.write('\nETYPE_ATTR_DOC = {}\n')
        template = "ETYPE_ATTR_DOC[('{etype}', '{rtype}', '{role}')] = ('{element}', {doc})\n"
        for mapping_element in mapping.ordered:
            for etype, rtype, role, element, doc in self._callback('doc_for', mapping_element):
                stream.write(template.format(etype=etype, rtype=rtype, role=role,
                                             element=element, doc=doc))

    def etypes_for_e_type_mapping(self, mapping):
        yield mapping.etype

    def autoform_section_for_rdef_mapping(self, mapping):
        if ('afs', mapping.rtype) in self._processed:
            return
        self._processed.add(('afs', mapping.rtype))
        if mapping.rtype in RTYPES_IN_TAB:
            section = 'hidden'
            role = mapping.composite or 'subject'
        elif mapping.composite:
            section = 'inlined'
            role = mapping.composite
        else:
            section = 'attributes'
            role = 'subject'
        yield mapping.rtype, neg_role(role), 'hidden'
        yield mapping.rtype, role, section

    def autoform_field_kwargs_for_e_type_mapping(self, mapping):
        for rtype, target_etype in sorted(mapping.attributes.items()):
            if rtype == 'id':
                continue
            if target_etype == 'String' and ('affk', rtype) not in self._processed:
                self._processed.add(('affk', rtype))
                yield rtype, 'subject', {'widget': Code("fw.TextInput({'size': 80})")}
            elif target_etype == 'Boolean' and ('aff', rtype) not in self._processed:
                self._processed.add(('aff', rtype))
                yield rtype, 'subject', {'allow_none': True}

    def autoform_field_kwargs_for_rdef_mapping(self, mapping):
        if mapping.rtype.endswith('code_list_version_to'):
            yield mapping.rtype, 'subject', {'label': 'value'}

    def primaryview_section_for_rdef_mapping(self, mapping):
        if ('pvs', mapping.rtype) in self._processed:
            return
        self._processed.add(('pvs', mapping.rtype))
        if mapping.rtype in RTYPES_IN_TAB:
            section = 'hidden'
            role = mapping.composite or 'subject'
            yield mapping.rtype, neg_role(role), section
            yield mapping.rtype, role, section
        elif ('Concept' in mapping.objtypes
              or 'ConceptScheme' in mapping.objtypes
              or 'AuthorityRecord' in mapping.objtypes):
            yield mapping.rtype, 'object', 'hidden'

    def reledit_ctrl_for_e_type_mapping(self, mapping):
        for rtype, target_etype in sorted(mapping.attributes.items()):
            if rtype == 'id':
                continue
            if ('rec', rtype) not in self._processed:
                self._processed.add(('rec', rtype))
                yield rtype, 'subject', _('<no value specified>')

    def reledit_ctrl_for_rdef_mapping(self, mapping):
        if ('rec', mapping.rtype) in self._processed:
            return
        self._processed.add(('rec', mapping.rtype))
        if mapping.composite is None:
            yield mapping.rtype, 'subject', '<no value specified>'
        else:
            card = mapping.card[mapping.composite == 'object']
            if card == '1':
                yield mapping.rtype, mapping.composite, _('<no value specified>')
            elif card == '?':
                yield mapping.rtype, mapping.composite, ' '

    def actionbox_appearsin_addmenu_for_rdef_mapping(self, mapping):
        if ('abaa', mapping.rtype) in self._processed:
            return
        self._processed.add(('abaa', mapping.rtype))
        role = mapping.composite or 'subject'
        yield mapping.rtype, neg_role(role), False
        yield mapping.rtype, role, False

    def order_for_e_type_mapping(self, mapping):
        attributes = ordered_attributes(mapping)
        if len(attributes) > 1:
            yield mapping.etype, attributes

    def doc_for_rdef_mapping(self, mapping):
        if mapping.element_name or mapping.desc:
            rtype = mapping.rtype
            yield mapping.subjtype, rtype, 'subject', mapping.element_name, mapping.desc
            for etype in mapping.objtypes:
                yield etype, rtype, 'object', mapping.element_name, mapping.desc


class Code(text_type):
    """Special string subclass whose repr() doesn't add quotes, for insertion of python code in a
    data structure
    """
    def __repr__(self):
        return str(self)


def ordered_attributes(mapping):
    """Given an ETypeMapping, return a list of its attributes sorted by desired order of appearance
    """
    attributes = [attr for attr in mapping.attributes if attr != 'id']
    if mapping.etype == 'SEDAArchiveTransfer':
        attributes.append('title')
        attributes.append('user_annotation')
    elif mapping.etype in ('SEDAArchiveUnit', 'SEDABinaryDataObject', 'SEDAPhysicalDataObject'):
        attributes.append('user_cardinality')
        attributes.append('user_annotation')
    elif attributes:
        if len(mapping.cards) > 1:
            attributes.insert(0, 'user_cardinality')
            attributes.append('user_annotation')
    return attributes


if __name__ == '__main__':
    UICFGGenerator.main()
