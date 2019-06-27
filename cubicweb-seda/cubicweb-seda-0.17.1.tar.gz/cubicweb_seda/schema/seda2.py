# XXX unsupported merge because of incompatible cardinality SEDADataObjectVersion seda_data_object_version_to Concept ? <SEDADataObjectVersion seda_data_object_version_to set(['Concept'])> ?*
# XXX unsupported merge because of incompatible cardinality SEDAArchiveUnitRefId seda_archive_unit_ref_id_to SEDAArchiveUnit ? <SEDAArchiveUnitRefId seda_archive_unit_ref_id_to set(['SEDAArchiveUnit'])> ?*
# XXX unsupported merge because of incompatible cardinality SEDAArchiveUnitRefId seda_archive_unit_ref_id_to SEDAArchiveUnit ? <SEDAArchiveUnitRefId seda_archive_unit_ref_id_to set(['SEDAArchiveUnit'])> ?*
# XXX unsupported merge because of incompatible cardinality SEDAArchiveUnitRefId seda_archive_unit_ref_id_to SEDAArchiveUnit ? <SEDAArchiveUnitRefId seda_archive_unit_ref_id_to set(['SEDAArchiveUnit'])> ?*
# XXX unsupported merge because of incompatible cardinality SEDAArchiveUnitRefId seda_archive_unit_ref_id_to SEDAArchiveUnit ? <SEDAArchiveUnitRefId seda_archive_unit_ref_id_to set(['SEDAArchiveUnit'])> ?*
# XXX unsupported merge because of incompatible cardinality SEDAArchiveUnitRefId seda_archive_unit_ref_id_to SEDAArchiveUnit ? <SEDAArchiveUnitRefId seda_archive_unit_ref_id_to set(['SEDAArchiveUnit'])> ?*
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

from yams.buildobjs import EntityType, RelationDefinition
from yams.buildobjs import String, Boolean
from cubicweb.schema import RQLConstraint
from cubicweb_seda.schema import seda_profile_element


@seda_profile_element()
class SEDAArchiveTransfer(EntityType):
    u""""""


@seda_profile_element(cardinalities=['0..1', '0..n', '1', '1..n'], default_cardinality='1',
                      annotable=True)
class SEDAComment(EntityType):
    u""""""
    comment = String(fulltextindexed=True)


class archive_transfer_comment(RelationDefinition):
    name = 'seda_comment'
    subject = 'SEDAComment'
    object = 'SEDAArchiveTransfer'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDASignature(EntityType):
    u""""""


class archive_transfer_signature(RelationDefinition):
    name = 'seda_signature'
    subject = 'SEDASignature'
    object = 'SEDAArchiveTransfer'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDAArchivalAgreement(EntityType):
    u""""""
    archival_agreement = String(fulltextindexed=True)


class archive_transfer_archival_agreement(RelationDefinition):
    name = 'seda_archival_agreement'
    subject = 'SEDAArchivalAgreement'
    object = 'SEDAArchiveTransfer'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '0..n', '1', '1..n'], default_cardinality='1',
                      annotable=True)
class SEDARelatedTransferReference(EntityType):
    u""""""


class archive_transfer_related_transfer_reference(RelationDefinition):
    name = 'seda_related_transfer_reference'
    subject = 'SEDARelatedTransferReference'
    object = 'SEDAArchiveTransfer'
    cardinality = '1*'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDATransferRequestReplyIdentifier(EntityType):
    u""""""


class archive_transfer_transfer_request_reply_identifier(RelationDefinition):
    name = 'seda_transfer_request_reply_identifier'
    subject = 'SEDATransferRequestReplyIdentifier'
    object = 'SEDAArchiveTransfer'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

class archive_transfer_archival_agency(RelationDefinition):
    name = 'seda_archival_agency'
    subject = 'SEDAArchiveTransfer'
    object = 'AuthorityRecord'
    cardinality = '?*'
    composite = fulltext_container = None
    inlined = True
    constraints = []

class archive_transfer_transferring_agency(RelationDefinition):
    name = 'seda_transferring_agency'
    subject = 'SEDAArchiveTransfer'
    object = 'AuthorityRecord'
    cardinality = '?*'
    composite = fulltext_container = None
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDAMessageDigestAlgorithmCodeListVersion(EntityType):
    u""""""


class archive_transfer_message_digest_algorithm_code_list_version_from(RelationDefinition):
    name = 'seda_message_digest_algorithm_code_list_version_from'
    subject = 'SEDAMessageDigestAlgorithmCodeListVersion'
    object = 'SEDAArchiveTransfer'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

class message_digest_algorithm_code_list_version_message_digest_algorithm_code_list_version_to(RelationDefinition):
    name = 'seda_message_digest_algorithm_code_list_version_to'
    subject = 'SEDAMessageDigestAlgorithmCodeListVersion'
    object = 'ConceptScheme'
    cardinality = '?*'
    composite = fulltext_container = None
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDAMimeTypeCodeListVersion(EntityType):
    u""""""


class archive_transfer_mime_type_code_list_version_from(RelationDefinition):
    name = 'seda_mime_type_code_list_version_from'
    subject = 'SEDAMimeTypeCodeListVersion'
    object = 'SEDAArchiveTransfer'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

class mime_type_code_list_version_mime_type_code_list_version_to(RelationDefinition):
    name = 'seda_mime_type_code_list_version_to'
    subject = 'SEDAMimeTypeCodeListVersion'
    object = 'ConceptScheme'
    cardinality = '?*'
    composite = fulltext_container = None
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDAEncodingCodeListVersion(EntityType):
    u""""""


class archive_transfer_encoding_code_list_version_from(RelationDefinition):
    name = 'seda_encoding_code_list_version_from'
    subject = 'SEDAEncodingCodeListVersion'
    object = 'SEDAArchiveTransfer'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

class encoding_code_list_version_encoding_code_list_version_to(RelationDefinition):
    name = 'seda_encoding_code_list_version_to'
    subject = 'SEDAEncodingCodeListVersion'
    object = 'ConceptScheme'
    cardinality = '?*'
    composite = fulltext_container = None
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDAFileFormatCodeListVersion(EntityType):
    u""""""


class archive_transfer_file_format_code_list_version_from(RelationDefinition):
    name = 'seda_file_format_code_list_version_from'
    subject = 'SEDAFileFormatCodeListVersion'
    object = 'SEDAArchiveTransfer'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

class file_format_code_list_version_file_format_code_list_version_to(RelationDefinition):
    name = 'seda_file_format_code_list_version_to'
    subject = 'SEDAFileFormatCodeListVersion'
    object = 'ConceptScheme'
    cardinality = '?*'
    composite = fulltext_container = None
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDACompressionAlgorithmCodeListVersion(EntityType):
    u""""""


class archive_transfer_compression_algorithm_code_list_version_from(RelationDefinition):
    name = 'seda_compression_algorithm_code_list_version_from'
    subject = 'SEDACompressionAlgorithmCodeListVersion'
    object = 'SEDAArchiveTransfer'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

class compression_algorithm_code_list_version_compression_algorithm_code_list_version_to(RelationDefinition):
    name = 'seda_compression_algorithm_code_list_version_to'
    subject = 'SEDACompressionAlgorithmCodeListVersion'
    object = 'ConceptScheme'
    cardinality = '?*'
    composite = fulltext_container = None
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDADataObjectVersionCodeListVersion(EntityType):
    u""""""


class archive_transfer_data_object_version_code_list_version_from(RelationDefinition):
    name = 'seda_data_object_version_code_list_version_from'
    subject = 'SEDADataObjectVersionCodeListVersion'
    object = 'SEDAArchiveTransfer'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

class data_object_version_code_list_version_data_object_version_code_list_version_to(RelationDefinition):
    name = 'seda_data_object_version_code_list_version_to'
    subject = 'SEDADataObjectVersionCodeListVersion'
    object = 'ConceptScheme'
    cardinality = '?*'
    composite = fulltext_container = None
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDAStorageRuleCodeListVersion(EntityType):
    u""""""


class archive_transfer_storage_rule_code_list_version_from(RelationDefinition):
    name = 'seda_storage_rule_code_list_version_from'
    subject = 'SEDAStorageRuleCodeListVersion'
    object = 'SEDAArchiveTransfer'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

class storage_rule_code_list_version_storage_rule_code_list_version_to(RelationDefinition):
    name = 'seda_storage_rule_code_list_version_to'
    subject = 'SEDAStorageRuleCodeListVersion'
    object = 'ConceptScheme'
    cardinality = '?*'
    composite = fulltext_container = None
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDAAppraisalRuleCodeListVersion(EntityType):
    u""""""


class archive_transfer_appraisal_rule_code_list_version_from(RelationDefinition):
    name = 'seda_appraisal_rule_code_list_version_from'
    subject = 'SEDAAppraisalRuleCodeListVersion'
    object = 'SEDAArchiveTransfer'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

class appraisal_rule_code_list_version_appraisal_rule_code_list_version_to(RelationDefinition):
    name = 'seda_appraisal_rule_code_list_version_to'
    subject = 'SEDAAppraisalRuleCodeListVersion'
    object = 'ConceptScheme'
    cardinality = '?*'
    composite = fulltext_container = None
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDAAccessRuleCodeListVersion(EntityType):
    u""""""


class archive_transfer_access_rule_code_list_version_from(RelationDefinition):
    name = 'seda_access_rule_code_list_version_from'
    subject = 'SEDAAccessRuleCodeListVersion'
    object = 'SEDAArchiveTransfer'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

