# @Utils
from nlp_model_gen.utils.objectUtils import fillDict

# @Helpers
from .presenteIndicativoHelper import presente_conj
from .preteritoPerfSimpleHelper import preterito_perf_simple_conj
from .preteritoImperfHelper import preterito_imperf_conj
from .futuroSimpleHelper import futuro_simple_conj
from .condicionalSimpleAHelper import condicional_simple_A_conj
from .condicionalSimpleBHelper import condicional_simple_B_conj
from .imperativoAHelper import imperativo_A_conj
from .imperativoBHelper import imperativo_B_conj
from .imperativoCHelper import imperativo_C_conj
from .participioHelper import participio
from .gerundioHelper import gerundio

def apply_conjugation_or_exception(exceptions, conjugation_func, verb, mode, configs):
    return exceptions if exceptions is not None else conjugation_func(verb, True, mode, configs)

# Recibe un verbo y las excepciones en sus conjugaciones. En los casos en los que 
# no existe una excepción se utilizaran los helpers para cada tiempo de conjugación.
def get_irregular_verb_template(verb, irregularDict, mode, verb_options, configs):
    ger, part, pres, pret_perf, pret_imperf, fut, impA, impB, impC, condA, condB, alternatives = fillDict(verb_options, ['ger', 'part', 'pres', 'pret_perf', 'pret_imperf', 'fut', 'impA', 'impB', 'impC', 'condA', 'condB', 'alternatives'])
    template = {
        'inf': [verb],
        'ger': apply_conjugation_or_exception(ger, gerundio, verb, mode, configs),
        'part': apply_conjugation_or_exception(part, participio, verb, mode, configs),
        'pres': apply_conjugation_or_exception(pres, presente_conj, verb, mode, configs),
        'pret_perf': apply_conjugation_or_exception(pret_perf, preterito_perf_simple_conj, verb, mode, configs),
        'pret_imperf': apply_conjugation_or_exception(pret_imperf, preterito_imperf_conj, verb, mode, configs),
        'fut': apply_conjugation_or_exception(fut, futuro_simple_conj, verb, mode, configs),
        'impA': apply_conjugation_or_exception(impA, imperativo_A_conj, verb, mode, configs),
        'impB': apply_conjugation_or_exception(impB, imperativo_B_conj, verb, mode, configs),
        'impC': apply_conjugation_or_exception(impC, imperativo_C_conj, verb, mode, configs),
        'condA': apply_conjugation_or_exception(condA, condicional_simple_A_conj, verb, mode, configs),
        'condB': apply_conjugation_or_exception(condB, condicional_simple_B_conj, verb, mode, configs),
    }
    if mode == 0 and alternatives is not None:
        for alternative in alternatives:
            template[alternative['key']][alternative['person']] = alternative['value']
    irregularDict[verb] = template

# Este modulo se utiliza para generar los casos excepcionales de verbos irregulares.
def get_irregular_verbs(irregularDict, mode, configs):
    irregular_verb_exceptions_config = configs['irregular_verb_exceptions_config']
    for verb_exception in irregular_verb_exceptions_config:
        get_irregular_verb_template(verb_exception['key'], irregularDict, mode, verb_exception['exceptions'], configs)
    return irregularDict
