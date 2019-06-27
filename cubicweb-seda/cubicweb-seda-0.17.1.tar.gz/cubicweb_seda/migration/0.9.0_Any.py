# coding: utf-8
from cubicweb_seda import iter_all_rdefs

for rdef, role in iter_all_rdefs(schema, 'SEDAArchiveTransfer'):
    if role == 'subject':
        target_etype = rdef.subject
    else:
        target_etype = rdef.object
    if target_etype == 'SEDAArchiveUnit':
        sync_schema_props_perms((rdef.subject, rdef.rtype, rdef.object))

sync_schema_props_perms('clone_of')

add_relation_type('code_keyword_type')

scheme = cnx.find('ConceptScheme', title=u'SEDA 2 : Types de mot-clé').one()
with cnx.deny_all_hooks_but():
    scheme.cw_set(title=u'SEDA : Types de mot-clé')
    cnx.commit()
    cnx.execute('SET L language_code "seda" WHERE L label_of C, C in_scheme CS, CS eid %(cs)s',
                {'cs': scheme.eid})
    cnx.commit()

for concept in scheme.reverse_in_scheme:
    label = {
        'corpname': u'Collectivité',
        'famname': u'Nom de famille',
        'geogname': u'Nom géographique',
        'name': u'Nom',
        'occupation': u'Fonction',
        'persname': u'Nom de personne',
        'subject': u'Mot-matière',
        'genreform': u'Typologie documentaire',
        'function': u'Activité',
    }[concept.label('seda')]
    cnx.create_entity('Label', label_of=concept, label=label,
                      kind=u'preferred', language_code=u'fr')

cnx.commit()