class access_rule_code_list_version_access_rule_code_list_version_to(RelationDefinition):
    name = 'seda_access_rule_code_list_version_to'
    subject = 'SEDAAccessRuleCodeListVersion'
    object = 'ConceptScheme'
    cardinality = '?*'
    composite = fulltext_container = None
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDADisseminationRuleCodeListVersion(EntityType):
    u""""""


class archive_transfer_dissemination_rule_code_list_version_from(RelationDefinition):
    name = 'seda_dissemination_rule_code_list_version_from'
    subject = 'SEDADisseminationRuleCodeListVersion'
    object = 'SEDAArchiveTransfer'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

class dissemination_rule_code_list_version_dissemination_rule_code_list_version_to(RelationDefinition):
    name = 'seda_dissemination_rule_code_list_version_to'
    subject = 'SEDADisseminationRuleCodeListVersion'
    object = 'ConceptScheme'
    cardinality = '?*'
    composite = fulltext_container = None
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDAReuseRuleCodeListVersion(EntityType):
    u""""""


class archive_transfer_reuse_rule_code_list_version_from(RelationDefinition):
    name = 'seda_reuse_rule_code_list_version_from'
    subject = 'SEDAReuseRuleCodeListVersion'
    object = 'SEDAArchiveTransfer'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

class reuse_rule_code_list_version_reuse_rule_code_list_version_to(RelationDefinition):
    name = 'seda_reuse_rule_code_list_version_to'
    subject = 'SEDAReuseRuleCodeListVersion'
    object = 'ConceptScheme'
    cardinality = '?*'
    composite = fulltext_container = None
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDAClassificationRuleCodeListVersion(EntityType):
    u""""""


class archive_transfer_classification_rule_code_list_version_from(RelationDefinition):
    name = 'seda_classification_rule_code_list_version_from'
    subject = 'SEDAClassificationRuleCodeListVersion'
    object = 'SEDAArchiveTransfer'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

class classification_rule_code_list_version_classification_rule_code_list_version_to(RelationDefinition):
    name = 'seda_classification_rule_code_list_version_to'
    subject = 'SEDAClassificationRuleCodeListVersion'
    object = 'ConceptScheme'
    cardinality = '?*'
    composite = fulltext_container = None
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDAAcquisitionInformationCodeListVersion(EntityType):
    u""""""


class archive_transfer_acquisition_information_code_list_version_from(RelationDefinition):
    name = 'seda_acquisition_information_code_list_version_from'
    subject = 'SEDAAcquisitionInformationCodeListVersion'
    object = 'SEDAArchiveTransfer'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

class acquisition_information_code_list_version_acquisition_information_code_list_version_to(RelationDefinition):
    name = 'seda_acquisition_information_code_list_version_to'
    subject = 'SEDAAcquisitionInformationCodeListVersion'
    object = 'ConceptScheme'
    cardinality = '?*'
    composite = fulltext_container = None
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDARelationshipCodeListVersion(EntityType):
    u""""""


class archive_transfer_relationship_code_list_version_from(RelationDefinition):
    name = 'seda_relationship_code_list_version_from'
    subject = 'SEDARelationshipCodeListVersion'
    object = 'SEDAArchiveTransfer'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

class relationship_code_list_version_relationship_code_list_version_to(RelationDefinition):
    name = 'seda_relationship_code_list_version_to'
    subject = 'SEDARelationshipCodeListVersion'
    object = 'ConceptScheme'
    cardinality = '?*'
    composite = fulltext_container = None
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '0..n', '1', '1..n'], default_cardinality='1',
                      annotable=True)
class SEDABinaryDataObject(EntityType):
    u""""""
    filename = String(fulltextindexed=True)


class archive_transfer_binary_data_object(RelationDefinition):
    name = 'seda_binary_data_object'
    subject = 'SEDABinaryDataObject'
    object = 'SEDAArchiveTransfer'
    cardinality = '?*'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '0..n', '1', '1..n'], default_cardinality='1',
                      annotable=True)
class SEDAPhysicalDataObject(EntityType):
    u""""""


class archive_transfer_physical_data_object(RelationDefinition):
    name = 'seda_physical_data_object'
    subject = 'SEDAPhysicalDataObject'
    object = 'SEDAArchiveTransfer'
    cardinality = '?*'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '0..n', '1', '1..n'], default_cardinality='1',
                      annotable=True)
class SEDARelationship(EntityType):
    u""""""


class binary_data_object_relationship(RelationDefinition):
    name = 'seda_relationship'
    subject = 'SEDARelationship'
    object = 'SEDABinaryDataObject'
    cardinality = '1*'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDADataObjectVersion(EntityType):
    u""""""


class binary_data_object_data_object_version_from(RelationDefinition):
    name = 'seda_data_object_version_from'
    subject = 'SEDADataObjectVersion'
    object = ('SEDABinaryDataObject', 'SEDAPhysicalDataObject')
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

class data_object_version_data_object_version_to(RelationDefinition):
    name = 'seda_data_object_version_to'
    subject = 'SEDADataObjectVersion'
    object = 'Concept'
    cardinality = '?*'
    composite = fulltext_container = None
    inlined = True
    constraints = [RQLConstraint('O in_scheme CS, CACLV seda_data_object_version_code_list_version_from AT, CACLV seda_data_object_version_code_list_version_to CS,S container AT')]

@seda_profile_element(cardinalities=['1'], default_cardinality='1',
                      annotable=False)
class SEDAAltBinaryDataObjectAttachment(EntityType):
    u""""""


class binary_data_object_alt_binary_data_object_attachment(RelationDefinition):
    name = 'seda_alt_binary_data_object_attachment'
    subject = 'SEDABinaryDataObject'
    object = 'SEDAAltBinaryDataObjectAttachment'
    cardinality = '11'
    composite = fulltext_container = 'subject'
    inlined = False
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDACompressed(EntityType):
    u""""""
    compressed = Boolean()


class binary_data_object_compressed(RelationDefinition):
    name = 'seda_compressed'
    subject = 'SEDACompressed'
    object = 'SEDABinaryDataObject'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

class physical_data_object_relationship(RelationDefinition):
    name = 'seda_relationship'
    subject = 'SEDARelationship'
    object = 'SEDAPhysicalDataObject'
    cardinality = '1*'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '0..n', '1', '1..n'], default_cardinality='1',
                      annotable=True)
class SEDAArchiveUnit(EntityType):
    u""""""


class archive_transfer_archive_unit(RelationDefinition):
    name = 'seda_archive_unit'
    subject = 'SEDAArchiveUnit'
    object = 'SEDAArchiveTransfer'
    cardinality = '?*'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDAServiceLevel(EntityType):
    u""""""
    service_level = String(fulltextindexed=True)


class archive_transfer_service_level(RelationDefinition):
    name = 'seda_service_level'
    subject = 'SEDAServiceLevel'
    object = 'SEDAArchiveTransfer'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDAAcquisitionInformation(EntityType):
    u""""""


class archive_transfer_acquisition_information_from(RelationDefinition):
    name = 'seda_acquisition_information_from'
    subject = 'SEDAAcquisitionInformation'
    object = 'SEDAArchiveTransfer'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

class acquisition_information_acquisition_information_to(RelationDefinition):
    name = 'seda_acquisition_information_to'
    subject = 'SEDAAcquisitionInformation'
    object = 'Concept'
    cardinality = '?*'
    composite = fulltext_container = None
    inlined = True
    constraints = [RQLConstraint('O in_scheme CS, EXISTS(CACLV seda_acquisition_information_code_list_version_from AT,        CACLV seda_acquisition_information_code_list_version_to CS,       S container AT) OR EXISTS(S container AU, AU is SEDAArchiveUnit, CS scheme_relation_type RT,            RT name "seda_acquisition_information_to")')]

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDALegalStatus(EntityType):
    u""""""


class archive_transfer_legal_status_from(RelationDefinition):
    name = 'seda_legal_status_from'
    subject = 'SEDALegalStatus'
    object = 'SEDAArchiveTransfer'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

class legal_status_legal_status_to(RelationDefinition):
    name = 'seda_legal_status_to'
    subject = 'SEDALegalStatus'
    object = 'Concept'
    cardinality = '?*'
    composite = fulltext_container = None
    inlined = True
    constraints = [RQLConstraint('O in_scheme CS, CS scheme_relation_type CR, CR name "seda_legal_status_to"')]

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDAOriginatingAgencyIdentifier(EntityType):
    u""""""
    originating_agency_identifier = String(fulltextindexed=True)


class archive_transfer_originating_agency_identifier(RelationDefinition):
    name = 'seda_originating_agency_identifier'
    subject = 'SEDAOriginatingAgencyIdentifier'
    object = 'SEDAArchiveTransfer'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDASubmissionAgencyIdentifier(EntityType):
    u""""""
    submission_agency_identifier = String(fulltextindexed=True)


class archive_transfer_submission_agency_identifier(RelationDefinition):
    name = 'seda_submission_agency_identifier'
    subject = 'SEDASubmissionAgencyIdentifier'
    object = 'SEDAArchiveTransfer'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDAStorageRule(EntityType):
    u""""""


class archive_transfer_storage_rule(RelationDefinition):
    name = 'seda_storage_rule'
    subject = 'SEDAStorageRule'
    object = 'SEDAArchiveTransfer'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDAAppraisalRule(EntityType):
    u""""""


