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
"""Tools to work with XML schema files (.xsd). It contains two main entry points:

* `seda_xsd` which return the pyxst representation of the SEDA XSD, cleaned a bit to remove
  unnecessary nodes (because they are skipped or useless).

* `XSDMMapping` which hold a structure mapping the previous SEDA XSD representation to the cubicweb
  data model.
"""

import os.path as osp
import re
from collections import defaultdict, deque

from pyxst.xml_struct import build_xml_structure_from_schema, graph_nodes

from logilab.common import attrdict
from yams import BASE_TYPES

SEDA_NS = '{fr:gouv:culture:archivesdefrance:seda:v2.0}'
SKIP_ELEMENTS = set([
    'DataObjectGroupId', 'DataObjectGroupReferenceId',  # XXX simplification
    'ArchivalProfile',  # XXX reference to a profile
    'ArchiveUnitProfile',  # XXX reference to a profile unit
    'ArchiveUnitReferenceAbstract',
    'Metadata',
    'OtherMetadata',
    'ObjectGroupExtenstionAbstract',
    'OtherManagementAbstract',
    'OtherCoreTechnicalMetadataAbstract',
    'OtherDimensionsAbstract',
    'OtherCodeListAbstract',
    'AuthorizationReasonCodeListVersion',  # not for ArchiveTransfer
    'ReplyCodeListVersion',  # not for ArchiveTransfer
    ('Content', 'Signature'),  # keep signature on ArchiveTransfer, skip it on content
])
JUMP_ELEMENTS = set([
    # ArchiveTransfer
    'CodeListVersions',
    'DataObjectPackage',
    # DataObjectPackage
    'ManagementMetadata',
    'DescriptiveMetadata',
    # BinaryDataObject
    'FormatIdentification',
    'FileInfo',
    'MessageDigest',
    # PhysicalDataObject
    'PhysicalDimensions',
    'Coverage',
    'Management',
    'CustodialHistory',
    'Gps',
    'RelatedObjectReference',
    # ArchiveUnit
    'Content',
    # Keyword
    'KeywordContent',
])
XSD2YAMS = {
    'string': 'String',
    'boolean': 'Boolean',
    'int': 'Int',
    'integer': 'Int',
    'positiveInteger': 'Int',  # XXX boundaryconstraint
    'decimal': 'Decimal',
    'base64Binary': 'Bytes',
    ('base64Binary', 'hexBinary'): 'Bytes',
    'date': 'Date',
    'dateTime': 'TZDatetime',
    ('date', 'dateTime'): 'TZDatetime',

    'ID': 'String',  # + unique
    'PhysicalId': 'String',
    'SystemId': 'String',
    'OriginatingSystemId': 'String',
    'EventIdentifier': 'String',
    'MessageIdentifier': 'String',
    'TransferRequestReplyIdentifier': 'String',
    'RelatedTransferReference': 'String',
    'ArchivalAgencyArchiveUnitIdentifier': 'String',
    'OriginatingAgencyIdentifier': 'String',
    'OriginatingAgencyArchiveUnitIdentifier': 'String',
    'SubmissionAgencyIdentifier': 'String',
    'TransferringAgencyArchiveUnitIdentifier': 'String',
    'RepositoryArchiveUnitPID': 'String',
    'RepositoryObjectPID': 'String',
    'ServiceLevel': 'String',
    'Masterdata': 'String',
    'ClassificationOwner': 'String',
    'ArchivalAgreement': 'String',

    'anyURI': 'String',
    'xlink:hrefType': 'String',

    'restrictionRuleIdRef': 'String',  # XXX ref to what?
    'restrictionValue': 'String',
    'FilePlanPosition': 'String',
    'Tag': 'String',
    'Status': 'String',

    'ArchiveUnitRefId': 'SEDAArchiveUnit',
    'DataObjectReferenceId': ('SEDABinaryDataObject', 'SEDAPhysicalDataObject'),
    'SignedObjectId': 'SEDABinaryDataObject',
    'target': ('SEDABinaryDataObject', 'SEDAPhysicalDataObject'),

    'Validator': 'AuthorityRecord',
    'Signer': 'AuthorityRecord',
    'Writer': 'AuthorityRecord',
    'AuthorizedAgent': 'AuthorityRecord',
    'Addressee': 'AuthorityRecord',
    'Recipient': 'AuthorityRecord',
    'OriginatingAgency': 'AuthorityRecord',
    'SubmissionAgency': 'AuthorityRecord',
    'ArchivalAgency': 'AuthorityRecord',
    'TransferringAgency': 'AuthorityRecord',

    'type': 'Concept',  # Relationship
    'algorithm': 'Concept',
    'language': 'Concept',
    'AcquisitionInformation': 'Concept',
    'DescriptionLevel': 'Concept',
    'ClassificationLevel': 'Concept',
    'FinalAction': 'Concept',
    'Encoding': 'Concept',
    'MimeType': 'Concept',
    'EventType': 'Concept',
    'LegalStatus': 'Concept',
    'KeywordType': 'Concept',
    'KeywordReference': 'Concept',
    'CompressionAlgorithm': 'Concept',
    'MeasurementUnits': 'Concept',
    'MeasurementWeightUnits': 'Concept',
    'unit': 'Concept',
    'FinalActionStorageCode': 'Concept',
    'FinalActionAppraisalCode': 'Concept',
    'Level': 'Concept',
    'FileFormat': 'Concept',
    'VersionId': 'Concept',
    'DataObjectVersion': 'Concept',
    'FormatId': 'Concept',
    'Rule': 'Concept',
    'RefNonRuleId': 'Concept',
    'Type': 'Concept',

    'RelationshipCodeListVersion': 'ConceptScheme',
    'AcquisitionInformationCodeListVersion': 'ConceptScheme',
    'AuthorizationReasonCodeListVersion': 'ConceptScheme',
    'ClassificationRuleCodeListVersion': 'ConceptScheme',
    'ReuseRuleCodeListVersion': 'ConceptScheme',
    'DisseminationRuleCodeListVersion': 'ConceptScheme',
    'AccessRuleCodeListVersion': 'ConceptScheme',
    'AppraisalRuleCodeListVersion': 'ConceptScheme',
    'StorageRuleCodeListVersion': 'ConceptScheme',
    'DataObjectVersionCodeListVersion': 'ConceptScheme',
    'CompressionAlgorithmCodeListVersion': 'ConceptScheme',
    'FileFormatCodeListVersion': 'ConceptScheme',
    'EncodingCodeListVersion': 'ConceptScheme',
    'MimeTypeCodeListVersion': 'ConceptScheme',
    'MessageDigestAlgorithmCodeListVersion': 'ConceptScheme',
}


