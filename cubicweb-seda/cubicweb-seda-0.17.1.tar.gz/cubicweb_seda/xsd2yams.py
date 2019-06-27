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
"""Generate Yams schema from XSD file. XSD parsing is done using pyxst.
"""
from __future__ import print_function

try:
    from yams import BASE_TYPES
except ImportError:
    BASE_TYPES = set(('String', 'Boolean', 'Int', 'TZDatetime', 'Date', 'Bytes', 'Decimal'))

from pyxst.xml_struct import graph_nodes

from xsd import XSDMMapping, un_camel_case


EXT_ETYPES = set(['AuthorityRecord', 'ConceptScheme', 'Concept'])
RULE_TYPES = set(('access', 'appraisal', 'classification', 'reuse', 'dissemination', 'storage'))

# elements in the intermediary model but not in the yams model
SKIP_ETYPES = set(['SEDAid', 'SEDAhref', 'SEDAfilename'])
SKIP_ATTRS = set([
    'acquired_date',
    'classification_reassessing_date',
    'created_date',
    'date',
    'date_created_by_application',
    'date_signature',
    'depth',
    'diameter',
    'end_date',
    'event_date_time',
    'event_detail',
    'event_identifier',
    'gps_altitude',
    'gps_altitude_ref',
    'gps_date_stamp',
    'gps_latitude',
    'gps_latitude_ref',
    'gps_longitude',
    'gps_longitude_ref',
    'gps_version_id',
    'height',
    'href',
    'last_modified',
    'length',
    'message_identifier',
    'number_of_page',
    'physical_id',
    'received_date',
    'registered_date',
    'related_transfer_reference',
    'repository_archive_unit_pid',
    'repository_object_pid',
    'restriction_end_date',
    'originating_system_id',
    'sent_date',
    'shape',
    'start_date',
    'size',
    'system_id',
    'thickness',
    'transacted_date',
    'transfer_request_reply_identifier',
    'uncompressed_size',
    'uri',
    'weight',
    'when',
    'width',
])

# list of entity types that may be used multiple times at a same level, and
# through which relation
MULTIPLE_CHILDREN = [
    ('SEDAArchiveUnit', 'seda_archive_unit'),
    ('SEDABinaryDataObject', 'seda_binary_data_object'),
    ('SEDAPhysicalDataObject', 'seda_physical_data_object'),
    ('SEDADataObjectReference', 'seda_data_object_reference'),
    ('SEDARelatedTransferReference', 'seda_related_transfer_reference'),
    ('SEDAWriter', 'seda_writer_from'),
    ('SEDAAddressee', 'seda_addressee_from'),
    ('SEDARecipient', 'seda_recipient_from'),
    ('SEDASpatial', 'seda_spatial'),
    ('SEDATemporal', 'seda_temporal '),
    ('SEDAJuridictional', 'seda_juridictional'),
    ('SEDAKeyword', 'seda_keyword'),
    ('SEDATag', 'seda_tag'),
    ('SEDAIsVersionOf', 'seda_is_version_of'),
    ('SEDAReplaces', 'seda_replaces'),
    ('SEDARequires', 'seda_requires'),
    ('SEDAIsPartOf', 'seda_is_part_of'),
    ('SEDAReferences', 'seda_references'),
    ('SEDAEvent', 'seda_event'),
    ('SEDACustodialHistoryItem', 'seda_custodial_history_item'),
    ('SEDARelationship', 'seda_relationship'),
]