class archive_transfer_appraisal_rule(RelationDefinition):
    name = 'seda_appraisal_rule'
    subject = 'SEDAAppraisalRule'
    object = 'SEDAArchiveTransfer'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDAAccessRule(EntityType):
    u""""""


class archive_transfer_access_rule(RelationDefinition):
    name = 'seda_access_rule'
    subject = 'SEDAAccessRule'
    object = 'SEDAArchiveTransfer'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDADisseminationRule(EntityType):
    u""""""


class archive_transfer_dissemination_rule(RelationDefinition):
    name = 'seda_dissemination_rule'
    subject = 'SEDADisseminationRule'
    object = 'SEDAArchiveTransfer'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDAReuseRule(EntityType):
    u""""""


class archive_transfer_reuse_rule(RelationDefinition):
    name = 'seda_reuse_rule'
    subject = 'SEDAReuseRule'
    object = 'SEDAArchiveTransfer'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDAClassificationRule(EntityType):
    u""""""
    classification_owner = String(fulltextindexed=True)


class archive_transfer_classification_rule(RelationDefinition):
    name = 'seda_classification_rule'
    subject = 'SEDAClassificationRule'
    object = 'SEDAArchiveTransfer'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDANeedAuthorization(EntityType):
    u""""""
    need_authorization = Boolean()


class archive_transfer_need_authorization(RelationDefinition):
    name = 'seda_need_authorization'
    subject = 'SEDANeedAuthorization'
    object = ('SEDAArchiveTransfer', 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement')
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['1'], default_cardinality='1',
                      annotable=False)
class SEDAAltArchiveUnitArchiveUnitRefId(EntityType):
    u""""""


class archive_unit_alt_archive_unit_archive_unit_ref_id(RelationDefinition):
    name = 'seda_alt_archive_unit_archive_unit_ref_id'
    subject = 'SEDAArchiveUnit'
    object = 'SEDAAltArchiveUnitArchiveUnitRefId'
    cardinality = '11'
    composite = fulltext_container = 'subject'
    inlined = False
    constraints = []

class relationship_type_relationship(RelationDefinition):
    name = 'seda_type_relationship'
    subject = 'SEDARelationship'
    object = 'Concept'
    cardinality = '?*'
    composite = fulltext_container = None
    inlined = True
    constraints = [RQLConstraint('O in_scheme CS, CACLV seda_relationship_code_list_version_from AT, CACLV seda_relationship_code_list_version_to CS,S container AT')]

class relationship_target(RelationDefinition):
    name = 'seda_target'
    subject = 'SEDARelationship'
    object = ('SEDABinaryDataObject', 'SEDAPhysicalDataObject')
    cardinality = '?*'
    composite = fulltext_container = None
    inlined = True
    constraints = [RQLConstraint('S container C, O container C')]

@seda_profile_element(cardinalities=['1'], default_cardinality='1',
                      annotable=False)
class SEDAAttachment(EntityType):
    u""""""


class alt_binary_data_object_attachment_attachment(RelationDefinition):
    name = 'seda_attachment'
    subject = 'SEDAAttachment'
    object = 'SEDAAltBinaryDataObjectAttachment'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['1'], default_cardinality='1',
                      annotable=False)
class SEDAUri(EntityType):
    u""""""


class alt_binary_data_object_attachment_uri(RelationDefinition):
    name = 'seda_uri'
    subject = 'SEDAUri'
    object = 'SEDAAltBinaryDataObjectAttachment'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

class binary_data_object_algorithm(RelationDefinition):
    name = 'seda_algorithm'
    subject = 'SEDABinaryDataObject'
    object = 'Concept'
    cardinality = '?*'
    composite = fulltext_container = None
    inlined = True
    constraints = [RQLConstraint('O in_scheme CS, EXISTS(S container AT, CACLV seda_message_digest_algorithm_code_list_version_from AT,        CACLV seda_message_digest_algorithm_code_list_version_to CS) OR EXISTS(S container AU, AU is SEDAArchiveUnit,           CS scheme_relation_type RT, RT name "seda_algorithm",           CS scheme_entity_type ET, ET name "SEDABinaryDataObject")')]

class compressed_algorithm(RelationDefinition):
    name = 'seda_algorithm'
    subject = 'SEDACompressed'
    object = 'Concept'
    cardinality = '?*'
    composite = fulltext_container = None
    inlined = True
    constraints = [RQLConstraint('O in_scheme CS, CACLV seda_compression_algorithm_code_list_version_from AT, CACLV seda_compression_algorithm_code_list_version_to CS,S container AT')]

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDAFormatLitteral(EntityType):
    u""""""
    format_litteral = String(fulltextindexed=True)


class binary_data_object_format_litteral(RelationDefinition):
    name = 'seda_format_litteral'
    subject = 'SEDAFormatLitteral'
    object = 'SEDABinaryDataObject'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDAMimeType(EntityType):
    u""""""


class binary_data_object_mime_type_from(RelationDefinition):
    name = 'seda_mime_type_from'
    subject = 'SEDAMimeType'
    object = 'SEDABinaryDataObject'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

class mime_type_mime_type_to(RelationDefinition):
    name = 'seda_mime_type_to'
    subject = 'SEDAMimeType'
    object = 'Concept'
    cardinality = '**'
    composite = fulltext_container = None
    inlined = False
    constraints = [RQLConstraint('O in_scheme CS, EXISTS(CACLV seda_mime_type_code_list_version_from AT,        CACLV seda_mime_type_code_list_version_to CS,       S container AT) OR EXISTS(S container AU, AU is SEDAArchiveUnit, CS scheme_relation_type RT,            RT name "file_category")')]

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDAFormatId(EntityType):
    u""""""


class binary_data_object_format_id_from(RelationDefinition):
    name = 'seda_format_id_from'
    subject = 'SEDAFormatId'
    object = 'SEDABinaryDataObject'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

class format_id_format_id_to(RelationDefinition):
    name = 'seda_format_id_to'
    subject = 'SEDAFormatId'
    object = 'Concept'
    cardinality = '**'
    composite = fulltext_container = None
    inlined = False
    constraints = [RQLConstraint('O in_scheme CS, EXISTS(CACL seda_file_format_code_list_version_from AT,        CACL seda_file_format_code_list_version_to CS,        S container AT) OR EXISTS(S container AU, AU is SEDAArchiveUnit, CS scheme_relation_type RT,            RT name "file_category")')]

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDAEncoding(EntityType):
    u""""""


class binary_data_object_encoding_from(RelationDefinition):
    name = 'seda_encoding_from'
    subject = 'SEDAEncoding'
    object = 'SEDABinaryDataObject'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

class encoding_encoding_to(RelationDefinition):
    name = 'seda_encoding_to'
    subject = 'SEDAEncoding'
    object = 'Concept'
    cardinality = '?*'
    composite = fulltext_container = None
    inlined = True
    constraints = [RQLConstraint('O in_scheme CS, EXISTS(CACLV seda_encoding_code_list_version_from AT,        CACLV seda_encoding_code_list_version_to CS,       S container AT) OR EXISTS(S container AU, AU is SEDAArchiveUnit, CS scheme_relation_type RT,            RT name "seda_encoding_to")')]

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDACreatingApplicationName(EntityType):
    u""""""
    creating_application_name = String(fulltextindexed=True)


class binary_data_object_creating_application_name(RelationDefinition):
    name = 'seda_creating_application_name'
    subject = 'SEDACreatingApplicationName'
    object = 'SEDABinaryDataObject'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDACreatingApplicationVersion(EntityType):
    u""""""
    creating_application_version = String(fulltextindexed=True)


class binary_data_object_creating_application_version(RelationDefinition):
    name = 'seda_creating_application_version'
    subject = 'SEDACreatingApplicationVersion'
    object = 'SEDABinaryDataObject'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDADateCreatedByApplication(EntityType):
    u""""""


class binary_data_object_date_created_by_application(RelationDefinition):
    name = 'seda_date_created_by_application'
    subject = 'SEDADateCreatedByApplication'
    object = 'SEDABinaryDataObject'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDACreatingOs(EntityType):
    u""""""
    creating_os = String(fulltextindexed=True)


class binary_data_object_creating_os(RelationDefinition):
    name = 'seda_creating_os'
    subject = 'SEDACreatingOs'
    object = 'SEDABinaryDataObject'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDACreatingOsVersion(EntityType):
    u""""""
    creating_os_version = String(fulltextindexed=True)


class binary_data_object_creating_os_version(RelationDefinition):
    name = 'seda_creating_os_version'
    subject = 'SEDACreatingOsVersion'
    object = 'SEDABinaryDataObject'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDALastModified(EntityType):
    u""""""


class binary_data_object_last_modified(RelationDefinition):
    name = 'seda_last_modified'
    subject = 'SEDALastModified'
    object = 'SEDABinaryDataObject'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDAWidth(EntityType):
    u""""""


class physical_data_object_width(RelationDefinition):
    name = 'seda_width'
    subject = 'SEDAWidth'
    object = 'SEDAPhysicalDataObject'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDAHeight(EntityType):
    u""""""


class physical_data_object_height(RelationDefinition):
    name = 'seda_height'
    subject = 'SEDAHeight'
    object = 'SEDAPhysicalDataObject'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDADepth(EntityType):
    u""""""


