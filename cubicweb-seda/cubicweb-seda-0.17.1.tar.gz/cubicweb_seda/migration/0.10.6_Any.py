scheme = cnx.find('ConceptScheme', title=u'Types MIME').one()
sql("""
UPDATE cw_label SET cw_language_code = 'seda'
FROM cw_concept, in_scheme_relation
WHERE in_scheme_relation.eid_to = {}
AND cw_concept.cw_eid = in_scheme_relation.eid_from
AND cw_label_of = cw_concept.cw_eid
AND cw_language_code = 'seda-2'
""".format(scheme.eid))