def un_camel_case(name):
    """Turn CamelCased name into a lower-underscored name (camel_case)."""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def etype_name(element):
    """Return entity type for the given XSD `element`."""
    if element.local_name == 'uri':
        return 'SEDAUri'
    return 'SEDA' + element.local_name


def base_rtype_name(element, etype):
    """Return base relation type for the given XSD `element`. It may be suffixed by '_from' or '_to'
    in later stage."""
    rtype = un_camel_case(element.local_name)
    if etype not in BASE_TYPES:
        rtype = 'seda_' + rtype
    return rtype


def seda_xsd():
    """Use this function to return the XSD representation of SEDA 2.0 (singleton)."""
    global _SEDA_XSD

    def seda_elements(tagname):
        return _SEDA_XSD.elts_index[SEDA_NS + tagname]

    if _SEDA_XSD is None:
        xsd_path = osp.join(osp.dirname(__file__), 'xsd', 'seda-2.0-main.xsd')
        _SEDA_XSD = build_xml_structure_from_schema(xsd_path)
        _SEDA_XSD.seda_elements = seda_elements
        _CleanerVisitor().clean(_SEDA_XSD.seda_elements('ArchiveTransfer')[0])
    return _SEDA_XSD


_SEDA_XSD = None


# XSD cleaner ######################################################################################

class _Stack(list):
    """Handle a stack using a context manage, e.g.:

    >>> with stack(element_to_stack):
    >>>    <code with element stacked>
    >>> <code with element poped>
    """
    def __call__(self, item):
        self.append(item)
        return self

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        self.pop()