class physical_data_object_depth(RelationDefinition):
    name = 'seda_depth'
    subject = 'SEDADepth'
    object = 'SEDAPhysicalDataObject'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDAShape(EntityType):
    u""""""


class physical_data_object_shape(RelationDefinition):
    name = 'seda_shape'
    subject = 'SEDAShape'
    object = 'SEDAPhysicalDataObject'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDADiameter(EntityType):
    u""""""


class physical_data_object_diameter(RelationDefinition):
    name = 'seda_diameter'
    subject = 'SEDADiameter'
    object = 'SEDAPhysicalDataObject'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDALength(EntityType):
    u""""""


class physical_data_object_length(RelationDefinition):
    name = 'seda_length'
    subject = 'SEDALength'
    object = 'SEDAPhysicalDataObject'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDAThickness(EntityType):
    u""""""


class physical_data_object_thickness(RelationDefinition):
    name = 'seda_thickness'
    subject = 'SEDAThickness'
    object = 'SEDAPhysicalDataObject'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDAWeight(EntityType):
    u""""""


class physical_data_object_weight(RelationDefinition):
    name = 'seda_weight'
    subject = 'SEDAWeight'
    object = 'SEDAPhysicalDataObject'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDANumberOfPage(EntityType):
    u""""""


class physical_data_object_number_of_page(RelationDefinition):
    name = 'seda_number_of_page'
    subject = 'SEDANumberOfPage'
    object = 'SEDAPhysicalDataObject'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['1'], default_cardinality='1',
                      annotable=False)
class SEDAArchiveUnitRefId(EntityType):
    u""""""


class alt_archive_unit_archive_unit_ref_id_archive_unit_ref_id_from(RelationDefinition):
    name = 'seda_archive_unit_ref_id_from'
    subject = 'SEDAArchiveUnitRefId'
    object = ('SEDAAltArchiveUnitArchiveUnitRefId', 'SEDAAltIsPartOfArchiveUnitRefId', 'SEDAAltIsVersionOfArchiveUnitRefId', 'SEDAAltReferencesArchiveUnitRefId', 'SEDAAltReplacesArchiveUnitRefId', 'SEDAAltRequiresArchiveUnitRefId')
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

class archive_unit_ref_id_archive_unit_ref_id_to(RelationDefinition):
    name = 'seda_archive_unit_ref_id_to'
    subject = 'SEDAArchiveUnitRefId'
    object = 'SEDAArchiveUnit'
    cardinality = '?*'
    composite = fulltext_container = None
    inlined = True
    constraints = [RQLConstraint('S container C, O container C')]

@seda_profile_element(cardinalities=['1'], default_cardinality='1',
                      annotable=False)
class SEDASeqAltArchiveUnitArchiveUnitRefIdManagement(EntityType):
    u""""""


class alt_archive_unit_archive_unit_ref_id_seq_alt_archive_unit_archive_unit_ref_id_management(RelationDefinition):
    name = 'seda_seq_alt_archive_unit_archive_unit_ref_id_management'
    subject = 'SEDAAltArchiveUnitArchiveUnitRefId'
    object = 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'
    cardinality = '?1'
    composite = fulltext_container = 'subject'
    inlined = False
    constraints = []

@seda_profile_element(cardinalities=['0..1', '0..n', '1', '1..n'], default_cardinality='1',
                      annotable=True)
class SEDASeqStorageRuleRule(EntityType):
    u""""""


class storage_rule_seq_storage_rule_rule(RelationDefinition):
    name = 'seda_seq_storage_rule_rule'
    subject = 'SEDAStorageRule'
    object = 'SEDASeqStorageRuleRule'
    cardinality = '*1'
    composite = fulltext_container = 'subject'
    inlined = False
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDAAltStorageRulePreventInheritance(EntityType):
    u""""""


class storage_rule_alt_storage_rule_prevent_inheritance(RelationDefinition):
    name = 'seda_alt_storage_rule_prevent_inheritance'
    subject = 'SEDAStorageRule'
    object = 'SEDAAltStorageRulePreventInheritance'
    cardinality = '?1'
    composite = fulltext_container = 'subject'
    inlined = False
    constraints = []

class storage_rule_final_action(RelationDefinition):
    name = 'seda_final_action'
    subject = 'SEDAStorageRule'
    object = 'Concept'
    cardinality = '?*'
    composite = fulltext_container = None
    inlined = True
    constraints = [RQLConstraint('O in_scheme CS, CS scheme_relation_type CR, CR name "seda_final_action", CS scheme_entity_type ET, ET name "SEDAStorageRule"')]

@seda_profile_element(cardinalities=['0..1', '0..n', '1', '1..n'], default_cardinality='1',
                      annotable=True)
class SEDASeqAppraisalRuleRule(EntityType):
    u""""""


class appraisal_rule_seq_appraisal_rule_rule(RelationDefinition):
    name = 'seda_seq_appraisal_rule_rule'
    subject = 'SEDAAppraisalRule'
    object = 'SEDASeqAppraisalRuleRule'
    cardinality = '*1'
    composite = fulltext_container = 'subject'
    inlined = False
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDAAltAppraisalRulePreventInheritance(EntityType):
    u""""""


class appraisal_rule_alt_appraisal_rule_prevent_inheritance(RelationDefinition):
    name = 'seda_alt_appraisal_rule_prevent_inheritance'
    subject = 'SEDAAppraisalRule'
    object = 'SEDAAltAppraisalRulePreventInheritance'
    cardinality = '?1'
    composite = fulltext_container = 'subject'
    inlined = False
    constraints = []

class appraisal_rule_final_action(RelationDefinition):
    name = 'seda_final_action'
    subject = 'SEDAAppraisalRule'
    object = 'Concept'
    cardinality = '?*'
    composite = fulltext_container = None
    inlined = True
    constraints = [RQLConstraint('O in_scheme CS, CS scheme_relation_type CR, CR name "seda_final_action", CS scheme_entity_type ET, ET name "SEDAAppraisalRule"')]

@seda_profile_element(cardinalities=['0..1', '0..n', '1', '1..n'], default_cardinality='1',
                      annotable=True)
class SEDASeqAccessRuleRule(EntityType):
    u""""""


class access_rule_seq_access_rule_rule(RelationDefinition):
    name = 'seda_seq_access_rule_rule'
    subject = 'SEDAAccessRule'
    object = 'SEDASeqAccessRuleRule'
    cardinality = '*1'
    composite = fulltext_container = 'subject'
    inlined = False
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDAAltAccessRulePreventInheritance(EntityType):
    u""""""


class access_rule_alt_access_rule_prevent_inheritance(RelationDefinition):
    name = 'seda_alt_access_rule_prevent_inheritance'
    subject = 'SEDAAccessRule'
    object = 'SEDAAltAccessRulePreventInheritance'
    cardinality = '?1'
    composite = fulltext_container = 'subject'
    inlined = False
    constraints = []

@seda_profile_element(cardinalities=['0..1', '0..n', '1', '1..n'], default_cardinality='1',
                      annotable=True)
class SEDASeqDisseminationRuleRule(EntityType):
    u""""""


class dissemination_rule_seq_dissemination_rule_rule(RelationDefinition):
    name = 'seda_seq_dissemination_rule_rule'
    subject = 'SEDADisseminationRule'
    object = 'SEDASeqDisseminationRuleRule'
    cardinality = '*1'
    composite = fulltext_container = 'subject'
    inlined = False
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDAAltDisseminationRulePreventInheritance(EntityType):
    u""""""


class dissemination_rule_alt_dissemination_rule_prevent_inheritance(RelationDefinition):
    name = 'seda_alt_dissemination_rule_prevent_inheritance'
    subject = 'SEDADisseminationRule'
    object = 'SEDAAltDisseminationRulePreventInheritance'
    cardinality = '?1'
    composite = fulltext_container = 'subject'
    inlined = False
    constraints = []

@seda_profile_element(cardinalities=['0..1', '0..n', '1', '1..n'], default_cardinality='1',
                      annotable=True)
class SEDASeqReuseRuleRule(EntityType):
    u""""""


class reuse_rule_seq_reuse_rule_rule(RelationDefinition):
    name = 'seda_seq_reuse_rule_rule'
    subject = 'SEDAReuseRule'
    object = 'SEDASeqReuseRuleRule'
    cardinality = '*1'
    composite = fulltext_container = 'subject'
    inlined = False
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDAAltReuseRulePreventInheritance(EntityType):
    u""""""


class reuse_rule_alt_reuse_rule_prevent_inheritance(RelationDefinition):
    name = 'seda_alt_reuse_rule_prevent_inheritance'
    subject = 'SEDAReuseRule'
    object = 'SEDAAltReuseRulePreventInheritance'
    cardinality = '?1'
    composite = fulltext_container = 'subject'
    inlined = False
    constraints = []

@seda_profile_element(cardinalities=['0..1', '0..n', '1', '1..n'], default_cardinality='1',
                      annotable=True)
class SEDASeqClassificationRuleRule(EntityType):
    u""""""


class classification_rule_seq_classification_rule_rule(RelationDefinition):
    name = 'seda_seq_classification_rule_rule'
    subject = 'SEDAClassificationRule'
    object = 'SEDASeqClassificationRuleRule'
    cardinality = '*1'
    composite = fulltext_container = 'subject'
    inlined = False
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDAAltClassificationRulePreventInheritance(EntityType):
    u""""""


