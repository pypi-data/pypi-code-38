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
"""THIS FILE IS GENERATED FROM SEDA 2.0 XSD FILES, DO NOT EDIT"""

from cubicweb.entities import AnyEntity, fetch_config


class SEDAAnyEntity(AnyEntity):
    __abstract__ = True
    value_attr = None

    def dc_title(self):
        if self.value_attr is None:
            return self.dc_type()
        return self.printable_value(self.value_attr)


class SEDAArchiveTransfer(SEDAAnyEntity):
    __regid__ = 'SEDAArchiveTransfer'
    fetch_attrs, cw_fetch_order = fetch_config(['title', 'user_annotation'])
    value_attr = None

class SEDAComment(SEDAAnyEntity):
    __regid__ = 'SEDAComment'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality', 'comment', 'user_annotation'])
    value_attr = 'comment'

class SEDASignature(SEDAAnyEntity):
    __regid__ = 'SEDASignature'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDAArchivalAgreement(SEDAAnyEntity):
    __regid__ = 'SEDAArchivalAgreement'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality', 'archival_agreement', 'user_annotation'])
    value_attr = 'archival_agreement'

class SEDARelatedTransferReference(SEDAAnyEntity):
    __regid__ = 'SEDARelatedTransferReference'
    fetch_attrs, cw_fetch_order = fetch_config(['ordering', 'user_cardinality'])
    value_attr = None

class SEDATransferRequestReplyIdentifier(SEDAAnyEntity):
    __regid__ = 'SEDATransferRequestReplyIdentifier'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDAMessageDigestAlgorithmCodeListVersion(SEDAAnyEntity):
    __regid__ = 'SEDAMessageDigestAlgorithmCodeListVersion'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDAMimeTypeCodeListVersion(SEDAAnyEntity):
    __regid__ = 'SEDAMimeTypeCodeListVersion'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDAEncodingCodeListVersion(SEDAAnyEntity):
    __regid__ = 'SEDAEncodingCodeListVersion'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDAFileFormatCodeListVersion(SEDAAnyEntity):
    __regid__ = 'SEDAFileFormatCodeListVersion'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDACompressionAlgorithmCodeListVersion(SEDAAnyEntity):
    __regid__ = 'SEDACompressionAlgorithmCodeListVersion'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDADataObjectVersionCodeListVersion(SEDAAnyEntity):
    __regid__ = 'SEDADataObjectVersionCodeListVersion'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDAStorageRuleCodeListVersion(SEDAAnyEntity):
    __regid__ = 'SEDAStorageRuleCodeListVersion'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDAAppraisalRuleCodeListVersion(SEDAAnyEntity):
    __regid__ = 'SEDAAppraisalRuleCodeListVersion'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDAAccessRuleCodeListVersion(SEDAAnyEntity):
    __regid__ = 'SEDAAccessRuleCodeListVersion'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDADisseminationRuleCodeListVersion(SEDAAnyEntity):
    __regid__ = 'SEDADisseminationRuleCodeListVersion'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDAReuseRuleCodeListVersion(SEDAAnyEntity):
    __regid__ = 'SEDAReuseRuleCodeListVersion'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDAClassificationRuleCodeListVersion(SEDAAnyEntity):
    __regid__ = 'SEDAClassificationRuleCodeListVersion'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDAAcquisitionInformationCodeListVersion(SEDAAnyEntity):
    __regid__ = 'SEDAAcquisitionInformationCodeListVersion'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDARelationshipCodeListVersion(SEDAAnyEntity):
    __regid__ = 'SEDARelationshipCodeListVersion'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDABinaryDataObject(SEDAAnyEntity):
    __regid__ = 'SEDABinaryDataObject'
    fetch_attrs, cw_fetch_order = fetch_config(['ordering', 'filename', 'user_cardinality', 'user_annotation'])
    value_attr = None

class SEDAPhysicalDataObject(SEDAAnyEntity):
    __regid__ = 'SEDAPhysicalDataObject'
    fetch_attrs, cw_fetch_order = fetch_config(['ordering', 'user_cardinality', 'user_annotation'])
    value_attr = None

