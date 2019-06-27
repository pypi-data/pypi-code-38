sync_schema_props_perms('language_code')

scheme = cnx.find('ConceptScheme', title=u'Langues (ISO-639-3)').one()
with cnx.deny_all_hooks_but('metadata'):
    rset = cnx.execute(
        'Any C, L, LL WHERE L label_of C, L language_code "seda-2", L label LL,'
        'C in_scheme CS, CS eid %(cs)s', {'cs': scheme.eid})
    for i, concept in enumerate(rset.entities()):
        label = rset.get_entity(i, 1)
        label.cw_set(language_code=u'seda')
        cnx.create_entity('Label', label_of=concept, language_code='seda-02',
                          label=label.label[:2])
    commit()