class classification_rule_alt_classification_rule_prevent_inheritance(RelationDefinition):
    name = 'seda_alt_classification_rule_prevent_inheritance'
    subject = 'SEDAClassificationRule'
    object = 'SEDAAltClassificationRulePreventInheritance'
    cardinality = '?1'
    composite = fulltext_container = 'subject'
    inlined = False
    constraints = []

class classification_rule_classification_level(RelationDefinition):
    name = 'seda_classification_level'
    subject = 'SEDAClassificationRule'
    object = 'Concept'
    cardinality = '?*'
    composite = fulltext_container = None
    inlined = True
    constraints = [RQLConstraint('O in_scheme CS, CS scheme_relation_type CR, CR name "seda_classification_level"')]

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDAClassificationReassessingDate(EntityType):
    u""""""


class classification_rule_classification_reassessing_date(RelationDefinition):
    name = 'seda_classification_reassessing_date'
    subject = 'SEDAClassificationReassessingDate'
    object = 'SEDAClassificationRule'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDANeedReassessingAuthorization(EntityType):
    u""""""
    need_reassessing_authorization = Boolean()


class classification_rule_need_reassessing_authorization(RelationDefinition):
    name = 'seda_need_reassessing_authorization'
    subject = 'SEDANeedReassessingAuthorization'
    object = 'SEDAClassificationRule'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

class seq_alt_archive_unit_archive_unit_ref_id_management_archive_unit(RelationDefinition):
    name = 'seda_archive_unit'
    subject = 'SEDAArchiveUnit'
    object = 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'
    cardinality = '?*'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '0..n', '1', '1..n'], default_cardinality='1',
                      annotable=True)
class SEDADataObjectReference(EntityType):
    u""""""


class seq_alt_archive_unit_archive_unit_ref_id_management_data_object_reference(RelationDefinition):
    name = 'seda_data_object_reference'
    subject = 'SEDADataObjectReference'
    object = 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'
    cardinality = '1*'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

class width_unit(RelationDefinition):
    name = 'seda_unit'
    subject = 'SEDAWidth'
    object = 'Concept'
    cardinality = '?*'
    composite = fulltext_container = None
    inlined = True
    constraints = [RQLConstraint('O in_scheme CS, CS scheme_relation_type CR, CR name "seda_unit", CS scheme_entity_type ET, ET name "SEDAWidth"')]

class height_unit(RelationDefinition):
    name = 'seda_unit'
    subject = 'SEDAHeight'
    object = 'Concept'
    cardinality = '?*'
    composite = fulltext_container = None
    inlined = True
    constraints = [RQLConstraint('O in_scheme CS, CS scheme_relation_type CR, CR name "seda_unit", CS scheme_entity_type ET, ET name "SEDAHeight"')]

class depth_unit(RelationDefinition):
    name = 'seda_unit'
    subject = 'SEDADepth'
    object = 'Concept'
    cardinality = '?*'
    composite = fulltext_container = None
    inlined = True
    constraints = [RQLConstraint('O in_scheme CS, CS scheme_relation_type CR, CR name "seda_unit", CS scheme_entity_type ET, ET name "SEDADepth"')]

class diameter_unit(RelationDefinition):
    name = 'seda_unit'
    subject = 'SEDADiameter'
    object = 'Concept'
    cardinality = '?*'
    composite = fulltext_container = None
    inlined = True
    constraints = [RQLConstraint('O in_scheme CS, CS scheme_relation_type CR, CR name "seda_unit", CS scheme_entity_type ET, ET name "SEDADiameter"')]

class length_unit(RelationDefinition):
    name = 'seda_unit'
    subject = 'SEDALength'
    object = 'Concept'
    cardinality = '?*'
    composite = fulltext_container = None
    inlined = True
    constraints = [RQLConstraint('O in_scheme CS, CS scheme_relation_type CR, CR name "seda_unit", CS scheme_entity_type ET, ET name "SEDALength"')]

class thickness_unit(RelationDefinition):
    name = 'seda_unit'
    subject = 'SEDAThickness'
    object = 'Concept'
    cardinality = '?*'
    composite = fulltext_container = None
    inlined = True
    constraints = [RQLConstraint('O in_scheme CS, CS scheme_relation_type CR, CR name "seda_unit", CS scheme_entity_type ET, ET name "SEDAThickness"')]

class weight_unit(RelationDefinition):
    name = 'seda_unit'
    subject = 'SEDAWeight'
    object = 'Concept'
    cardinality = '?*'
    composite = fulltext_container = None
    inlined = True
    constraints = [RQLConstraint('O in_scheme CS, CS scheme_relation_type CR, CR name "seda_unit", CS scheme_entity_type ET, ET name "SEDAWeight"')]

class seq_alt_archive_unit_archive_unit_ref_id_management_storage_rule(RelationDefinition):
    name = 'seda_storage_rule'
    subject = 'SEDAStorageRule'
    object = 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

class seq_alt_archive_unit_archive_unit_ref_id_management_appraisal_rule(RelationDefinition):
    name = 'seda_appraisal_rule'
    subject = 'SEDAAppraisalRule'
    object = 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

class seq_alt_archive_unit_archive_unit_ref_id_management_access_rule(RelationDefinition):
    name = 'seda_access_rule'
    subject = 'SEDAAccessRule'
    object = 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

class seq_alt_archive_unit_archive_unit_ref_id_management_dissemination_rule(RelationDefinition):
    name = 'seda_dissemination_rule'
    subject = 'SEDADisseminationRule'
    object = 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

class seq_alt_archive_unit_archive_unit_ref_id_management_reuse_rule(RelationDefinition):
    name = 'seda_reuse_rule'
    subject = 'SEDAReuseRule'
    object = 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

class seq_alt_archive_unit_archive_unit_ref_id_management_classification_rule(RelationDefinition):
    name = 'seda_classification_rule'
    subject = 'SEDAClassificationRule'
    object = 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

class seq_alt_archive_unit_archive_unit_ref_id_management_description_level(RelationDefinition):
    name = 'seda_description_level'
    subject = 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'
    object = 'Concept'
    cardinality = '1*'
    composite = fulltext_container = None
    inlined = True
    constraints = [RQLConstraint('O in_scheme CS, CS scheme_relation_type CR, CR name "seda_description_level"')]

@seda_profile_element(cardinalities=['1..n', '1'], default_cardinality='1',
                      annotable=True)
class SEDATitle(EntityType):
    u""""""
    title = String(fulltextindexed=True)


class seq_alt_archive_unit_archive_unit_ref_id_management_title(RelationDefinition):
    name = 'seda_title'
    subject = 'SEDATitle'
    object = 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'
    cardinality = '11'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDAFilePlanPosition(EntityType):
    u""""""
    file_plan_position = String(fulltextindexed=True)


class seq_alt_archive_unit_archive_unit_ref_id_management_file_plan_position(RelationDefinition):
    name = 'seda_file_plan_position'
    subject = 'SEDAFilePlanPosition'
    object = 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDASystemId(EntityType):
    u""""""


class seq_alt_archive_unit_archive_unit_ref_id_management_system_id(RelationDefinition):
    name = 'seda_system_id'
    subject = 'SEDASystemId'
    object = 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDAOriginatingSystemId(EntityType):
    u""""""


class seq_alt_archive_unit_archive_unit_ref_id_management_originating_system_id(RelationDefinition):
    name = 'seda_originating_system_id'
    subject = 'SEDAOriginatingSystemId'
    object = 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDAArchivalAgencyArchiveUnitIdentifier(EntityType):
    u""""""
    archival_agency_archive_unit_identifier = String(fulltextindexed=True)


class seq_alt_archive_unit_archive_unit_ref_id_management_archival_agency_archive_unit_identifier(RelationDefinition):
    name = 'seda_archival_agency_archive_unit_identifier'
    subject = 'SEDAArchivalAgencyArchiveUnitIdentifier'
    object = 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDAOriginatingAgencyArchiveUnitIdentifier(EntityType):
    u""""""
    originating_agency_archive_unit_identifier = String(fulltextindexed=True)


class seq_alt_archive_unit_archive_unit_ref_id_management_originating_agency_archive_unit_identifier(RelationDefinition):
    name = 'seda_originating_agency_archive_unit_identifier'
    subject = 'SEDAOriginatingAgencyArchiveUnitIdentifier'
    object = 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDATransferringAgencyArchiveUnitIdentifier(EntityType):
    u""""""
    transferring_agency_archive_unit_identifier = String(fulltextindexed=True)


class seq_alt_archive_unit_archive_unit_ref_id_management_transferring_agency_archive_unit_identifier(RelationDefinition):
    name = 'seda_transferring_agency_archive_unit_identifier'
    subject = 'SEDATransferringAgencyArchiveUnitIdentifier'
    object = 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '0..n', '1', '1..n'], default_cardinality='1',
                      annotable=True)
class SEDADescription(EntityType):
    u""""""
    description = String(fulltextindexed=True)


class seq_alt_archive_unit_archive_unit_ref_id_management_description(RelationDefinition):
    name = 'seda_description'
    subject = 'SEDADescription'
    object = 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDAType(EntityType):
    u""""""


class seq_alt_archive_unit_archive_unit_ref_id_management_type_from(RelationDefinition):
    name = 'seda_type_from'
    subject = 'SEDAType'
    object = 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

class type_type_to(RelationDefinition):
    name = 'seda_type_to'
    subject = 'SEDAType'
    object = 'Concept'
    cardinality = '?*'
    composite = fulltext_container = None
    inlined = True
    constraints = [RQLConstraint('O in_scheme CS, CS scheme_relation_type CR, CR name "seda_type_to"')]

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDADocumentType(EntityType):
    u""""""
    document_type = String(fulltextindexed=True)