class SEDARelationship(SEDAAnyEntity):
    __regid__ = 'SEDARelationship'
    fetch_attrs, cw_fetch_order = fetch_config(['ordering', 'user_cardinality'])
    value_attr = None

class SEDADataObjectVersion(SEDAAnyEntity):
    __regid__ = 'SEDADataObjectVersion'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDAAltBinaryDataObjectAttachment(SEDAAnyEntity):
    __regid__ = 'SEDAAltBinaryDataObjectAttachment'
    fetch_attrs, cw_fetch_order = fetch_config([])
    value_attr = None

class SEDACompressed(SEDAAnyEntity):
    __regid__ = 'SEDACompressed'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality', 'compressed', 'user_annotation'])
    value_attr = 'compressed'

class SEDAArchiveUnit(SEDAAnyEntity):
    __regid__ = 'SEDAArchiveUnit'
    fetch_attrs, cw_fetch_order = fetch_config(['ordering', 'user_cardinality', 'user_annotation'])
    value_attr = None

class SEDAServiceLevel(SEDAAnyEntity):
    __regid__ = 'SEDAServiceLevel'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality', 'service_level', 'user_annotation'])
    value_attr = 'service_level'

class SEDAAcquisitionInformation(SEDAAnyEntity):
    __regid__ = 'SEDAAcquisitionInformation'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDALegalStatus(SEDAAnyEntity):
    __regid__ = 'SEDALegalStatus'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDAOriginatingAgencyIdentifier(SEDAAnyEntity):
    __regid__ = 'SEDAOriginatingAgencyIdentifier'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality', 'originating_agency_identifier', 'user_annotation'])
    value_attr = 'originating_agency_identifier'

class SEDASubmissionAgencyIdentifier(SEDAAnyEntity):
    __regid__ = 'SEDASubmissionAgencyIdentifier'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality', 'submission_agency_identifier', 'user_annotation'])
    value_attr = 'submission_agency_identifier'

class SEDAStorageRule(SEDAAnyEntity):
    __regid__ = 'SEDAStorageRule'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDAAppraisalRule(SEDAAnyEntity):
    __regid__ = 'SEDAAppraisalRule'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDAAccessRule(SEDAAnyEntity):
    __regid__ = 'SEDAAccessRule'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDADisseminationRule(SEDAAnyEntity):
    __regid__ = 'SEDADisseminationRule'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDAReuseRule(SEDAAnyEntity):
    __regid__ = 'SEDAReuseRule'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDAClassificationRule(SEDAAnyEntity):
    __regid__ = 'SEDAClassificationRule'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality', 'classification_owner', 'user_annotation'])
    value_attr = 'classification_owner'

class SEDANeedAuthorization(SEDAAnyEntity):
    __regid__ = 'SEDANeedAuthorization'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality', 'need_authorization', 'user_annotation'])
    value_attr = 'need_authorization'

class SEDAAltArchiveUnitArchiveUnitRefId(SEDAAnyEntity):
    __regid__ = 'SEDAAltArchiveUnitArchiveUnitRefId'
    fetch_attrs, cw_fetch_order = fetch_config([])
    value_attr = None

class SEDAAttachment(SEDAAnyEntity):
    __regid__ = 'SEDAAttachment'
    fetch_attrs, cw_fetch_order = fetch_config([])
    value_attr = None

class SEDAUri(SEDAAnyEntity):
    __regid__ = 'SEDAUri'
    fetch_attrs, cw_fetch_order = fetch_config([])
    value_attr = None

class SEDAFormatLitteral(SEDAAnyEntity):
    __regid__ = 'SEDAFormatLitteral'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality', 'format_litteral', 'user_annotation'])
    value_attr = 'format_litteral'

class SEDAMimeType(SEDAAnyEntity):
    __regid__ = 'SEDAMimeType'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDAFormatId(SEDAAnyEntity):
    __regid__ = 'SEDAFormatId'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDAEncoding(SEDAAnyEntity):
    __regid__ = 'SEDAEncoding'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDACreatingApplicationName(SEDAAnyEntity):
    __regid__ = 'SEDACreatingApplicationName'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality', 'creating_application_name', 'user_annotation'])
    value_attr = 'creating_application_name'

