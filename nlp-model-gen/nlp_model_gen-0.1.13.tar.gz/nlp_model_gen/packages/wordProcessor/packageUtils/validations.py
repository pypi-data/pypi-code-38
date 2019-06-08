# @Vendors
from schema import Schema, And, Use, Optional

# @Constants
from nlp_model_gen.constants.constants import WORD_PROCESSOR_SCHEMAS

conjugator_general_config_schema = Schema({
    'singular': [And(Use(int))],
    'plural': [And(Use(int))],
    'primera_persona': [And(Use(int))],
    'segunda_persona': [And(Use(int))],
    'tercera_persona': [And(Use(int))],
    'verb_suffixes': [And(str, Use(str.lower), len)],
    'irregular_suffix_exceptions': [And(str, Use(str.lower), len)],
    'empty_conj_dict': {
        'inf': And([And(lambda s: s is '')], lambda arr: len(arr) == 1),
        'ger' : And([And(lambda s: s is '')], lambda arr: len(arr) == 1),
        'part': And([And(lambda s: s is '')], lambda arr: len(arr) == 3),
        'pres': And([And(lambda s: s is '')], lambda arr: len(arr) == 6),
        'pret_perf': And([And(lambda s: s is '')], lambda arr: len(arr) == 6),
        'pret_imperf': And([And(lambda s: s is '')], lambda arr: len(arr) == 6),
        'fut': And([And(lambda s: s is '')], lambda arr: len(arr) == 6),
        'impA': And([And(lambda s: s is '')], lambda arr: len(arr) == 6),
        'impB': And([And(lambda s: s is '')], lambda arr: len(arr) == 6),
        'impC': And([And(lambda s: s is '')], lambda arr: len(arr) == 6),
        'condA': And([And(lambda s: s is '')], lambda arr: len(arr) == 6),
        'condB': And([And(lambda s: s is '')], lambda arr: len(arr) == 6)
    },
    'table_headers': And(lambda arr: ['', 'Presente', 'Preterito imperfecto', 'Preterito perfecto simple', 'Condicional'] in arr and ['', 'Futuro', 'pret_imperf subjuntivo', 'Imperativo_A', 'Imperativo_B', 'Imperativo_C'] in arr and ['', ''] in arr),
    'row_headers': And(lambda arr: ['yo', 'tu/vos', 'el', 'nos', 'vosotros', 'ellos'] in arr and ['Infinitivo', 'Gerundio', 'Participio 1', 'Participio 2', 'Participio 3'] in arr)
})

conjugator_verb_exceptions_schema = Schema({
    'key': And(str, Use(str.lower), len),
    'exceptions': {
        Optional('inf'): [And(str, Use(str.lower))],
        Optional('ger'): [And(str, Use(str.lower))],
        Optional('part'): [And(str, Use(str.lower))],
        Optional('pres'): [And(str, Use(str.lower))],
        Optional('pret_perf'): [And(str, Use(str.lower))],
        Optional('pret_imperf'): [And(str, Use(str.lower))],
        Optional('fut'): [And(str, Use(str.lower))],
        Optional('impA'): [And(str, Use(str.lower))],
        Optional('impB'): [And(str, Use(str.lower))],
        Optional('impC'): [And(str, Use(str.lower))],
        Optional('condA'): [And(str, Use(str.lower))],
        Optional('condB'): [And(str, Use(str.lower))],
        Optional('alternatives'): [{'key': And(str, Use(str.lower), len), 'person': And(Use(int)), 'value': And(str, Use(str.lower))}]
    }
})

conjugator_verb_groups_schema = Schema({
    'irregular_verbs_grupo_01_ar': [And(str, len)],
    'irregular_verbs_grupo_01_er': [And(str, len)],
    'irregular_verbs_grupo_01_ir': [And(str, len)],
    'irregular_verbs_grupo_02_ar': [And(str, len)],
    'irregular_verbs_grupo_02_er': [And(str, len)],
    'irregular_verbs_grupo_03_acer': [And(str, len)],
    'irregular_verbs_grupo_03_ecer': [And(str, len)],
    'irregular_verbs_grupo_03_ocer': [And(str, len)],
    'irregular_verbs_grupo_03_ucer': [And(str, len)],
    'irregular_verbs_grupo_04_ducir': [And(str, len)],
    'irregular_verbs_grupo_05_er': [And(str, len)],
    'irregular_verbs_grupo_05_nir': [And(str, len)],
    'irregular_verbs_grupo_05_ullir': [And(str, len)],
    'irregular_verbs_grupo_06_ir': [And(str, len)],
    'irregular_verbs_grupo_07_enir': [And(str, len)],
    'irregular_verbs_grupo_07_eir': [And(str, len)],
    'irregular_verbs_grupo_08_ir': [And(str, len)],
    'irregular_verbs_grupo_09_u': [And(str, len)],
    'irregular_verbs_grupo_10_irir': [And(str, len)],
    'irregular_verbs_grupo_11_uir': [And(str, len)],
    'irregular_verbs_grupo_12_o': [And(str, len)],
    'irregular_verbs_grupo_13_aler': [And(str, len)],
    'irregular_verbs_grupo_13_alir': [And(str, len)]
})

fuzzy_genetator_config_schema = Schema({
    'char_confusions': {str: [And(str)]},
    'transformations': [And(str, lambda s: s in ['rnd_confuse_char',  'rnd_char_del', 'rnd_char_change', 'rnd_duplicate_char'])],
    'char_confusions_max_length': And(Use(int), lambda n: n > 0)
})

noun_conversor_config_schema = Schema({
    Optional('nacionalidades'): [And(str, len)],
    'groups': [{ 
        'suffixes': [And(str, len)],
        'replacement': And(str),
        Optional('backReplacements'): [{'key': And(str, len), 'backCrop': And(Use(int), lambda n: n > 0), 'replacement': And(str)}]
    }],
    'exceptions': [And(str, len)] 
})

schemas = dict({})
schemas[WORD_PROCESSOR_SCHEMAS['CONJ_GENERAL_CFG']] = conjugator_general_config_schema
schemas[WORD_PROCESSOR_SCHEMAS['CONJ_IRR_GROUPS']] = conjugator_verb_groups_schema
schemas[WORD_PROCESSOR_SCHEMAS['CONJ_EXCEPTIONS']] = conjugator_verb_exceptions_schema
schemas[WORD_PROCESSOR_SCHEMAS['FUZZY_GENERAL_CFG']] = fuzzy_genetator_config_schema
schemas[WORD_PROCESSOR_SCHEMAS['NOUN_CONV_GENERAL_CFG']] = noun_conversor_config_schema

def validate_config(config_type, config):
    if not config_type in schemas.keys():
        return False
    return schemas[config_type].is_valid(config)