class seq_alt_archive_unit_archive_unit_ref_id_management_document_type(RelationDefinition):
    name = 'seda_document_type'
    subject = 'SEDADocumentType'
    object = 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDALanguage(EntityType):
    u""""""


class seq_alt_archive_unit_archive_unit_ref_id_management_language_from(RelationDefinition):
    name = 'seda_language_from'
    subject = 'SEDALanguage'
    object = 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

class language_language_to(RelationDefinition):
    name = 'seda_language_to'
    subject = 'SEDALanguage'
    object = 'Concept'
    cardinality = '?*'
    composite = fulltext_container = None
    inlined = True
    constraints = [RQLConstraint('O in_scheme CS, CS scheme_relation_type CR, CR name "seda_language_to"')]

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDADescriptionLanguage(EntityType):
    u""""""


class seq_alt_archive_unit_archive_unit_ref_id_management_description_language_from(RelationDefinition):
    name = 'seda_description_language_from'
    subject = 'SEDADescriptionLanguage'
    object = 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

class description_language_description_language_to(RelationDefinition):
    name = 'seda_description_language_to'
    subject = 'SEDADescriptionLanguage'
    object = 'Concept'
    cardinality = '?*'
    composite = fulltext_container = None
    inlined = True
    constraints = [RQLConstraint('O in_scheme CS, CS scheme_relation_type CR, CR name "seda_description_language_to"')]

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDAStatus(EntityType):
    u""""""
    status = String(fulltextindexed=True)


class seq_alt_archive_unit_archive_unit_ref_id_management_status(RelationDefinition):
    name = 'seda_status'
    subject = 'SEDAStatus'
    object = 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDAVersion(EntityType):
    u""""""
    version = String(fulltextindexed=True)


class seq_alt_archive_unit_archive_unit_ref_id_management_version(RelationDefinition):
    name = 'seda_version'
    subject = 'SEDAVersion'
    object = 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '0..n', '1', '1..n'], default_cardinality='1',
                      annotable=True)
class SEDATag(EntityType):
    u""""""
    tag = String(fulltextindexed=True)


class seq_alt_archive_unit_archive_unit_ref_id_management_tag(RelationDefinition):
    name = 'seda_tag'
    subject = 'SEDATag'
    object = 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'
    cardinality = '1*'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '0..n', '1', '1..n'], default_cardinality='1',
                      annotable=True)
class SEDAKeyword(EntityType):
    u""""""
    keyword_content = String(fulltextindexed=True)


class seq_alt_archive_unit_archive_unit_ref_id_management_keyword(RelationDefinition):
    name = 'seda_keyword'
    subject = 'SEDAKeyword'
    object = 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'
    cardinality = '1*'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDAOriginatingAgency(EntityType):
    u""""""


class seq_alt_archive_unit_archive_unit_ref_id_management_originating_agency_from(RelationDefinition):
    name = 'seda_originating_agency_from'
    subject = 'SEDAOriginatingAgency'
    object = 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

class originating_agency_originating_agency_to(RelationDefinition):
    name = 'seda_originating_agency_to'
    subject = 'SEDAOriginatingAgency'
    object = 'AuthorityRecord'
    cardinality = '?*'
    composite = fulltext_container = None
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDASubmissionAgency(EntityType):
    u""""""


class seq_alt_archive_unit_archive_unit_ref_id_management_submission_agency_from(RelationDefinition):
    name = 'seda_submission_agency_from'
    subject = 'SEDASubmissionAgency'
    object = 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

class submission_agency_submission_agency_to(RelationDefinition):
    name = 'seda_submission_agency_to'
    subject = 'SEDASubmissionAgency'
    object = 'AuthorityRecord'
    cardinality = '?*'
    composite = fulltext_container = None
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDAAuthorizedAgent(EntityType):
    u""""""


class seq_alt_archive_unit_archive_unit_ref_id_management_authorized_agent_from(RelationDefinition):
    name = 'seda_authorized_agent_from'
    subject = 'SEDAAuthorizedAgent'
    object = 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

class authorized_agent_authorized_agent_to(RelationDefinition):
    name = 'seda_authorized_agent_to'
    subject = 'SEDAAuthorizedAgent'
    object = 'AuthorityRecord'
    cardinality = '?*'
    composite = fulltext_container = None
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '0..n', '1', '1..n'], default_cardinality='1',
                      annotable=True)
class SEDAWriter(EntityType):
    u""""""


class seq_alt_archive_unit_archive_unit_ref_id_management_writer_from(RelationDefinition):
    name = 'seda_writer_from'
    subject = 'SEDAWriter'
    object = 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'
    cardinality = '1*'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

class writer_writer_to(RelationDefinition):
    name = 'seda_writer_to'
    subject = 'SEDAWriter'
    object = 'AuthorityRecord'
    cardinality = '**'
    composite = fulltext_container = None
    inlined = False
    constraints = []

@seda_profile_element(cardinalities=['0..1', '0..n', '1', '1..n'], default_cardinality='1',
                      annotable=True)
class SEDAAddressee(EntityType):
    u""""""


class seq_alt_archive_unit_archive_unit_ref_id_management_addressee_from(RelationDefinition):
    name = 'seda_addressee_from'
    subject = 'SEDAAddressee'
    object = 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'
    cardinality = '1*'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

class addressee_addressee_to(RelationDefinition):
    name = 'seda_addressee_to'
    subject = 'SEDAAddressee'
    object = 'AuthorityRecord'
    cardinality = '**'
    composite = fulltext_container = None
    inlined = False
    constraints = []

@seda_profile_element(cardinalities=['0..1', '0..n', '1', '1..n'], default_cardinality='1',
                      annotable=True)
class SEDARecipient(EntityType):
    u""""""


class seq_alt_archive_unit_archive_unit_ref_id_management_recipient_from(RelationDefinition):
    name = 'seda_recipient_from'
    subject = 'SEDARecipient'
    object = 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'
    cardinality = '1*'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

class recipient_recipient_to(RelationDefinition):
    name = 'seda_recipient_to'
    subject = 'SEDARecipient'
    object = 'AuthorityRecord'
    cardinality = '**'
    composite = fulltext_container = None
    inlined = False
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDASource(EntityType):
    u""""""
    source = String(fulltextindexed=True)


class seq_alt_archive_unit_archive_unit_ref_id_management_source(RelationDefinition):
    name = 'seda_source'
    subject = 'SEDASource'
    object = 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDACreatedDate(EntityType):
    u""""""


class seq_alt_archive_unit_archive_unit_ref_id_management_created_date(RelationDefinition):
    name = 'seda_created_date'
    subject = 'SEDACreatedDate'
    object = 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDATransactedDate(EntityType):
    u""""""


class seq_alt_archive_unit_archive_unit_ref_id_management_transacted_date(RelationDefinition):
    name = 'seda_transacted_date'
    subject = 'SEDATransactedDate'
    object = 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDAAcquiredDate(EntityType):
    u""""""


class seq_alt_archive_unit_archive_unit_ref_id_management_acquired_date(RelationDefinition):
    name = 'seda_acquired_date'
    subject = 'SEDAAcquiredDate'
    object = 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDASentDate(EntityType):
    u""""""


class seq_alt_archive_unit_archive_unit_ref_id_management_sent_date(RelationDefinition):
    name = 'seda_sent_date'
    subject = 'SEDASentDate'
    object = 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDAReceivedDate(EntityType):
    u""""""


class seq_alt_archive_unit_archive_unit_ref_id_management_received_date(RelationDefinition):
    name = 'seda_received_date'
    subject = 'SEDAReceivedDate'
    object = 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDARegisteredDate(EntityType):
    u""""""


class seq_alt_archive_unit_archive_unit_ref_id_management_registered_date(RelationDefinition):
    name = 'seda_registered_date'
    subject = 'SEDARegisteredDate'
    object = 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDAStartDate(EntityType):
    u""""""


class seq_alt_archive_unit_archive_unit_ref_id_management_start_date(RelationDefinition):
    name = 'seda_start_date'
    subject = 'SEDAStartDate'
    object = 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDAEndDate(EntityType):
    u""""""


class seq_alt_archive_unit_archive_unit_ref_id_management_end_date(RelationDefinition):
    name = 'seda_end_date'
    subject = 'SEDAEndDate'
    object = 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '0..n', '1', '1..n'], default_cardinality='1',
                      annotable=True)
class SEDAEvent(EntityType):
    u""""""


class seq_alt_archive_unit_archive_unit_ref_id_management_event(RelationDefinition):
    name = 'seda_event'
    subject = 'SEDAEvent'
    object = 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'
    cardinality = '1*'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

class data_object_reference_data_object_reference_id(RelationDefinition):
    name = 'seda_data_object_reference_id'
    subject = 'SEDADataObjectReference'
    object = ('SEDABinaryDataObject', 'SEDAPhysicalDataObject')
    cardinality = '?*'
    composite = fulltext_container = None
    inlined = True
    constraints = [RQLConstraint('S container C, O container C')]

class seq_storage_rule_rule_rule(RelationDefinition):
    name = 'seda_rule'
    subject = 'SEDASeqStorageRuleRule'
    object = 'Concept'
    cardinality = '?*'
    composite = fulltext_container = None
    inlined = True
    constraints = [RQLConstraint('O in_scheme CS, CACLV seda_storage_rule_code_list_version_from AT, CACLV seda_storage_rule_code_list_version_to CS,S container AT')]