class SEDACreatingApplicationVersion(SEDAAnyEntity):
    __regid__ = 'SEDACreatingApplicationVersion'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality', 'creating_application_version', 'user_annotation'])
    value_attr = 'creating_application_version'

class SEDADateCreatedByApplication(SEDAAnyEntity):
    __regid__ = 'SEDADateCreatedByApplication'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDACreatingOs(SEDAAnyEntity):
    __regid__ = 'SEDACreatingOs'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality', 'creating_os', 'user_annotation'])
    value_attr = 'creating_os'

class SEDACreatingOsVersion(SEDAAnyEntity):
    __regid__ = 'SEDACreatingOsVersion'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality', 'creating_os_version', 'user_annotation'])
    value_attr = 'creating_os_version'

class SEDALastModified(SEDAAnyEntity):
    __regid__ = 'SEDALastModified'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDAWidth(SEDAAnyEntity):
    __regid__ = 'SEDAWidth'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDAHeight(SEDAAnyEntity):
    __regid__ = 'SEDAHeight'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDADepth(SEDAAnyEntity):
    __regid__ = 'SEDADepth'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDAShape(SEDAAnyEntity):
    __regid__ = 'SEDAShape'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDADiameter(SEDAAnyEntity):
    __regid__ = 'SEDADiameter'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDALength(SEDAAnyEntity):
    __regid__ = 'SEDALength'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDAThickness(SEDAAnyEntity):
    __regid__ = 'SEDAThickness'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDAWeight(SEDAAnyEntity):
    __regid__ = 'SEDAWeight'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDANumberOfPage(SEDAAnyEntity):
    __regid__ = 'SEDANumberOfPage'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDAArchiveUnitRefId(SEDAAnyEntity):
    __regid__ = 'SEDAArchiveUnitRefId'
    fetch_attrs, cw_fetch_order = fetch_config([])
    value_attr = None

class SEDASeqAltArchiveUnitArchiveUnitRefIdManagement(SEDAAnyEntity):
    __regid__ = 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'
    fetch_attrs, cw_fetch_order = fetch_config([])
    value_attr = None

class SEDASeqStorageRuleRule(SEDAAnyEntity):
    __regid__ = 'SEDASeqStorageRuleRule'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDAAltStorageRulePreventInheritance(SEDAAnyEntity):
    __regid__ = 'SEDAAltStorageRulePreventInheritance'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDASeqAppraisalRuleRule(SEDAAnyEntity):
    __regid__ = 'SEDASeqAppraisalRuleRule'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDAAltAppraisalRulePreventInheritance(SEDAAnyEntity):
    __regid__ = 'SEDAAltAppraisalRulePreventInheritance'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDASeqAccessRuleRule(SEDAAnyEntity):
    __regid__ = 'SEDASeqAccessRuleRule'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDAAltAccessRulePreventInheritance(SEDAAnyEntity):
    __regid__ = 'SEDAAltAccessRulePreventInheritance'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDASeqDisseminationRuleRule(SEDAAnyEntity):
    __regid__ = 'SEDASeqDisseminationRuleRule'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDAAltDisseminationRulePreventInheritance(SEDAAnyEntity):
    __regid__ = 'SEDAAltDisseminationRulePreventInheritance'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDASeqReuseRuleRule(SEDAAnyEntity):
    __regid__ = 'SEDASeqReuseRuleRule'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDAAltReuseRulePreventInheritance(SEDAAnyEntity):
    __regid__ = 'SEDAAltReuseRulePreventInheritance'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDASeqClassificationRuleRule(SEDAAnyEntity):
    __regid__ = 'SEDASeqClassificationRuleRule'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDAAltClassificationRulePreventInheritance(SEDAAnyEntity):
    __regid__ = 'SEDAAltClassificationRulePreventInheritance'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDAClassificationReassessingDate(SEDAAnyEntity):
    __regid__ = 'SEDAClassificationReassessingDate'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDANeedReassessingAuthorization(SEDAAnyEntity):
    __regid__ = 'SEDANeedReassessingAuthorization'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality', 'need_reassessing_authorization', 'user_annotation'])
    value_attr = 'need_reassessing_authorization'

