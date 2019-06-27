from __future__ import print_function
from cubicweb_seda.dataimport import LCSV_FILES, import_seda_schemes

# please close your eyes - this is necessary if seda is used by saem else call
# to import_seda_schemes will fail because it will attempt to reuse and existing
# uri. Should be done there but still easier here.
try:
    from cubicweb_saem_ref.site_cubicweb import init_seda_scheme
    init_seda_scheme.func_defaults[0][0] = len(LCSV_FILES) - 1
except ImportError:
    pass

print('filtering language concepts, this will take a while')

seda_02_langs = set((
    'aa', 'ab', 'af', 'ak', 'am', 'ar', 'an', 'as', 'av', 'ae', 'ay', 'az',
    'ba', 'bm', 'be', 'bn', 'bh', 'bi', 'bo', 'bs', 'br', 'bg',
    'ca', 'cs', 'ch', 'ce', 'cu', 'cv', 'co', 'cr', 'cy',
    'da', 'de', 'dv', 'dz',
    'el', 'en', 'eo', 'et', 'ee', 'es', 'eu',
    'fo', 'fa', 'fj', 'fi', 'fr', 'fy', 'ff',
    'ga', 'gl', 'gv', 'gn', 'gu',
    'ht', 'ha', 'he', 'hz', 'hi', 'ho', 'hr', 'hu', 'hy',
    'ig', 'is', 'io', 'ii', 'iu', 'ie', 'ia', 'id', 'ik', 'it',
    'jv', 'ja',
    'ka', 'kl', 'kn', 'ks', 'kr', 'kk', 'km', 'ki', 'ky', 'kv', 'kg', 'ko', 'kj', 'ku', 'kw',
    'lo', 'lv', 'li', 'ln', 'lt', 'lb', 'lu', 'lg',
    'mk', 'mh', 'ml', 'mi', 'mr', 'ms', 'mg', 'mt', 'mn', 'my',
    'na', 'nv', 'nr', 'nd', 'ng', 'ne', 'nn', 'nb', 'no', 'ny', 'nl',
    'oc', 'oj', 'or', 'om', 'os',
    'pa', 'pi', 'pl', 'pt', 'ps'
    'qu',
    'rm', 'ro', 'rn', 'ru', 'rw',
    'sg', 'sa', 'si', 'sk', 'sl', 'se', 'sm', 'sn', 'sd', 'so', 'st', 'sc', 'sr', 'ss', 'su', 'sw', 'sv', 'sq',
    'ty', 'ta', 'tt', 'te', 'tg', 'tl', 'th', 'ti', 'to', 'tn', 'ts', 'tk', 'tr', 'tw',
    'ug', 'uk', 'ur', 'uz',
    've', 'vi', 'vo',
    'wa', 'wo',
    'xh',
    'yi', 'yo',
    'za', 'zu', 'zh',
))

rset = rql(
    'Any X WHERE X in_scheme S, S title "Langues (ISO-639-3)", '
    'L label_of X, L language_code "seda-02", NOT L label IN ({})'
    .format(','.join(repr(code) for code in seda_02_langs)))
print(len(rset), 'concepts to delete')
for i, concept in enumerate(rset.entities()):
    concept.cw_delete()
    if i % 10:
        cnx.commit()


sync_schema_props_perms('user_cardinality')

add_relation_type('file_category')

import_seda_schemes(cnx)

sync_schema_props_perms('seda_mime_type_to')
sync_schema_props_perms('seda_format_id_to')