class _CleanerVisitor(object):
    """Visitor that will remove unnecessary element from an XSD representation:

    * group or sequence with only one child ;

    * group or sequence which are not in an alternative and with maxOccurs = 1 and either minOccurs
      = 1 or all their children with minOccurs = 0 ;

    * alternative with minOccurs = 0 maxOccurs == graph_INFINITY, by changing child cardinality to
      minOccurs = 0 and maxOccurs = INFINITY.

    Also, all occurences will grew a new `fixed_minimum` attribute that will hold their original
    cardinality or 0 if element is in a choice.
    """
    def __init__(self):
        self._stack = _Stack()
        self._processed = set()

    def clean(self, element):
        callback = getattr(self, 'visit_' + element.__class__.__name__.lower())
        callback(element)
        callback = getattr(self, 'leave_' + element.__class__.__name__.lower())
        callback(element)

    def visit_xmlelement(self, element):
        if element in self._processed:
            return
        self._processed.add(element)
        # attribute occurences are not visited, initialize their fixed_minimum there
        for occ in element.attributes.values():
            occ.fixed_minimum = occ.minimum
        if element.content:
            with self._stack(element):
                self.clean(element.content)

    def leave_xmlelement(self, element):
        if element.local_name in SKIP_ELEMENTS:
            _drop(self._stack[-2], self._stack[-1])
        elif (len(element.parent_elts) == 1
              and (element.parent_elts[0].local_name, element.local_name) in SKIP_ELEMENTS):
            _drop(self._stack[-2], self._stack[-1])

    def visit_occurence(self, element):
        element.fixed_minimum = element.minimum
        with self._stack(element):
            self.clean(element.target)

    def leave_occurence(self, x):
        return x

    def visit_group(self, element):
        with self._stack(element):
            for occ in element.children[:]:
                self.clean(occ)

    visit_alternative = visit_sequence = visit_group

    def leave_group(self, element):
        parent_occ = self._stack[-1]
        if len(element.children) == 1:
            assert parent_occ.minimum == parent_occ.maximum == 1
            _jump(self._stack[-2], parent_occ, element.children[0])

    leave_sequence = leave_group

    def leave_alternative(self, element):
        parent_occ = self._stack[-1]
        if not element.children:
            _drop(self._stack[-2], parent_occ)
        elif len(element.children) == 1:
            assert parent_occ.maximum == 1, parent_occ
            new_occ = element.children[0]
            new_occ.minimum = min(new_occ.minimum, parent_occ.minimum)
            _jump(self._stack[-2], parent_occ, new_occ)
        # skip alternative with minOccurs = 0 / maxOccurs = unbounded
        elif parent_occ.minimum == 0 and parent_occ.maximum == graph_nodes.INFINITY:
            for occ in element.children:
                occ.minimum = occ.fixed_minimum = 0
                occ.maximum = graph_nodes.INFINITY
            _replace(self._stack[-2], parent_occ, element.children)
        else:
            for occ in element.children:
                # we need another attribute on occurences to distinguish between the cardinality
                # defined in the XSD and the one computed because of modelizing issues.
                if occ.minimum != 0:
                    occ.fixed_minimum = 0


def _replace(parent, parent_occ, new_occurences):
    idx = parent.children.index(parent_occ)
    # print 'REPLACE', parent.children[idx], 'BY', new_occurences
    del parent.children[idx]
    parent.children[idx:idx] = new_occurences


def _drop(parent, parent_occ):
    # print 'DROP', parent_occ
    parent.children.remove(parent_occ)


def _jump(parent, parent_occ, new_occurence):
    # print 'JUMP', parent_occ
    try:
        parent.children.replace(parent_occ, new_occurence)
    except AttributeError:
        parent.content = new_occurence


# XSD - datamodel iterator #########################################################################