class SEDADataObjectReference(SEDAAnyEntity):
    __regid__ = 'SEDADataObjectReference'
    fetch_attrs, cw_fetch_order = fetch_config(['ordering', 'user_cardinality'])
    value_attr = None

class SEDATitle(SEDAAnyEntity):
    __regid__ = 'SEDATitle'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality', 'title', 'user_annotation'])
    value_attr = 'title'

class SEDAFilePlanPosition(SEDAAnyEntity):
    __regid__ = 'SEDAFilePlanPosition'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality', 'file_plan_position', 'user_annotation'])
    value_attr = 'file_plan_position'

class SEDASystemId(SEDAAnyEntity):
    __regid__ = 'SEDASystemId'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDAOriginatingSystemId(SEDAAnyEntity):
    __regid__ = 'SEDAOriginatingSystemId'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDAArchivalAgencyArchiveUnitIdentifier(SEDAAnyEntity):
    __regid__ = 'SEDAArchivalAgencyArchiveUnitIdentifier'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality', 'archival_agency_archive_unit_identifier', 'user_annotation'])
    value_attr = 'archival_agency_archive_unit_identifier'

class SEDAOriginatingAgencyArchiveUnitIdentifier(SEDAAnyEntity):
    __regid__ = 'SEDAOriginatingAgencyArchiveUnitIdentifier'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality', 'originating_agency_archive_unit_identifier', 'user_annotation'])
    value_attr = 'originating_agency_archive_unit_identifier'

class SEDATransferringAgencyArchiveUnitIdentifier(SEDAAnyEntity):
    __regid__ = 'SEDATransferringAgencyArchiveUnitIdentifier'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality', 'transferring_agency_archive_unit_identifier', 'user_annotation'])
    value_attr = 'transferring_agency_archive_unit_identifier'

class SEDADescription(SEDAAnyEntity):
    __regid__ = 'SEDADescription'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality', 'description', 'user_annotation'])
    value_attr = 'description'

class SEDAType(SEDAAnyEntity):
    __regid__ = 'SEDAType'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDADocumentType(SEDAAnyEntity):
    __regid__ = 'SEDADocumentType'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality', 'document_type', 'user_annotation'])
    value_attr = 'document_type'

class SEDALanguage(SEDAAnyEntity):
    __regid__ = 'SEDALanguage'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDADescriptionLanguage(SEDAAnyEntity):
    __regid__ = 'SEDADescriptionLanguage'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDAStatus(SEDAAnyEntity):
    __regid__ = 'SEDAStatus'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality', 'status', 'user_annotation'])
    value_attr = 'status'

class SEDAVersion(SEDAAnyEntity):
    __regid__ = 'SEDAVersion'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality', 'version', 'user_annotation'])
    value_attr = 'version'

class SEDATag(SEDAAnyEntity):
    __regid__ = 'SEDATag'
    fetch_attrs, cw_fetch_order = fetch_config(['ordering', 'user_cardinality', 'tag', 'user_annotation'])
    value_attr = 'tag'

class SEDAKeyword(SEDAAnyEntity):
    __regid__ = 'SEDAKeyword'
    fetch_attrs, cw_fetch_order = fetch_config(['ordering', 'user_cardinality', 'keyword_content', 'user_annotation'])
    value_attr = 'keyword_content'

class SEDAOriginatingAgency(SEDAAnyEntity):
    __regid__ = 'SEDAOriginatingAgency'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDASubmissionAgency(SEDAAnyEntity):
    __regid__ = 'SEDASubmissionAgency'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDAAuthorizedAgent(SEDAAnyEntity):
    __regid__ = 'SEDAAuthorizedAgent'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDAWriter(SEDAAnyEntity):
    __regid__ = 'SEDAWriter'
    fetch_attrs, cw_fetch_order = fetch_config(['ordering', 'user_cardinality'])
    value_attr = None

class SEDAAddressee(SEDAAnyEntity):
    __regid__ = 'SEDAAddressee'
    fetch_attrs, cw_fetch_order = fetch_config(['ordering', 'user_cardinality'])
    value_attr = None