RDEF_CONSTRAINTS = {
    # x-ref constraints
    'seda_data_object_reference_id': 'S container C, O container C',
    'seda_archive_unit_ref_id_to': 'S container C, O container C',
    'seda_signed_object_id': 'S container C, O container C',
    'seda_target': 'S container C, O container C',
    # link to concept constraints
    # - scheme defined according to the relation type
    'seda_description_level': (
        'O in_scheme CS, CS scheme_relation_type CR, CR name "seda_description_level"'),
    'seda_classification_level': (
        'O in_scheme CS, CS scheme_relation_type CR, CR name "seda_classification_level"'),
    'seda_language_to': (
        'O in_scheme CS, CS scheme_relation_type CR, CR name "seda_language_to"'),
    'seda_legal_status_to': (
        'O in_scheme CS, CS scheme_relation_type CR, CR name "seda_legal_status_to"'),
    'seda_description_language_to': (
        'O in_scheme CS, CS scheme_relation_type CR, CR name "seda_description_language_to"'),
    'seda_event_type_to': (
        'O in_scheme CS, CS scheme_relation_type CR, CR name "seda_event_type_to"'),
    'seda_keyword_type_to': (
        'O in_scheme CS, CS scheme_relation_type CR, CR name "seda_keyword_type_to"'),
    'seda_type_to': (
        'O in_scheme CS, CS scheme_relation_type CR, CR name "seda_type_to"'),
    # - scheme defined according to the relation type and the subject type
    'seda_algorithm': (  # XXX still there because of signature
        'O in_scheme CS, CS scheme_relation_type CR, CR name "seda_algorithm", '
        'CS scheme_entity_type ET, ET name "{subjtype}"'),
    'seda_unit': (
        'O in_scheme CS, CS scheme_relation_type CR, CR name "seda_unit", '
        'CS scheme_entity_type ET, ET name "{subjtype}"'),
    'seda_final_action': (
        'O in_scheme CS, CS scheme_relation_type CR, CR name "seda_final_action", '
        'CS scheme_entity_type ET, ET name "{subjtype}"'),
    # - scheme defined as code list
    #   if you modify one of those, keep synchronized the SCHEME_FROM_CONTAINER map below
    #   and run "python -m tox -e make" to update the schema"
    'seda_acquisition_information_to': (
        'O in_scheme CS, '
        'EXISTS(CACLV seda_acquisition_information_code_list_version_from AT, '
        '       CACLV seda_acquisition_information_code_list_version_to CS,'
        '       S container AT)'
        ' OR EXISTS(S container AU, AU is SEDAArchiveUnit, CS scheme_relation_type RT, '
        '           RT name "seda_acquisition_information_to")'),
    'seda_mime_type_to': (
        'O in_scheme CS, '
        'EXISTS(CACLV seda_mime_type_code_list_version_from AT, '
        '       CACLV seda_mime_type_code_list_version_to CS,'
        '       S container AT)'
        ' OR EXISTS(S container AU, AU is SEDAArchiveUnit, CS scheme_relation_type RT, '
        '           RT name "file_category")'),
    'seda_encoding_to': (
        'O in_scheme CS, '
        'EXISTS(CACLV seda_encoding_code_list_version_from AT, '
        '       CACLV seda_encoding_code_list_version_to CS,'
        '       S container AT)'
        ' OR EXISTS(S container AU, AU is SEDAArchiveUnit, CS scheme_relation_type RT, '
        '           RT name "seda_encoding_to")'),
    'seda_format_id_to': (
        'O in_scheme CS, '
        'EXISTS(CACL seda_file_format_code_list_version_from AT, '
        '       CACL seda_file_format_code_list_version_to CS, '
        '       S container AT)'
        ' OR EXISTS(S container AU, AU is SEDAArchiveUnit, CS scheme_relation_type RT, '
        '           RT name "file_category")'),
    'seda_data_object_version_to': (
        'O in_scheme CS, CACLV seda_data_object_version_code_list_version_from AT, '
        'CACLV seda_data_object_version_code_list_version_to CS,'
        'S container AT'),
    'seda_type_relationship': (
        'O in_scheme CS, CACLV seda_relationship_code_list_version_from AT, '
        'CACLV seda_relationship_code_list_version_to CS,'
        'S container AT'),
    ('SEDABinaryDataObject', 'seda_algorithm'): (
        'O in_scheme CS, '
        'EXISTS(S container AT, CACLV seda_message_digest_algorithm_code_list_version_from AT, '
        '       CACLV seda_message_digest_algorithm_code_list_version_to CS) '
        'OR EXISTS(S container AU, AU is SEDAArchiveUnit, '
        '          CS scheme_relation_type RT, RT name "seda_algorithm", '
        '          CS scheme_entity_type ET, ET name "SEDABinaryDataObject")'),
    ('SEDACompressed', 'seda_algorithm'): (
        'O in_scheme CS, CACLV seda_compression_algorithm_code_list_version_from AT, '
        'CACLV seda_compression_algorithm_code_list_version_to CS,'
        'S container AT'),
    ('SEDASeqClassificationRuleRule', 'seda_rule'): (
        'O in_scheme CS, CACLV seda_classification_rule_code_list_version_from AT, '
        'CACLV seda_classification_rule_code_list_version_to CS,'
        'S container AT'),
    ('SEDASeqReuseRuleRule', 'seda_rule'): (
        'O in_scheme CS, CACLV seda_reuse_rule_code_list_version_from AT, '
        'CACLV seda_reuse_rule_code_list_version_to CS,'
        'S container AT'),
    ('SEDASeqDisseminationRuleRule', 'seda_rule'): (
        'O in_scheme CS, CACLV seda_dissemination_rule_code_list_version_from AT, '
        'CACLV seda_dissemination_rule_code_list_version_to CS,'
        'S container AT'),
    ('SEDASeqAccessRuleRule', 'seda_rule'): (
        'O in_scheme CS, '
        'EXISTS(CACLV seda_access_rule_code_list_version_from AT, '
        '       CACLV seda_access_rule_code_list_version_to CS,'
        '       S container AT)'
        ' OR EXISTS(S container AU, AU is SEDAArchiveUnit)'),
    ('SEDASeqAppraisalRuleRule', 'seda_rule'): (
        'O in_scheme CS, '
        'EXISTS(CACLV seda_appraisal_rule_code_list_version_from AT, '
        '       CACLV seda_appraisal_rule_code_list_version_to CS,'
        '       S container AT)'
        ' OR EXISTS(S container AU, AU is SEDAArchiveUnit)'),
    ('SEDASeqStorageRuleRule', 'seda_rule'): (
        'O in_scheme CS, CACLV seda_storage_rule_code_list_version_from AT, '
        'CACLV seda_storage_rule_code_list_version_to CS,'
        'S container AT'),
    # others
    'seda_keyword_reference_to': (
        'O in_scheme CS, S seda_keyword_reference_to_scheme CS'),
}
RTYPE_CARDS = {
    'seda_archive_unit': '?*',
    'seda_binary_data_object': '?*',
    'seda_comment': '1?',
    'seda_custodial_history_item': '1*',
    'seda_description': '1?',
    'seda_description_level': '1*',
    'seda_format_id_to': '**',
    'seda_mime_type_to': '**',
    'seda_physical_data_object': '?*',
    'seda_title': '11',
}
RTYPE_CARD = {
    'seda_custodial_history_item': '*',
}
_CARD_TO_CARDS = {
    '1': ['1'],
    '?': ['0..1', '1'],
    '+': ['1..n', '1'],
    '*': ['0..1', '0..n', '1', '1..n'],
}