class seq_storage_rule_rule_start_date(RelationDefinition):
    name = 'seda_start_date'
    subject = 'SEDAStartDate'
    object = ('SEDASeqAccessRuleRule', 'SEDASeqAppraisalRuleRule', 'SEDASeqClassificationRuleRule', 'SEDASeqDisseminationRuleRule', 'SEDASeqReuseRuleRule', 'SEDASeqStorageRuleRule')
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['1'], default_cardinality='1',
                      annotable=False)
class SEDAPreventInheritance(EntityType):
    u""""""
    prevent_inheritance = Boolean()


class alt_storage_rule_prevent_inheritance_prevent_inheritance(RelationDefinition):
    name = 'seda_prevent_inheritance'
    subject = 'SEDAPreventInheritance'
    object = ('SEDAAltAccessRulePreventInheritance', 'SEDAAltAppraisalRulePreventInheritance', 'SEDAAltClassificationRulePreventInheritance', 'SEDAAltDisseminationRulePreventInheritance', 'SEDAAltReuseRulePreventInheritance', 'SEDAAltStorageRulePreventInheritance')
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['1..n', '1'], default_cardinality='1',
                      annotable=True)
class SEDARefNonRuleId(EntityType):
    u""""""


class alt_storage_rule_prevent_inheritance_ref_non_rule_id_from(RelationDefinition):
    name = 'seda_ref_non_rule_id_from'
    subject = 'SEDARefNonRuleId'
    object = ('SEDAAltAccessRulePreventInheritance', 'SEDAAltAppraisalRulePreventInheritance', 'SEDAAltClassificationRulePreventInheritance', 'SEDAAltDisseminationRulePreventInheritance', 'SEDAAltReuseRulePreventInheritance', 'SEDAAltStorageRulePreventInheritance')
    cardinality = '1*'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

class ref_non_rule_id_ref_non_rule_id_to(RelationDefinition):
    name = 'seda_ref_non_rule_id_to'
    subject = 'SEDARefNonRuleId'
    object = 'Concept'
    cardinality = '**'
    composite = fulltext_container = None
    inlined = False
    constraints = []

class seq_appraisal_rule_rule_rule(RelationDefinition):
    name = 'seda_rule'
    subject = 'SEDASeqAppraisalRuleRule'
    object = 'Concept'
    cardinality = '?*'
    composite = fulltext_container = None
    inlined = True
    constraints = [RQLConstraint('O in_scheme CS, EXISTS(CACLV seda_appraisal_rule_code_list_version_from AT,        CACLV seda_appraisal_rule_code_list_version_to CS,       S container AT) OR EXISTS(S container AU, AU is SEDAArchiveUnit)')]

class seq_access_rule_rule_rule(RelationDefinition):
    name = 'seda_rule'
    subject = 'SEDASeqAccessRuleRule'
    object = 'Concept'
    cardinality = '?*'
    composite = fulltext_container = None
    inlined = True
    constraints = [RQLConstraint('O in_scheme CS, EXISTS(CACLV seda_access_rule_code_list_version_from AT,        CACLV seda_access_rule_code_list_version_to CS,       S container AT) OR EXISTS(S container AU, AU is SEDAArchiveUnit)')]

class seq_dissemination_rule_rule_rule(RelationDefinition):
    name = 'seda_rule'
    subject = 'SEDASeqDisseminationRuleRule'
    object = 'Concept'
    cardinality = '?*'
    composite = fulltext_container = None
    inlined = True
    constraints = [RQLConstraint('O in_scheme CS, CACLV seda_dissemination_rule_code_list_version_from AT, CACLV seda_dissemination_rule_code_list_version_to CS,S container AT')]

class seq_reuse_rule_rule_rule(RelationDefinition):
    name = 'seda_rule'
    subject = 'SEDASeqReuseRuleRule'
    object = 'Concept'
    cardinality = '?*'
    composite = fulltext_container = None
    inlined = True
    constraints = [RQLConstraint('O in_scheme CS, CACLV seda_reuse_rule_code_list_version_from AT, CACLV seda_reuse_rule_code_list_version_to CS,S container AT')]

class seq_classification_rule_rule_rule(RelationDefinition):
    name = 'seda_rule'
    subject = 'SEDASeqClassificationRuleRule'
    object = 'Concept'
    cardinality = '?*'
    composite = fulltext_container = None
    inlined = True
    constraints = [RQLConstraint('O in_scheme CS, CACLV seda_classification_rule_code_list_version_from AT, CACLV seda_classification_rule_code_list_version_to CS,S container AT')]

@seda_profile_element(cardinalities=['0..1', '0..n', '1', '1..n'], default_cardinality='1',
                      annotable=True)
class SEDACustodialHistoryItem(EntityType):
    u""""""
    custodial_history_item = String(fulltextindexed=True)


class seq_alt_archive_unit_archive_unit_ref_id_management_custodial_history_item(RelationDefinition):
    name = 'seda_custodial_history_item'
    subject = 'SEDACustodialHistoryItem'
    object = 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'
    cardinality = '1*'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDACustodialHistoryFile(EntityType):
    u""""""


class seq_alt_archive_unit_archive_unit_ref_id_management_custodial_history_file(RelationDefinition):
    name = 'seda_custodial_history_file'
    subject = 'SEDACustodialHistoryFile'
    object = 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDAKeywordReference(EntityType):
    u""""""


class keyword_keyword_reference_from(RelationDefinition):
    name = 'seda_keyword_reference_from'
    subject = 'SEDAKeywordReference'
    object = 'SEDAKeyword'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

class keyword_reference_keyword_reference_to(RelationDefinition):
    name = 'seda_keyword_reference_to'
    subject = 'SEDAKeywordReference'
    object = 'Concept'
    cardinality = '?*'
    composite = fulltext_container = None
    inlined = True
    constraints = [RQLConstraint('O in_scheme CS, S seda_keyword_reference_to_scheme CS')]

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDAKeywordType(EntityType):
    u""""""


class keyword_keyword_type_from(RelationDefinition):
    name = 'seda_keyword_type_from'
    subject = 'SEDAKeywordType'
    object = 'SEDAKeyword'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

class keyword_type_keyword_type_to(RelationDefinition):
    name = 'seda_keyword_type_to'
    subject = 'SEDAKeywordType'
    object = 'Concept'
    cardinality = '?*'
    composite = fulltext_container = None
    inlined = True
    constraints = [RQLConstraint('O in_scheme CS, CS scheme_relation_type CR, CR name "seda_keyword_type_to"')]

@seda_profile_element(cardinalities=['0..1', '0..n', '1', '1..n'], default_cardinality='1',
                      annotable=True)
class SEDASpatial(EntityType):
    u""""""
    spatial = String(fulltextindexed=True)


class seq_alt_archive_unit_archive_unit_ref_id_management_spatial(RelationDefinition):
    name = 'seda_spatial'
    subject = 'SEDASpatial'
    object = 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'
    cardinality = '1*'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '0..n', '1', '1..n'], default_cardinality='1',
                      annotable=True)
class SEDATemporal(EntityType):
    u""""""
    temporal = String(fulltextindexed=True)


class seq_alt_archive_unit_archive_unit_ref_id_management_temporal(RelationDefinition):
    name = 'seda_temporal'
    subject = 'SEDATemporal'
    object = 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'
    cardinality = '1*'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '0..n', '1', '1..n'], default_cardinality='1',
                      annotable=True)
class SEDAJuridictional(EntityType):
    u""""""
    juridictional = String(fulltextindexed=True)


class seq_alt_archive_unit_archive_unit_ref_id_management_juridictional(RelationDefinition):
    name = 'seda_juridictional'
    subject = 'SEDAJuridictional'
    object = 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'
    cardinality = '1*'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '0..n', '1', '1..n'], default_cardinality='1',
                      annotable=True)
class SEDAIsVersionOf(EntityType):
    u""""""


class seq_alt_archive_unit_archive_unit_ref_id_management_is_version_of(RelationDefinition):
    name = 'seda_is_version_of'
    subject = 'SEDAIsVersionOf'
    object = 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'
    cardinality = '1*'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '0..n', '1', '1..n'], default_cardinality='1',
                      annotable=True)
class SEDAReplaces(EntityType):
    u""""""


class seq_alt_archive_unit_archive_unit_ref_id_management_replaces(RelationDefinition):
    name = 'seda_replaces'
    subject = 'SEDAReplaces'
    object = 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'
    cardinality = '1*'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '0..n', '1', '1..n'], default_cardinality='1',
                      annotable=True)
class SEDARequires(EntityType):
    u""""""


class seq_alt_archive_unit_archive_unit_ref_id_management_requires(RelationDefinition):
    name = 'seda_requires'
    subject = 'SEDARequires'
    object = 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'
    cardinality = '1*'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '0..n', '1', '1..n'], default_cardinality='1',
                      annotable=True)
class SEDAIsPartOf(EntityType):
    u""""""


class seq_alt_archive_unit_archive_unit_ref_id_management_is_part_of(RelationDefinition):
    name = 'seda_is_part_of'
    subject = 'SEDAIsPartOf'
    object = 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'
    cardinality = '1*'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '0..n', '1', '1..n'], default_cardinality='1',
                      annotable=True)