class SEDARecipient(SEDAAnyEntity):
    __regid__ = 'SEDARecipient'
    fetch_attrs, cw_fetch_order = fetch_config(['ordering', 'user_cardinality'])
    value_attr = None

class SEDASource(SEDAAnyEntity):
    __regid__ = 'SEDASource'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality', 'source', 'user_annotation'])
    value_attr = 'source'

class SEDACreatedDate(SEDAAnyEntity):
    __regid__ = 'SEDACreatedDate'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDATransactedDate(SEDAAnyEntity):
    __regid__ = 'SEDATransactedDate'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDAAcquiredDate(SEDAAnyEntity):
    __regid__ = 'SEDAAcquiredDate'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDASentDate(SEDAAnyEntity):
    __regid__ = 'SEDASentDate'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDAReceivedDate(SEDAAnyEntity):
    __regid__ = 'SEDAReceivedDate'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDARegisteredDate(SEDAAnyEntity):
    __regid__ = 'SEDARegisteredDate'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDAStartDate(SEDAAnyEntity):
    __regid__ = 'SEDAStartDate'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDAEndDate(SEDAAnyEntity):
    __regid__ = 'SEDAEndDate'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDAEvent(SEDAAnyEntity):
    __regid__ = 'SEDAEvent'
    fetch_attrs, cw_fetch_order = fetch_config(['ordering', 'user_cardinality'])
    value_attr = None

class SEDAPreventInheritance(SEDAAnyEntity):
    __regid__ = 'SEDAPreventInheritance'
    fetch_attrs, cw_fetch_order = fetch_config(['prevent_inheritance'])
    value_attr = 'prevent_inheritance'

class SEDARefNonRuleId(SEDAAnyEntity):
    __regid__ = 'SEDARefNonRuleId'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDACustodialHistoryItem(SEDAAnyEntity):
    __regid__ = 'SEDACustodialHistoryItem'
    fetch_attrs, cw_fetch_order = fetch_config(['ordering', 'user_cardinality', 'custodial_history_item', 'user_annotation'])
    value_attr = 'custodial_history_item'

class SEDACustodialHistoryFile(SEDAAnyEntity):
    __regid__ = 'SEDACustodialHistoryFile'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDAKeywordReference(SEDAAnyEntity):
    __regid__ = 'SEDAKeywordReference'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDAKeywordType(SEDAAnyEntity):
    __regid__ = 'SEDAKeywordType'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDASpatial(SEDAAnyEntity):
    __regid__ = 'SEDASpatial'
    fetch_attrs, cw_fetch_order = fetch_config(['ordering', 'user_cardinality', 'spatial', 'user_annotation'])
    value_attr = 'spatial'

class SEDATemporal(SEDAAnyEntity):
    __regid__ = 'SEDATemporal'
    fetch_attrs, cw_fetch_order = fetch_config(['ordering', 'user_cardinality', 'temporal', 'user_annotation'])
    value_attr = 'temporal'

class SEDAJuridictional(SEDAAnyEntity):
    __regid__ = 'SEDAJuridictional'
    fetch_attrs, cw_fetch_order = fetch_config(['ordering', 'user_cardinality', 'juridictional', 'user_annotation'])
    value_attr = 'juridictional'

class SEDAIsVersionOf(SEDAAnyEntity):
    __regid__ = 'SEDAIsVersionOf'
    fetch_attrs, cw_fetch_order = fetch_config(['ordering', 'user_cardinality'])
    value_attr = None

class SEDAReplaces(SEDAAnyEntity):
    __regid__ = 'SEDAReplaces'
    fetch_attrs, cw_fetch_order = fetch_config(['ordering', 'user_cardinality'])
    value_attr = None

class SEDARequires(SEDAAnyEntity):
    __regid__ = 'SEDARequires'
    fetch_attrs, cw_fetch_order = fetch_config(['ordering', 'user_cardinality'])
    value_attr = None

class SEDAIsPartOf(SEDAAnyEntity):
    __regid__ = 'SEDAIsPartOf'
    fetch_attrs, cw_fetch_order = fetch_config(['ordering', 'user_cardinality'])
    value_attr = None