# Map RQL expression to retrieve matching concept scheme depending on the container type.
# Client code (e.g. in `views/dataobject`) expect scheme to be mapped to the "CS" variable
# and container's eid will be specified using a "container" query argument.
SCHEME_FROM_CONTAINER = {
    'seda_acquisition_information_to': {
        'SEDAArchiveTransfer': ('CACLV seda_acquisition_information_code_list_version_from AT, '
                                'CACLV seda_acquisition_information_code_list_version_to CS, '
                                'AT eid %(container)s'),
    },
    'seda_mime_type_to': {
        'SEDAArchiveTransfer': ('CACLV seda_mime_type_code_list_version_from AT, '
                                'CACLV seda_mime_type_code_list_version_to CS, '
                                'AT eid %(container)s'),
        'SEDAArchiveUnit': 'CS scheme_relation_type RT, RT name "seda_mime_type_to"',
    },
    'seda_encoding_to': {
        'SEDAArchiveTransfer': ('CACLV seda_encoding_code_list_version_from AT, '
                                'CACLV seda_encoding_code_list_version_to CS, '
                                'AT eid %(container)s'),
        'SEDAArchiveUnit': 'CS scheme_relation_type RT, RT name "seda_encoding_to"',
    },
    'seda_format_id_to': {
        'SEDAArchiveTransfer': ('CACLV seda_file_format_code_list_version_from AT, '
                                'CACLV seda_file_format_code_list_version_to CS, '
                                'AT eid %(container)s'),
    },
    'seda_data_object_version_to': {
        'SEDAArchiveTransfer': ('CACLV seda_data_object_version_code_list_version_from AT, '
                                'CACLV seda_data_object_version_code_list_version_to CS, '
                                'AT eid %(container)s'),
    },
    'seda_type_relationship': {
        'SEDAArchiveTransfer': ('CACLV seda_relationship_code_list_version_to CS,'
                                'AT eid %(container)s'),
    },
    ('SEDABinaryDataObject', 'seda_algorithm'): {
        'SEDAArchiveTransfer': ('CACLV seda_message_digest_algorithm_code_list_version_from AT, '
                                'CACLV seda_message_digest_algorithm_code_list_version_to CS, '
                                'AT eid %(container)s'),
        'SEDAArchiveUnit': ('CS scheme_relation_type RT, RT name "seda_algorithm", '
                            'CS scheme_entity_type ET, ET name "SEDABinaryDataObject"'),
    },
    ('SEDACompressed', 'seda_algorithm'): {
        'SEDAArchiveTransfer': ('CACLV seda_compression_algorithm_code_list_version_from AT, '
                                'CACLV seda_compression_algorithm_code_list_version_to CS,'
                                'AT eid %(container)s'),
    },
}


