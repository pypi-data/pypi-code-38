from cubicweb_seda.dataimport import import_seda_schemes

rql('SET X compat_list CL + ", RNG" WHERE X compat_list CL')
commit(ask_confirm=False)

rql('INSERT SEDAMimeType X: X user_cardinality "0..1", X seda_mime_type_from BDO '
    'WHERE NOT Y seda_mime_type_from BDO')

rql('INSERT SEDAFormatId X: X user_cardinality "0..1", X seda_format_id_from BDO '
    'WHERE NOT Y seda_format_id_from BDO')
commit(ask_confirm=False)

sync_schema_props_perms('seda_mime_type_to')
sync_schema_props_perms('seda_format_id_to')
sync_schema_props_perms('seda_data_object_reference_id')

rql('DELETE CS scheme_relation_type RT WHERE '
    'RT name IN ("seda_language_to", "seda_description_language_to")')
commit(ask_confirm=False)
import_seda_schemes(cnx)