class XSDMMapping(object):
    """Mapping between XSD and the CubicWeb data model."""

    def __init__(self, tagname='ArchiveTransfer'):
        self.xschema = seda_xsd()
        xselements = self.xschema.seda_elements(tagname)
        assert len(xselements) == 1
        self.root_xselement = xselements[0]
        self._ordered = []
        self._index = {}
        self._elements_by_name_index = None
        for parent, parent_etype, child_defs in _xsiterate(self.root_xselement):
            self._ordered.append((parent, parent_etype, child_defs))
            assert parent not in self._index
            self._index[parent] = (parent_etype, child_defs)

    def __iter__(self):
        return iter(self._ordered)

    def __getitem__(self, element):
        return self._index[element]

    def iter_rtype_role(self, xsd_element):
        """Given a XSD element name, yield (rtype, role, path) where `rtype` and `role` define a
        relation of the yams data model for a subelement, also including the full `path` if you need
        more information
        """
        subelement_defs = self[self.element_by_name(xsd_element)][1]
        for occ, path in subelement_defs:
            if occ.target.local_name in ('id', 'href'):
                continue
            if not path:
                for rtype, role, path in self.iter_rtype_role(occ.target.local_name):
                    yield rtype, role, path
            else:
                rtype, role, _, _ = path[0]
                yield rtype, role, path

    def elements_by_name(self, element_name):
        if self._elements_by_name_index is None:
            self._elements_by_name_index = defaultdict(list)
            for element in self._index:
                try:
                    name = element.local_name
                except AttributeError:
                    continue  # Alternative / Sequence node
                self._elements_by_name_index[name].append(element)
        return self._elements_by_name_index[element_name]

    def element_by_name(self, element_name):
        elements = self.elements_by_name(element_name)
        assert len(elements) == 1
        return elements[0]


def _xsiterate(xselement):  # noqa
    """Given an xsd element, return an iterator on `xselement, [(child occ, entities path)]` where
    `child occ` hold the reachable XSD child elements and `entities path` the associated list of
    `(relation, role, target_etype, {rdef options})` to traverse to get the matching child entity.

    Notice this generator has to be fulfiled to get all the proper information (else child
    definitions will miss information that will be filed later).
    """
    _processed = set()
    _stack = deque()

    def _push(xselement, etype, child_defs=None):
        if xselement not in _processed:
            _stack.append((xselement, etype, child_defs))
            _processed.add(xselement)

    _push(xselement, etype_name(xselement))
    while _stack:
        parent, parent_etype, child_defs = _stack.popleft()
        if child_defs is None:
            child_defs = []
            skip = False
        else:
            skip = True
        if isinstance(parent, graph_nodes.XMLElement):
            # process attribute definitions
            child_defs += _attributes_paths(parent)
            # if element content has been skipped on previous stage
            if parent.local_name not in XSD2YAMS and parent.attributes \
               and XSD2YAMS.get(_content_types(parent)):
                etype = XSD2YAMS[_content_types(parent)]
                if etype != 'Bytes':  # Bytes element are usually to be specified by the end user
                    rtype = base_rtype_name(parent, etype)
                    # fake an occurence to give to occ_path
                    occ = attrdict({'minimum': 1, 'fixed_minimum': 1, 'maximum': 1,
                                    'target': parent})
                    path = _occ_path(occ, etype, rtype, composite=False)
                    child_defs.append((occ, path))
        # if etype is in BASE_TYPES, it has to be yield but we must not recurse on it
        if parent_etype not in BASE_TYPES:
            for occ in _children_occurences(parent):
                child = occ.target
                if isinstance(child, graph_nodes.XMLElement):
                    if child.local_name in JUMP_ELEMENTS:
                        # insert element in parent's child_defs with an empty path, meaning we're
                        # not moving from the parent entity
                        child_defs.append((occ, []))
                        # push element so we go to its children
                        _push(child, parent_etype)
                    else:
                        etype = (XSD2YAMS.get(child.local_name)
                                 or (not child.attributes and XSD2YAMS.get(_content_types(child)))
                                 or etype_name(child))
                        rtype = base_rtype_name(child, etype)
                        composite = not (child.local_name in XSD2YAMS
                                         or (not child.attributes
                                             and _content_types(child) in XSD2YAMS))
                        path = _occ_path(occ, etype, rtype, composite=composite)
                        child_defs.append((occ, path))
                        # don't recurse if element is in XSD2YAMS
                        if child.local_name not in XSD2YAMS:
                            # target_etype is either the last element in the path, or the
                            # intermediary element if the last is a base type
                            target_etype = path[-1][2]
                            if target_etype in BASE_TYPES:
                                target_etype = path[0][2]
                            # if target_etype is still a base type, gives parent's etype to hold its
                            # children / attributes
                            if target_etype in BASE_TYPES:
                                _push(child, parent_etype)
                            else:
                                _push(child, target_etype)
                else:  # Alternative, Group or Sequence
                    # always keep alternative but attempt to skip sequence/group which are not under
                    # an alternative and with maxOccurs = 1 and either minOccurs = 1 or all children
                    # have minOccurs = 0
                    alt_etype = None
                    if (isinstance(child, graph_nodes.Alternative)
                        or isinstance(parent, graph_nodes.Alternative)
                        or not (occ.maximum == 1 and (occ.minimum == 1
                                                      or all(cocc.minimum == 0
                                                             for cocc in child.children)))):
                        # use first children to build then entity type for the element
                        sample_target = child.children[0].target
                        sample_target_name = getattr(sample_target, 'local_name',
                                                     sample_target.__class__.__name__)
                        alt_etype = 'SEDA{0}{1}{2}'.format(_shorten(occ.target.__class__.__name__),
                                                           parent_etype.replace('SEDA', ''),
                                                           sample_target_name)
                        rtype = un_camel_case(alt_etype)
                        child_defs.append((occ, [(rtype, 'subject', alt_etype,
                                                  {'composite': 'subject'})]))
                        _push(child, alt_etype)
                    else:
                        # element may be skipped, give parent's child_defs
                        _push(child, parent_etype, child_defs)
        if not skip:
            yield parent, parent_etype, child_defs