class SEDAReferences(SEDAAnyEntity):
    __regid__ = 'SEDAReferences'
    fetch_attrs, cw_fetch_order = fetch_config(['ordering', 'user_cardinality'])
    value_attr = None

class SEDAEventIdentifier(SEDAAnyEntity):
    __regid__ = 'SEDAEventIdentifier'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDAEventType(SEDAAnyEntity):
    __regid__ = 'SEDAEventType'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDAEventDetail(SEDAAnyEntity):
    __regid__ = 'SEDAEventDetail'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDAGpsVersionID(SEDAAnyEntity):
    __regid__ = 'SEDAGpsVersionID'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDAGpsAltitude(SEDAAnyEntity):
    __regid__ = 'SEDAGpsAltitude'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDAGpsAltitudeRef(SEDAAnyEntity):
    __regid__ = 'SEDAGpsAltitudeRef'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDAGpsLatitude(SEDAAnyEntity):
    __regid__ = 'SEDAGpsLatitude'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDAGpsLatitudeRef(SEDAAnyEntity):
    __regid__ = 'SEDAGpsLatitudeRef'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDAGpsLongitude(SEDAAnyEntity):
    __regid__ = 'SEDAGpsLongitude'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDAGpsLongitudeRef(SEDAAnyEntity):
    __regid__ = 'SEDAGpsLongitudeRef'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDAGpsDateStamp(SEDAAnyEntity):
    __regid__ = 'SEDAGpsDateStamp'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDAwhen(SEDAAnyEntity):
    __regid__ = 'SEDAwhen'
    fetch_attrs, cw_fetch_order = fetch_config(['user_cardinality'])
    value_attr = None

class SEDAAltIsVersionOfArchiveUnitRefId(SEDAAnyEntity):
    __regid__ = 'SEDAAltIsVersionOfArchiveUnitRefId'
    fetch_attrs, cw_fetch_order = fetch_config([])
    value_attr = None

class SEDAAltReplacesArchiveUnitRefId(SEDAAnyEntity):
    __regid__ = 'SEDAAltReplacesArchiveUnitRefId'
    fetch_attrs, cw_fetch_order = fetch_config([])
    value_attr = None

class SEDAAltRequiresArchiveUnitRefId(SEDAAnyEntity):
    __regid__ = 'SEDAAltRequiresArchiveUnitRefId'
    fetch_attrs, cw_fetch_order = fetch_config([])
    value_attr = None

class SEDAAltIsPartOfArchiveUnitRefId(SEDAAnyEntity):
    __regid__ = 'SEDAAltIsPartOfArchiveUnitRefId'
    fetch_attrs, cw_fetch_order = fetch_config([])
    value_attr = None

class SEDAAltReferencesArchiveUnitRefId(SEDAAnyEntity):
    __regid__ = 'SEDAAltReferencesArchiveUnitRefId'
    fetch_attrs, cw_fetch_order = fetch_config([])
    value_attr = None

class SEDARepositoryArchiveUnitPID(SEDAAnyEntity):
    __regid__ = 'SEDARepositoryArchiveUnitPID'
    fetch_attrs, cw_fetch_order = fetch_config([])
    value_attr = None

class SEDARepositoryObjectPID(SEDAAnyEntity):
    __regid__ = 'SEDARepositoryObjectPID'
    fetch_attrs, cw_fetch_order = fetch_config([])
    value_attr = None