class SEDAReferences(EntityType):
    u""""""


class seq_alt_archive_unit_archive_unit_ref_id_management_references(RelationDefinition):
    name = 'seda_references'
    subject = 'SEDAReferences'
    object = 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'
    cardinality = '1*'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDAEventIdentifier(EntityType):
    u""""""


class event_event_identifier(RelationDefinition):
    name = 'seda_event_identifier'
    subject = 'SEDAEventIdentifier'
    object = 'SEDAEvent'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDAEventType(EntityType):
    u""""""


class event_event_type_from(RelationDefinition):
    name = 'seda_event_type_from'
    subject = 'SEDAEventType'
    object = 'SEDAEvent'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

class event_type_event_type_to(RelationDefinition):
    name = 'seda_event_type_to'
    subject = 'SEDAEventType'
    object = 'Concept'
    cardinality = '?*'
    composite = fulltext_container = None
    inlined = True
    constraints = [RQLConstraint('O in_scheme CS, CS scheme_relation_type CR, CR name "seda_event_type_to"')]

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDAEventDetail(EntityType):
    u""""""


class event_event_detail(RelationDefinition):
    name = 'seda_event_detail'
    subject = 'SEDAEventDetail'
    object = 'SEDAEvent'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDAGpsVersionID(EntityType):
    u""""""


class seq_alt_archive_unit_archive_unit_ref_id_management_gps_version_id(RelationDefinition):
    name = 'seda_gps_version_id'
    subject = 'SEDAGpsVersionID'
    object = 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDAGpsAltitude(EntityType):
    u""""""


class seq_alt_archive_unit_archive_unit_ref_id_management_gps_altitude(RelationDefinition):
    name = 'seda_gps_altitude'
    subject = 'SEDAGpsAltitude'
    object = 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDAGpsAltitudeRef(EntityType):
    u""""""


class seq_alt_archive_unit_archive_unit_ref_id_management_gps_altitude_ref(RelationDefinition):
    name = 'seda_gps_altitude_ref'
    subject = 'SEDAGpsAltitudeRef'
    object = 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDAGpsLatitude(EntityType):
    u""""""


class seq_alt_archive_unit_archive_unit_ref_id_management_gps_latitude(RelationDefinition):
    name = 'seda_gps_latitude'
    subject = 'SEDAGpsLatitude'
    object = 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDAGpsLatitudeRef(EntityType):
    u""""""


class seq_alt_archive_unit_archive_unit_ref_id_management_gps_latitude_ref(RelationDefinition):
    name = 'seda_gps_latitude_ref'
    subject = 'SEDAGpsLatitudeRef'
    object = 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDAGpsLongitude(EntityType):
    u""""""


class seq_alt_archive_unit_archive_unit_ref_id_management_gps_longitude(RelationDefinition):
    name = 'seda_gps_longitude'
    subject = 'SEDAGpsLongitude'
    object = 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDAGpsLongitudeRef(EntityType):
    u""""""


class seq_alt_archive_unit_archive_unit_ref_id_management_gps_longitude_ref(RelationDefinition):
    name = 'seda_gps_longitude_ref'
    subject = 'SEDAGpsLongitudeRef'
    object = 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDAGpsDateStamp(EntityType):
    u""""""


class seq_alt_archive_unit_archive_unit_ref_id_management_gps_date_stamp(RelationDefinition):
    name = 'seda_gps_date_stamp'
    subject = 'SEDAGpsDateStamp'
    object = 'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['0..1', '1'], default_cardinality='1',
                      annotable=True)
class SEDAwhen(EntityType):
    u""""""


class custodial_history_item_when(RelationDefinition):
    name = 'seda_when'
    subject = 'SEDAwhen'
    object = 'SEDACustodialHistoryItem'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

class custodial_history_file_data_object_reference_id(RelationDefinition):
    name = 'seda_data_object_reference_id'
    subject = 'SEDACustodialHistoryFile'
    object = ('SEDABinaryDataObject', 'SEDAPhysicalDataObject')
    cardinality = '?*'
    composite = fulltext_container = None
    inlined = True
    constraints = [RQLConstraint('S container C, O container C')]

@seda_profile_element(cardinalities=['1'], default_cardinality='1',
                      annotable=False)
class SEDAAltIsVersionOfArchiveUnitRefId(EntityType):
    u""""""


class is_version_of_alt_is_version_of_archive_unit_ref_id(RelationDefinition):
    name = 'seda_alt_is_version_of_archive_unit_ref_id'
    subject = 'SEDAIsVersionOf'
    object = 'SEDAAltIsVersionOfArchiveUnitRefId'
    cardinality = '11'
    composite = fulltext_container = 'subject'
    inlined = False
    constraints = []

@seda_profile_element(cardinalities=['1'], default_cardinality='1',
                      annotable=False)
class SEDAAltReplacesArchiveUnitRefId(EntityType):
    u""""""


class replaces_alt_replaces_archive_unit_ref_id(RelationDefinition):
    name = 'seda_alt_replaces_archive_unit_ref_id'
    subject = 'SEDAReplaces'
    object = 'SEDAAltReplacesArchiveUnitRefId'
    cardinality = '11'
    composite = fulltext_container = 'subject'
    inlined = False
    constraints = []

@seda_profile_element(cardinalities=['1'], default_cardinality='1',
                      annotable=False)
class SEDAAltRequiresArchiveUnitRefId(EntityType):
    u""""""


class requires_alt_requires_archive_unit_ref_id(RelationDefinition):
    name = 'seda_alt_requires_archive_unit_ref_id'
    subject = 'SEDARequires'
    object = 'SEDAAltRequiresArchiveUnitRefId'
    cardinality = '11'
    composite = fulltext_container = 'subject'
    inlined = False
    constraints = []

@seda_profile_element(cardinalities=['1'], default_cardinality='1',
                      annotable=False)
class SEDAAltIsPartOfArchiveUnitRefId(EntityType):
    u""""""


class is_part_of_alt_is_part_of_archive_unit_ref_id(RelationDefinition):
    name = 'seda_alt_is_part_of_archive_unit_ref_id'
    subject = 'SEDAIsPartOf'
    object = 'SEDAAltIsPartOfArchiveUnitRefId'
    cardinality = '11'
    composite = fulltext_container = 'subject'
    inlined = False
    constraints = []

@seda_profile_element(cardinalities=['1'], default_cardinality='1',
                      annotable=False)
class SEDAAltReferencesArchiveUnitRefId(EntityType):
    u""""""


class references_alt_references_archive_unit_ref_id(RelationDefinition):
    name = 'seda_alt_references_archive_unit_ref_id'
    subject = 'SEDAReferences'
    object = 'SEDAAltReferencesArchiveUnitRefId'
    cardinality = '11'
    composite = fulltext_container = 'subject'
    inlined = False
    constraints = []

class alt_is_version_of_archive_unit_ref_id_data_object_reference(RelationDefinition):
    name = 'seda_data_object_reference'
    subject = 'SEDADataObjectReference'
    object = 'SEDAAltIsVersionOfArchiveUnitRefId'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['1'], default_cardinality='1',
                      annotable=False)
class SEDARepositoryArchiveUnitPID(EntityType):
    u""""""


class alt_is_version_of_archive_unit_ref_id_repository_archive_unit_pid(RelationDefinition):
    name = 'seda_repository_archive_unit_pid'
    subject = 'SEDARepositoryArchiveUnitPID'
    object = ('SEDAAltIsPartOfArchiveUnitRefId', 'SEDAAltIsVersionOfArchiveUnitRefId', 'SEDAAltReferencesArchiveUnitRefId', 'SEDAAltReplacesArchiveUnitRefId', 'SEDAAltRequiresArchiveUnitRefId')
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

@seda_profile_element(cardinalities=['1'], default_cardinality='1',
                      annotable=False)
class SEDARepositoryObjectPID(EntityType):
    u""""""


class alt_is_version_of_archive_unit_ref_id_repository_object_pid(RelationDefinition):
    name = 'seda_repository_object_pid'
    subject = 'SEDARepositoryObjectPID'
    object = ('SEDAAltIsPartOfArchiveUnitRefId', 'SEDAAltIsVersionOfArchiveUnitRefId', 'SEDAAltReferencesArchiveUnitRefId', 'SEDAAltReplacesArchiveUnitRefId', 'SEDAAltRequiresArchiveUnitRefId')
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

class alt_replaces_archive_unit_ref_id_data_object_reference(RelationDefinition):
    name = 'seda_data_object_reference'
    subject = 'SEDADataObjectReference'
    object = 'SEDAAltReplacesArchiveUnitRefId'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

class alt_requires_archive_unit_ref_id_data_object_reference(RelationDefinition):
    name = 'seda_data_object_reference'
    subject = 'SEDADataObjectReference'
    object = 'SEDAAltRequiresArchiveUnitRefId'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

class alt_is_part_of_archive_unit_ref_id_data_object_reference(RelationDefinition):
    name = 'seda_data_object_reference'
    subject = 'SEDADataObjectReference'
    object = 'SEDAAltIsPartOfArchiveUnitRefId'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

class alt_references_archive_unit_ref_id_data_object_reference(RelationDefinition):
    name = 'seda_data_object_reference'
    subject = 'SEDADataObjectReference'
    object = 'SEDAAltReferencesArchiveUnitRefId'
    cardinality = '1?'
    composite = fulltext_container = 'object'
    inlined = True
    constraints = []