def _attributes_paths(element):
    """Return (occ, path) for the element's attributes."""
    for occ in element.attributes.values():
        xattr = occ.target
        if xattr.local_name == 'lang':
            continue
        etype = (XSD2YAMS.get(xattr.local_name)
                 or XSD2YAMS[_content_types(xattr)])
        rtype = base_rtype_name(xattr, etype)
        path = _occ_path(occ, etype, rtype, composite=False)
        yield (occ, path)


def _occ_path(occ, etype, rtype, composite):
    """Return path from an occurence element and turn it into a list of `(rtype, role, target etype,
    {rdef kwargs})`. There may be several elements when an intermediary entity to hold the
    cardinality/annotation of the relation is needed.

    Choice is made depending on the target type and the cardinality (simple or complex relation).

    `composite` is `True` (if the given `etype` is the composite) or `False` (not a composite
    relation).
    """
    composite = 'subject' if composite else None
    inlined = occ.maximum == 1
    # do we need an intermediary entity type?
    is_simple = occ.fixed_minimum == 1 and occ.maximum == 1
    if is_simple:
        # special case for seda_type which has to be desambiguified
        if rtype == 'seda_type':
            rtype += '_' + un_camel_case(occ.target.parent_elts[0].local_name)
        return [(rtype, 'subject', etype, {'composite': composite, 'inlined': inlined})]
    rtype_etype = etype_name(occ.target)
    relations = []
    # handle relation between intermediary type and the parent entity
    if etype in BASE_TYPES:
        ref_rtype = 'seda_' + rtype
    elif etype == rtype_etype:
        ref_rtype = rtype
    else:
        ref_rtype = rtype + '_from'
    relations.append((ref_rtype, 'object', rtype_etype, {'composite': 'object',
                                                         'inlined': True}))
    # handle relation between intermediary type and the child entity
    if etype in BASE_TYPES:
        relations.append((rtype, 'subject', etype, {}))
    elif etype != rtype_etype:
        relations.append((rtype + '_to', 'subject', etype, {'composite': composite,
                                                            'inlined': inlined}))
    return relations


def _children_occurences(element):
    """Return children occurence of the given XSD element (list of `Occurence` instances)."""
    if isinstance(element, (graph_nodes.Alternative, graph_nodes.Group, graph_nodes.Sequence)):
        return element.children
    else:
        assert isinstance(element, graph_nodes.XMLElement)
        if element.content:
            return (element.content,)
        else:
            return ()


def _content_types(element):
    """Return an hashable value representing the element content type (string or ordered tuple of
    types).
    """
    if isinstance(element.textual_content_type, set):
        if 'Unknown' in element.textual_content_type:
            element.textual_content_type.remove('Unknown')  # pyxst artefact
        if len(element.textual_content_type) == 1:
            element.textual_content_type = element.textual_content_type.pop()
            return element.textual_content_type
        return tuple(sorted(element.textual_content_type))
    return element.textual_content_type


def _shorten(name):
    return {'Alternative': 'Alt', 'Sequence': 'Seq'}[name]


XSDM_MAPPING = XSDMMapping()
