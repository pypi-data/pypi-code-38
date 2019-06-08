# Recibe un verbo y devuelve su gerundio.
# <verb> verbo a conjugar debe ser una cadena de caracteres terminada en
# uno de {ar, er, ir, ár, ér, ír}. De no ser asi devuelve un vector vacio.
# <force_conj>: valor booleano. Si es verdadero fuerza a que el verbo
# sea conjugado por la función sin recurrir al diccionario de irregulares
# (aún si el mismo se encontrase allí)

# @Vendors
import fnmatch

# @Helpers
from .irregularVerbCastHelper import (
    irregular_cast_group_06,
    irregular_cast_group_07,
    irregular_cast_group_11,
    irregular_cast_group_12_b
)

def gerundio(verb, force_conj, mode, configs):
    irregular_verb_exceptions = configs['irregular_verb_exceptions'] 
    irregular_verb_groups = configs['irregular_verb_groups']
    if not any(fnmatch.fnmatch(verb, suffix) for suffix in ['*ar', '*er', '*ir', '*ár', '*ér', '*ír']):
        return ['']
    verb_conj = []
    suffix_conj = []
    base_verb = verb[0:len(verb)-2]
    if not verb in irregular_verb_exceptions.keys() or force_conj:
        if fnmatch.fnmatch(verb, '*ar') or fnmatch.fnmatch(verb, '*ár'):
            suffix_conj = ['ando']
        if fnmatch.fnmatch(verb, '*er') or fnmatch.fnmatch(verb, '*ér'):
            suffix_conj = ['iendo']
        if fnmatch.fnmatch(verb, '*ir') or fnmatch.fnmatch(verb, '*ír'):
            suffix_conj = ['iendo']
    else:
        return irregular_verb_exceptions[verb]['ger']
    for suffix in suffix_conj:
        base_form = base_verb

        # Cambia la forma base del verbo según los dispuesto para el grupo 06.
        # e --> i
        base_form = irregular_cast_group_06(verb, base_form, irregular_verb_groups)

        # Cambia la forma base del verbo según los dispuesto para el grupo 06.
        # e --> i
        base_form = irregular_cast_group_07(verb, base_form, irregular_verb_groups)


        # Cambia la forma base del grupo segun lo dispueto para el grupo 11.
        # base_form + y
        base_form = irregular_cast_group_11(verb, base_form, irregular_verb_groups)

        # Cambia la forma base del grupo segun lo dispueto para el grupo 12.
        # o --> u
        base_form = irregular_cast_group_12_b(verb, base_form, irregular_verb_groups)

        #Para los verbos en el grupo 11 se elimina la i de 'iendo'
        if verb in irregular_verb_groups['irregular_verbs_grupo_11_uir'] or verb in irregular_verb_groups['irregular_verbs_grupo_07_eir'] or verb in irregular_verb_groups['irregular_verbs_grupo_07_enir'] or verb in irregular_verb_groups['irregular_verbs_grupo_05_er'] or verb in irregular_verb_groups['irregular_verbs_grupo_05_nir'] or verb in irregular_verb_groups['irregular_verbs_grupo_05_ullir']:
            suffix = suffix[1:]

        verb_conj.append(base_form + suffix)

    return verb_conj