CHOICE_RTYPE = {
  'SEDAAltAccessRulePreventInheritance': [
    [
      'seda_prevent_inheritance',
      'object'
    ],
    [
      'seda_ref_non_rule_id_from',
      'object'
    ]
  ],
  'SEDAAltAppraisalRulePreventInheritance': [
    [
      'seda_prevent_inheritance',
      'object'
    ],
    [
      'seda_ref_non_rule_id_from',
      'object'
    ]
  ],
  'SEDAAltArchiveUnitArchiveUnitRefId': [
    [
      'seda_archive_unit_ref_id_from',
      'object'
    ],
    [
      'seda_seq_alt_archive_unit_archive_unit_ref_id_management',
      'subject'
    ]
  ],
  'SEDAAltBinaryDataObjectAttachment': [
    [
      'seda_attachment',
      'object'
    ],
    [
      'seda_uri',
      'object'
    ]
  ],
  'SEDAAltClassificationRulePreventInheritance': [
    [
      'seda_prevent_inheritance',
      'object'
    ],
    [
      'seda_ref_non_rule_id_from',
      'object'
    ]
  ],
  'SEDAAltDisseminationRulePreventInheritance': [
    [
      'seda_prevent_inheritance',
      'object'
    ],
    [
      'seda_ref_non_rule_id_from',
      'object'
    ]
  ],
  'SEDAAltIsPartOfArchiveUnitRefId': [
    [
      'seda_archive_unit_ref_id_from',
      'object'
    ],
    [
      'seda_repository_archive_unit_pid',
      'object'
    ],
    [
      'seda_repository_object_pid',
      'object'
    ],
    [
      'seda_data_object_reference',
      'object'
    ]
  ],
  'SEDAAltIsVersionOfArchiveUnitRefId': [
    [
      'seda_archive_unit_ref_id_from',
      'object'
    ],
    [
      'seda_data_object_reference',
      'object'
    ],
    [
      'seda_repository_archive_unit_pid',
      'object'
    ],
    [
      'seda_repository_object_pid',
      'object'
    ]
  ],
  'SEDAAltReferencesArchiveUnitRefId': [
    [
      'seda_archive_unit_ref_id_from',
      'object'
    ],
    [
      'seda_repository_archive_unit_pid',
      'object'
    ],
    [
      'seda_repository_object_pid',
      'object'
    ],
    [
      'seda_data_object_reference',
      'object'
    ]
  ],
  'SEDAAltReplacesArchiveUnitRefId': [
    [
      'seda_archive_unit_ref_id_from',
      'object'
    ],
    [
      'seda_repository_archive_unit_pid',
      'object'
    ],
    [
      'seda_repository_object_pid',
      'object'
    ],
    [
      'seda_data_object_reference',
      'object'
    ]
  ],
  'SEDAAltRequiresArchiveUnitRefId': [
    [
      'seda_archive_unit_ref_id_from',
      'object'
    ],
    [
      'seda_repository_archive_unit_pid',
      'object'
    ],
    [
      'seda_repository_object_pid',
      'object'
    ],
    [
      'seda_data_object_reference',
      'object'
    ]
  ],
  'SEDAAltReuseRulePreventInheritance': [
    [
      'seda_prevent_inheritance',
      'object'
    ],
    [
      'seda_ref_non_rule_id_from',
      'object'
    ]
  ],
  'SEDAAltStorageRulePreventInheritance': [
    [
      'seda_prevent_inheritance',
      'object'
    ],
    [
      'seda_ref_non_rule_id_from',
      'object'
    ]
  ]
}
CHECK_CARD_ETYPES = [
  'SEDAAddressee',
  'SEDAArchiveUnit',
  'SEDABinaryDataObject',
  'SEDACustodialHistoryItem',
  'SEDADataObjectReference',
  'SEDAEvent',
  'SEDAIsPartOf',
  'SEDAIsVersionOf',
  'SEDAJuridictional',
  'SEDAKeyword',
  'SEDAPhysicalDataObject',
  'SEDARecipient',
  'SEDARefNonRuleId',
  'SEDAReferences',
  'SEDARelatedTransferReference',
  'SEDARelationship',
  'SEDAReplaces',
  'SEDARequires',
  'SEDASpatial',
  'SEDATag',
  'SEDATemporal',
  'SEDAWriter'
]
CHECK_CHILDREN_CARD_RTYPES = [
  'seda_addressee_from',
  'seda_archive_unit',
  'seda_binary_data_object',
  'seda_custodial_history_item',
  'seda_data_object_reference',
  'seda_event',
  'seda_is_part_of',
  'seda_is_version_of',
  'seda_juridictional',
  'seda_keyword',
  'seda_physical_data_object',
  'seda_recipient_from',
  'seda_ref_non_rule_id_from',
  'seda_references',
  'seda_related_transfer_reference',
  'seda_relationship',
  'seda_replaces',
  'seda_requires',
  'seda_spatial',
  'seda_tag',
  'seda_temporal',
  'seda_writer_from'
]