def xsy_mapping(tagname='ArchiveTransfer'):
    mapping = XSYMapping()
    mapping.collect(XSDMMapping(tagname))
    return mapping


def yams_cardinality(minimum, maximum):
    if minimum == 0 and maximum == 1:
        return '?'
    if minimum == 1 and maximum == 1:
        return '1'
    if minimum == 0 and maximum == graph_nodes.INFINITY:
        return '*'
    if minimum == 1 and maximum == graph_nodes.INFINITY:
        return '+'
    assert False


class ETypeMapping(object):
    """Map an element to its entity type.

    * `element` is the mapped XSD element

    * `etype` is the name of the entity type

    * `card` is a cardinality if the entity should have a `user_cardinality` attribute, else None
    """
    def __init__(self, etype=None, cards=None):
        self.etype = etype
        self.cards = cards
        self.attributes = {}

    def __repr__(self):
        return '<{0}>'.format(self.etype)


class RdefMapping(object):
    """Map a relation to a simple relation definition."""

    def __init__(self, subjtype, rtype, objtypes, card,
                 composite=None, inlined=False, alias=None,
                 desc=(), element_name=None):
        assert len(card) == 2, card
        self.subjtype = subjtype
        self.rtype = rtype
        self.objtypes = objtypes
        self.card = card
        self.composite = composite
        self.inlined = inlined
        self.alias = alias
        self.desc = desc  # list of text collected under xsd:documentation
        self.element_name = element_name  # XML tag name

    @property
    def final(self):
        return next(iter(self.objtypes)) in BASE_TYPES

    def __repr__(self):
        return '<{0} {1} {2}>'.format(self.subjtype, self.rtype, self.objtypes)


