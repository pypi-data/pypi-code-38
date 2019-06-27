from cubicweb.schema import META_RTYPES

with cnx.deny_all_hooks_but('metadata'):
    scheme = cnx.find('ConceptScheme', title=u'SEDA : Niveaux de description').one()
    for concept in scheme.reverse_in_scheme:
        seda_label = concept.labels['seda']
        seda2_label = {'recordgrp': u'RecordGrp',
                       'subgrp': u'SubGrp'}.get(seda_label, seda_label.capitalize())
        cnx.create_entity('Label', label_of=concept,
                          kind=u'preferred', language_code=u'seda-2',
                          label=seda2_label)
    commit()

sync_schema_props_perms(('SEDAArchiveTransfer', 'title', 'String'))

with cnx.deny_all_hooks_but():
    rql('SET X user_annotation XI + "\n" + XUA WHERE X id XI, X user_annotation XUA, '
        'NOT X user_annotation NULL')
    rql('SET X user_annotation XI WHERE X id XI, '
        'X user_annotation NULL')
    commit()

for etype in ('SEDAArchiveUnit', 'SEDABinaryDataObject', 'SEDAPhysicalDataObject'):
    drop_attribute(etype, 'id')
    sync_schema_props_perms((etype, 'user_annotation', 'String'))

SKIP_RTYPES = set(('seda_content', 'container')) | META_RTYPES
for rschema, targets, role in schema.eschema('SEDAContent').relation_definitions():
    if rschema.type in SKIP_RTYPES:
        continue
    for target in targets:
        if role == 'subject':
            add_relation_definition('SEDASeqAltArchiveUnitArchiveUnitRefIdManagement',
                                    rschema.type, target, ask_confirm=False)
        else:
            add_relation_definition(target, rschema.type,
                                    'SEDASeqAltArchiveUnitArchiveUnitRefIdManagement',
                                    ask_confirm=False)
    with cnx.deny_all_hooks_but():
        if role == 'subject':
            rql('SET SEQ {0} X WHERE C seda_content SEQ, C {0} X'.format(rschema),
                ask_confirm=False)
        else:
            rql('SET X {0} SEQ WHERE C seda_content SEQ, X {0} C'.format(rschema),
                ask_confirm=False)
        commit(ask_confirm=False)
drop_entity_type('SEDAContent')

add_cube('eac')
if 'Agent' not in fsschema:
    drop_entity_type('Agent')

add_attribute('SEDAKeyword', 'keyword_content')
with cnx.deny_all_hooks_but():
    rql('SET KW keyword_content C WHERE KWC seda_keyword_content KW, KWC keyword_content C')
commit()
drop_entity_type('SEDAKeywordContent')
