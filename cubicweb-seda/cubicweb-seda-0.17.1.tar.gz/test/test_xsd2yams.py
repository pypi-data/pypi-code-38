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

from StringIO import StringIO
try:
    import unittest2 as unittest
except ImportError:
    import unittest

from cubicweb import devtools  # noqa

from cubicweb_seda.xsd2yams import xsy_mapping, YamsSchemaGenerator, XSDMMapping


def readable_edef(edef):

    def name(e):
        return getattr(e, 'local_name', e.__class__.__name__)

    if len(edef) == 3:
        return (name(edef[0]), edef[1],
                [(name(rdef[0].target), [x[:-1] for x in rdef[1]])
                for rdef in edef[2]])
    else:
        return (edef[0], [(name(rdef[0].target), [x[:-1] for x in rdef[1]])
                          for rdef in edef[1]])


class CodeGenerationTC(unittest.TestCase):

    def test_base(self):
        mapping = xsy_mapping('DataObjectPackage')
        stream = StringIO()
        YamsSchemaGenerator().generate(mapping, stream)
        code = stream.getvalue()
        # assert this is valid python
        compile(code, '<generated schema>', mode='exec')
        # assert there is no duplicated classes
        classes = set()
        for line in code.splitlines():
            if line.startswith('class '):
                # don't consider case, postgres won't
                classname = line.split()[1].split('(:')[0].lower()
                self.assertNotIn(classname, classes)
                classes.add(classname)
            elif line.strip().startswith('name ='):
                name = line.split('name =')[-1].strip()[1:-1]
                self.assertLess(len(name), 64, 'too long name %r (%s))' % (name, len(name)))


class XSYMappingTC(unittest.TestCase):

    def assertEMappingEqual(self, emapping, attributes={}):
        self.assertEqual(emapping.attributes, attributes)

    def assertRMappingEqual(self, rmapping, rdefs):
        self.assertEqual(sorted([(rdef.subjtype, rdef.objtype) for rdef in rmapping.rdefs]),
                         rdefs)

    def test_keyword(self):
        mapping = xsy_mapping('Keyword')
        emapping = mapping.etypes['SEDAKeyword']
        self.assertEMappingEqual(emapping, {'keyword_content': 'String'})

    def test_binarydataobject(self):
        mapping = xsy_mapping('BinaryDataObject')
        self.assertIn('SEDABinaryDataObject', mapping.etypes)
        emapping = mapping.etypes['SEDABinaryDataObject']
        self.assertEMappingEqual(emapping, {'id': 'String', 'filename': 'String'})
        emapping = mapping.etypes['SEDACompressed']
        self.assertEMappingEqual(emapping, {'compressed': 'Boolean'})

    def test_hardcoded_cardinalities(self):
        mapping = xsy_mapping('Content')
        seda_title_card = [rdefmapping.card for rdefmapping in mapping.ordered
                           if getattr(rdefmapping, 'rtype', None) == 'seda_title'][0]
        self.assertEqual(seda_title_card, '11')
        seda_description_card = [rdefmapping.card for rdefmapping in mapping.ordered
                                 if getattr(rdefmapping, 'rtype', None) == 'seda_description'][0]
        self.assertEqual(seda_description_card, '1?')