class XSYMapping(object):
    """XSD 2 Yams mapping: an ordered representation of entity types and relation definitions to be
    defined.
    """

    def __init__(self):
        self.etypes = {}
        self.ordered = []
        self._rdefs = {}

    def collect(self, xsdm_mapping):  # noqa
        """Collect information for future entity types, relation types and relation definitions from
        the given `XSDMMapping` instance.
        """
        for element, etype, child_defs in xsdm_mapping:
            if etype in EXT_ETYPES or etype in BASE_TYPES:
                assert not child_defs, ('unexpected child_defs', element, etype, child_defs)
                continue
            emapping = self.map_etype(etype)
            for occ, path in child_defs:
                if not path:
                    continue  # jumped element
                if path[0][2] in SKIP_ETYPES:
                    continue
                current_emapping = emapping
                is_complex = len(path) == 2
                end_etype = path[-1][2]
                # cardinality specified in the XSD
                card = yams_cardinality(occ.minimum, occ.maximum)
                # cardinality fixed according to parent (set to 0 if element is in a choice)
                fixedcard = yams_cardinality(occ.fixed_minimum, occ.maximum)
                for i, (rtype, role, target_etype, rdef_options) in enumerate(path):
                    if target_etype in BASE_TYPES:
                        assert role == 'subject'
                        if rtype not in SKIP_ATTRS:
                            current_emapping.attributes[rtype] = target_etype
                        continue
                    # we want seda_uri for SEDAAltBinaryDataObjectAttachment but not for Attachment
                    # (it should be systematically added in XSD for the later)
                    if rtype == 'seda_uri' and emapping.etype == 'SEDAAttachment':
                        continue
                    rdef_options['desc'] = getattr(occ.target, 'desc', ())
                    rdef_options['element_name'] = getattr(occ.target, 'local_name', None)
                    if role == 'subject':
                        subjtype = current_emapping.etype
                        objtype = target_etype
                        rdef_options['alias'] = _alias(subjtype, rtype)
                    else:
                        subjtype = target_etype
                        objtype = current_emapping.etype
                        rdef_options['alias'] = _alias(objtype, rtype)
                    # compute rdef cardinalities depending on composite and fixedcard
                    composite = rdef_options.get('composite')
                    if rtype in RTYPE_CARDS:
                        rdef_options['card'] = RTYPE_CARDS[rtype]
                        if RTYPE_CARDS[rtype][0] not in '?1':
                            rdef_options['inlined'] = False
                    elif composite == 'subject':
                        rdef_options['card'] = fixedcard + '1'
                    elif composite == 'object':
                        rdef_options['card'] = '1' + fixedcard
                    elif fixedcard in '1?':
                        rdef_options['card'] = '?*'
                    else:
                        rdef_options['card'] = '**'
                    if rtype in RTYPE_CARD:
                        card = RTYPE_CARD[rtype]
                    # create mapping for intermediary entity type if necessary
                    if target_etype not in EXT_ETYPES and not isinstance(target_etype, tuple):
                        cards = _CARD_TO_CARDS[card]
                        current_emapping = self.map_etype(target_etype, cards)
                    # merge rdef with a previously added one (only for complex relations) or create
                    # a new one
                    if is_complex and i == 1 and (end_etype, rtype) in self._rdefs:
                        ref_mapping = self._rdefs[(end_etype, rtype)]
                        _merge_mapping(ref_mapping, subjtype, rtype, objtype, composite, fixedcard)
                    elif is_complex and i == 0 and (rtype, end_etype) in self._rdefs:
                        ref_mapping = self._rdefs[(rtype, end_etype)]
                        _merge_mapping(ref_mapping, subjtype, rtype, objtype, composite, fixedcard)
                    # occ is element.parent when occurence is reused for element's textual content
                    elif occ is not element.parent:
                        ref_mapping = self.map_rdef(subjtype, rtype, objtype, **rdef_options)
                        if is_complex:
                            key = (end_etype, rtype) if i == 1 else (rtype, end_etype)
                            self._rdefs[key] = ref_mapping

    def map_etype(self, etype, cards=None):
        """Register an entity type."""
        emapping = ETypeMapping(etype, cards)
        if etype in self.etypes:
            emapping = self.etypes[etype]
            if cards is not None:
                if emapping.cards is None:
                    emapping.cards = cards
                else:
                    cards = set(cards)
                    emapping_cards = set(emapping.cards)
                    if cards - emapping_cards:
                        print("# XXX extending cards for", emapping, cards - emapping_cards)
                        emapping.cards = sorted(emapping_cards | cards)
        else:
            self.etypes[emapping.etype] = emapping
            self.ordered.append(emapping)
        return emapping

    def map_rdef(self, subjtype, rtype, objtypes, card,
                 composite=None, inlined=False, alias=None,
                 desc=(), element_name=None):
        """Register a relation definition."""
        objtypes = _ensure_set(objtypes)
        mapping = RdefMapping(subjtype, rtype, objtypes,
                              card=card, composite=composite, inlined=inlined, alias=alias,
                              desc=desc, element_name=element_name)
        self.ordered.append(mapping)
        return mapping


def _ensure_set(value):
    """Given a string or a tuple, return a set."""
    if isinstance(value, set):
        return value
    elif isinstance(value, tuple):
        return set(value)
    else:
        return set([value])


def _merge_mapping(ref_mapping, subjtype, rtype, objtype, composite, card=None):
    assert composite == ref_mapping.composite, (ref_mapping, composite)
    if card is not None:
        if not card == ref_mapping.card[1]:
            print('# XXX unsupported merge because of incompatible cardinality', subjtype, rtype,
                  objtype, card, ref_mapping, ref_mapping.card)
        ref_mapping.objtypes.update(_ensure_set(objtype))
    else:
        assert ref_mapping.objtypes == _ensure_set(objtype)


