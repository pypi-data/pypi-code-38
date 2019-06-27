# coding: utf-8

for e in rql('Any X groupby X WHERE X container C HAVING COUNT(C) > 1').entities():
    container = max(c.eid for c in e.container)
    e.cw_set(container=None)
    e.cw_set(container=container)
commit()

sync_schema_props_perms('container')

scheme = cnx.find('ConceptScheme', title=u'SEDA 2 : Status légaux').one()
for old_label, new_label in [(u'Archive publique', u'Archives publiques'),
                             (u'Archive privée', u'Archives privées')]:
    rql('SET X label %(new_label)s WHERE X label %(old_label)s, '
        'X label_of C, C in_scheme S, S eid %(s)s',
        {'s': scheme.eid, 'new_label': new_label, 'old_label': old_label})

commit()

scheme = cnx.find('ConceptScheme', title=u'SEDA : Niveaux de description').one()
for old_label, new_label in [(u"Dossier l'intérieur d'une série organique", u'Dossier'),
                             (u'Item', u'Pièce')]:
    rql('SET X label %(new_label)s WHERE X label %(old_label)s, '
        'X label_of C, C in_scheme S, S eid %(s)s',
        {'s': scheme.eid, 'new_label': new_label, 'old_label': old_label})
    # don't care about migrating updated definition for now
commit()


sync_schema_props_perms('seda_description_level')