class XSIterateTC(unittest.TestCase):

    def test_custodialhistoryitem(self):
        element_defs = iter(XSDMMapping('CustodialHistoryItem'))
        edef = next(element_defs)
        self.assertEqual(
            readable_edef(edef),
            ('CustodialHistoryItem', 'SEDACustodialHistoryItem', [
                ('when',
                 [('seda_when', 'object', 'SEDAwhen'), ('when', 'subject', 'TZDatetime')]),
                ('CustodialHistoryItem',
                 [('custodial_history_item', 'subject', 'String')]),
            ]))

    def test_keyword(self):
        element_defs = iter(XSDMMapping('Keyword'))
        edef = next(element_defs)
        self.assertEqual(
            readable_edef(edef),
            ('Keyword', 'SEDAKeyword', [
                ('id', [('seda_id', 'object', 'SEDAid'),
                        ('id', 'subject', 'String')]),
                ('KeywordContent', []),
                ('KeywordReference',
                 [('seda_keyword_reference_from', 'object', 'SEDAKeywordReference'),
                  ('seda_keyword_reference_to', 'subject', 'Concept')]),
                ('KeywordType', [('seda_keyword_type_from', 'object', 'SEDAKeywordType'),
                                 ('seda_keyword_type_to', 'subject', 'Concept')]),
            ]))
        edef = next(element_defs)
        self.assertEqual(
            readable_edef(edef),
            ('KeywordContent', 'SEDAKeyword', [
                ('KeywordContent', [('keyword_content', 'subject', 'String')]),
            ]))
        self.assertRaises(StopIteration, next, element_defs)

    def test_rule(self):
        element_defs = iter(XSDMMapping('AppraisalRule'))
        edef = next(element_defs)
        self.assertEqual(
            readable_edef(edef),
            ('AppraisalRule', 'SEDAAppraisalRule', [
                ('Sequence',
                 [('seda_seq_appraisal_rule_rule', 'subject', 'SEDASeqAppraisalRuleRule')]),
                ('Alternative',
                 [('seda_alt_appraisal_rule_prevent_inheritance',
                   'subject',
                   'SEDAAltAppraisalRulePreventInheritance')]),
                ('FinalAction', [('seda_final_action', 'subject', 'Concept')]),
            ]))
        edef = next(element_defs)
        self.assertEqual(
            readable_edef(edef),
            ('Sequence', 'SEDASeqAppraisalRuleRule', [
                ('Rule', [('seda_rule', 'subject', 'Concept')]),
                ('StartDate',
                 [('seda_start_date', 'object', 'SEDAStartDate'),
                  ('start_date', 'subject', 'Date')])]))
        edef = next(element_defs)
        self.assertEqual(
            readable_edef(edef),
            ('Alternative', 'SEDAAltAppraisalRulePreventInheritance', [
                ('PreventInheritance',
                 [('seda_prevent_inheritance', 'object', 'SEDAPreventInheritance'),
                  ('prevent_inheritance', 'subject', 'Boolean')]),
                ('RefNonRuleId',
                 [('seda_ref_non_rule_id_from', 'object', 'SEDARefNonRuleId'),
                  ('seda_ref_non_rule_id_to', 'subject', 'Concept')])]))
        edef = next(element_defs)
        self.assertEqual(
            readable_edef(edef),
            ('StartDate', 'SEDAStartDate', []))
        edef = next(element_defs)
        self.assertEqual(
            readable_edef(edef),
            ('PreventInheritance', 'SEDAPreventInheritance', []))
        self.assertRaises(StopIteration, next, element_defs)

    def test_binarydataobject(self):
        element_defs = XSDMMapping('BinaryDataObject')
        edef = next(iter(element_defs))
        children = [getattr(e[0].target, 'local_name', e[0].target.__class__.__name__)
                    for e in edef[2]]
        self.assertEqual(children, ['id', 'Relationship', 'DataObjectVersion',
                                    'Alternative', 'MessageDigest', 'Size', 'Compressed',
                                    'FormatIdentification', 'FileInfo'])
        digest_element = edef[2][4][0].target
        self.assertEqual(edef[2][4][1], [])
        digest_edef = (digest_element,) + element_defs[digest_element]
        self.assertEqual(
            readable_edef(digest_edef),
            ('MessageDigest', 'SEDABinaryDataObject', [
                ('algorithm', [('seda_algorithm', 'subject', 'Concept')]),
            ]))

    def test_archiveunit(self):
        element_defs = XSDMMapping('ArchiveUnit')
        edef = next(iter(element_defs))
        self.assertEqual(
            readable_edef(edef),
            ('ArchiveUnit', 'SEDAArchiveUnit', [
                ('id', [('id', 'subject', 'String')]),
                ('Alternative',
                 [('seda_alt_archive_unit_archive_unit_ref_id',
                   'subject', 'SEDAAltArchiveUnitArchiveUnitRefId')])
            ]))
        alt_element = edef[2][-1][0].target
        alt_edef = (alt_element,) + element_defs[alt_element]
        self.assertEqual(
            readable_edef(alt_edef),
            ('Alternative', 'SEDAAltArchiveUnitArchiveUnitRefId', [
                ('ArchiveUnitRefId',
                 [('seda_archive_unit_ref_id_from', 'object', 'SEDAArchiveUnitRefId'),
                  ('seda_archive_unit_ref_id_to', 'subject', 'SEDAArchiveUnit')]),
                ('Sequence',
                 [('seda_seq_alt_archive_unit_archive_unit_ref_id_management', 'subject',
                   'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement')])
            ]))
        seq_element = alt_edef[2][-1][0].target
        seq_edef = (seq_element,) + element_defs[seq_element]
        self.assertEqual(
            readable_edef(seq_edef),
            ('Sequence', 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement', [
                ('Management', []),
                ('Content', []),
                ('ArchiveUnit', [('seda_archive_unit', 'object', 'SEDAArchiveUnit')]),
                ('DataObjectReference',
                 [('seda_data_object_reference', 'object', 'SEDADataObjectReference')])
            ]))

    def test_dataobjectpackage(self):
        element_defs = XSDMMapping('ArchiveTransfer')
        edef = next(iter(element_defs))
        self.assertEqual(
            readable_edef(edef),
            ('ArchiveTransfer', 'SEDAArchiveTransfer', [
                ('id', [('seda_id', 'object', 'SEDAid'), ('id', 'subject', 'String')]),
                ('Comment', [('seda_comment', 'object', 'SEDAComment')]),
                ('Date', [('date', 'subject', 'TZDatetime')]),
                ('MessageIdentifier', [('message_identifier', 'subject', 'String')]),
                ('Signature', [('seda_signature', 'object', 'SEDASignature')]),
                ('ArchivalAgreement',
                 [('seda_archival_agreement', 'object', 'SEDAArchivalAgreement'),
                  ('archival_agreement', 'subject', 'String')]),
                ('CodeListVersions', []),
                ('DataObjectPackage', []),
                ('RelatedTransferReference',
                 [('seda_related_transfer_reference', 'object', 'SEDARelatedTransferReference'),
                  ('related_transfer_reference', 'subject', 'String')]),
                ('TransferRequestReplyIdentifier',
                 [('seda_transfer_request_reply_identifier', 'object',
                   'SEDATransferRequestReplyIdentifier'),
                  ('transfer_request_reply_identifier', 'subject', 'String')]),
                ('ArchivalAgency', [('seda_archival_agency', 'subject', 'AuthorityRecord')]),
                ('TransferringAgency',
                 [('seda_transferring_agency', 'subject', 'AuthorityRecord')]),
            ]))
        dao_element = edef[2][7][0].target
        dao_edef = (dao_element,) + element_defs[dao_element]
        descr_element = dao_edef[2][3][0].target
        descr_edef = (descr_element,) + element_defs[descr_element]
        self.assertEqual(
            readable_edef(descr_edef),
            ('DescriptiveMetadata', 'SEDAArchiveTransfer', [
                ('ArchiveUnit', [('seda_archive_unit', 'object', 'SEDAArchiveUnit')])
            ]))
        mgmt_element = dao_edef[2][4][0].target
        mgmt_edef = (mgmt_element,) + element_defs[mgmt_element]
        self.assertEqual(
            readable_edef(mgmt_edef),
            ('ManagementMetadata', 'SEDAArchiveTransfer', [
                ('id', [('seda_id', 'object', 'SEDAid'), ('id', 'subject', 'String')]),
                ('ServiceLevel',
                 [('seda_service_level', 'object', 'SEDAServiceLevel'),
                  ('service_level', 'subject', 'String')]),
                ('AcquisitionInformation',
                 [('seda_acquisition_information_from', 'object', 'SEDAAcquisitionInformation'),
                  ('seda_acquisition_information_to', 'subject', 'Concept')]),
                ('LegalStatus',
                 [('seda_legal_status_from', 'object', 'SEDALegalStatus'),
                  ('seda_legal_status_to', 'subject', 'Concept')]),
                ('OriginatingAgencyIdentifier',
                 [('seda_originating_agency_identifier', 'object',
                   'SEDAOriginatingAgencyIdentifier'),
                  ('originating_agency_identifier', 'subject', 'String')]),
                ('SubmissionAgencyIdentifier',
                 [('seda_submission_agency_identifier', 'object', 'SEDASubmissionAgencyIdentifier'),
                  ('submission_agency_identifier', 'subject', 'String')]),
                ('StorageRule', [('seda_storage_rule', 'object', 'SEDAStorageRule')]),
                ('AppraisalRule', [('seda_appraisal_rule', 'object', 'SEDAAppraisalRule')]),
                ('AccessRule', [('seda_access_rule', 'object', 'SEDAAccessRule')]),
                ('DisseminationRule',
                 [('seda_dissemination_rule', 'object', 'SEDADisseminationRule')]),
                ('ReuseRule', [('seda_reuse_rule', 'object', 'SEDAReuseRule')]),
                ('ClassificationRule',
                 [('seda_classification_rule', 'object', 'SEDAClassificationRule')]),
                ('NeedAuthorization',
                 [('seda_need_authorization', 'object', 'SEDANeedAuthorization'),
                  ('need_authorization', 'subject', 'Boolean')]),
            ]))

    def test_elements_by_name(self):
        mapping = XSDMMapping('ArchiveTransfer')
        self.assertEqual(len(mapping.elements_by_name('StartDate')), 2)
        self.assertEqual(len(mapping.elements_by_name('CodeListVersions')), 1)
        self.assertEqual(mapping.element_by_name('CodeListVersions').local_name,
                         'CodeListVersions')


if __name__ == '__main__':
    unittest.main()