# code generation ##################################################################################

class CodeGenerator(object):
    """Abstract class for code generator"""

    @classmethod
    def main(cls):
        """A main implementation to generate code"""
        import sys
        if len(sys.argv) < 2:
            mapping = xsy_mapping()
        else:
            assert len(sys.argv) == 2
            mapping = xsy_mapping(sys.argv[1])
        cls().generate(mapping, sys.stdout)

    def generate(self, mapping, stream, with_header=True):
        """Generator entry point: write generated code for :class:`XSYMapping` into the given stream
        """
        if with_header:
            stream.write(_PY_HEADER)
        self._generate(mapping, stream)

    def _generate(self, mapping, stream):
        """Override me in concret class"""
        raise NotImplementedError()

    def _callback(self, prefix, mapping_element):
        """Call method named according to `prefix` and `mapping_element`'s class and return its
        result or an empty tuple if the method doesn't exist
        """
        callback = '{0}_{1}'.format(prefix, un_camel_case(mapping_element.__class__.__name__))
        try:
            method = getattr(self, callback)
        except AttributeError:
            return ()
        return method(mapping_element)


class YamsSchemaGenerator(CodeGenerator):
    """Yams schema generator"""

    def _generate(self, mapping, stream):
        stream.write('''from yams.buildobjs import EntityType, RelationDefinition
from yams.buildobjs import String, Boolean
from cubicweb.schema import RQLConstraint
from cubicweb_seda.schema import seda_profile_element


''')
        self._processed_complex_rdef = set()
        for mapping_element in mapping.ordered:
            mapping_code = self._callback('code_for', mapping_element)
            stream.write(mapping_code.encode('utf8'))

    def code_for_e_type_mapping(self, mapping):
        if mapping.cards:
            cards = mapping.cards
            annotable = len(cards) > 1
            default_card = '1'
            code = '''\
@seda_profile_element(cardinalities={cards}, default_cardinality='{default_card}',
                      annotable={annotable})
'''.format(**locals())
        else:
            # SEDAArchiveTransfert
            code = '@seda_profile_element()\n'
        code += u'''class {0}(EntityType):
    u""""""
'''.format(mapping.etype)
        for attrname, attrtype in sorted(mapping.attributes.items()):
            if attrname == 'id':
                continue
            args = u''
            if attrtype == 'String':
                args = 'fulltextindexed=True'
            code += '    {0} = {1}({2})\n'.format(attrname, attrtype, args)
        return code + '\n\n'

    def code_for_rdef_mapping(self, mapping):
        rtype = mapping.rtype
        alias = mapping.alias
        if not alias:
            alias = _alias(mapping.subjtype, rtype)
        constraint = _constraint(mapping.subjtype, mapping.rtype)
        if len(mapping.objtypes) == 1:
            objtypes = repr(next(iter(mapping.objtypes)))
        else:
            objtypes = tuple(sorted(mapping.objtypes))
        composite = repr(mapping.composite)
        return u'''class {alias}(RelationDefinition):
    name = '{mapping.rtype}'
    subject = '{mapping.subjtype}'
    object = {objtypes}
    cardinality = '{mapping.card}'
    composite = fulltext_container = {composite}
    inlined = {mapping.inlined}
    constraints = [{constraint}]

'''.format(**locals())


def _constraint(etype, rtype):
    try:
        expr = RDEF_CONSTRAINTS[(etype, rtype)]
    except KeyError:
        try:
            expr = RDEF_CONSTRAINTS[rtype]
        except KeyError:
            return ''
    return 'RQLConstraint({0!r})'.format(expr.format(subjtype=etype))


def _alias(etype, rtype):
    if isinstance(etype, tuple):
        etype = ''.join(sorted(etype))
    return (un_camel_case(etype) + '_' + rtype).replace('seda_', '')


_PY_HEADER = '''# copyright 2016 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
"""THIS FILE IS GENERATED FROM SEDA 2.0 XSD FILES, DO NOT EDIT"""

'''


if __name__ == '__main__':
    YamsSchemaGenerator.main()
