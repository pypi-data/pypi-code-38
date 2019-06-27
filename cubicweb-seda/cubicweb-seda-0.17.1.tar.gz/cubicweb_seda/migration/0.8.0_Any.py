from cubicweb_seda.dataimport import import_seda_schemes, LCSV_FILES

add_entity_type('SEDAMessageDigestAlgorithmCodeListVersion')
drop_relation_type('seda_message_digest_algorithm_code_list_version')
add_entity_type('SEDAFileFormatCodeListVersion')
drop_relation_type('seda_file_format_code_list_version')

add_entity_type('SEDAAcquisitionInformationCodeListVersion')
add_entity_type('SEDAAcquisitionInformation')

add_entity_type('SEDAOriginatingAgencyIdentifier')
add_entity_type('SEDASubmissionAgencyIdentifier')

add_entity_type('SEDALegalStatus')

sync_schema_props_perms('seda_algorithm')
sync_schema_props_perms('seda_format_id_to')

for etype in ('SEDArestrictionRuleIdRef',
              'SEDArestrictionValue',
              'SEDArestrictionEndDate'):
    drop_entity_type(etype)

lcsv_files = [file_def for file_def in LCSV_FILES
              if file_def[-1] in ('legal_status.csv', 'digest_algorithms.csv', 'dissemination.csv')]
import_seda_schemes(cnx, lcsv_files=lcsv_files)

drop_relation_type('seda_reply_code_list_version')
add_relation_definition('SEDAArchiveTransfer', 'clone_of', 'SEDAArchiveTransfer')
