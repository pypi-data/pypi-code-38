# Recibe un verbo y devuelve su conjugación en futuro indicativo.
# <verb> verbo a conjugar debe ser una cadena de caracteres terminada en
# uno de {ar, er, ir, ár, ér, ír}. De no ser asi devuelve un vector vacio.
# <force_conj>: valor booleano. Si es verdadero fuerza a que el verbo
# sea conjugado por la función sin recurrir al diccionario de irregulares
# (aún si el mismo se encontrase allí)

# @Vendors
import fnmatch

# @Helpers
from .irregularVerbCastHelper import irregular_cast_group_13_b

def futuro_simple_conj(verb, force_conj, mode, configs):
    irregular_verb_exceptions = configs['irregular_verb_exceptions'] 
    irregular_verb_groups = configs['irregular_verb_groups']
    if not any(fnmatch.fnmatch(verb, suffix) for suffix in ['*ar', '*er', '*ir', '*ár', '*ér', '*ír']):
        return ['', '', '', '', '', '']
    verb_conj = []
    suffix_conj = []
    if fnmatch.fnmatch(verb, '*hacer'):
        verb = verb.replace('hacer', 'hacar')
    base_verb = verb[0:len(verb)-2]
    if not verb in irregular_verb_exceptions.keys() or force_conj:
        if fnmatch.fnmatch(verb, '*ar') or fnmatch.fnmatch(verb, '*ár'):
            suffix_conj = ['aré', 'arás', 'ará', 'aremos', 'aréis', 'arán']
        if fnmatch.fnmatch(verb, '*er') or fnmatch.fnmatch(verb, '*ér'):
            suffix_conj = ['eré', 'erás', 'erá', 'eremos', 'eréis', 'erán']
        if fnmatch.fnmatch(verb, '*ir') or fnmatch.fnmatch(verb, '*ír'):
            suffix_conj = ['iré', 'irás', 'irá', 'iremos', 'iréis', 'irán']
    else:
        return irregular_verb_exceptions[verb]['fut']
    for suffix in suffix_conj:
        if  fnmatch.fnmatch(verb, '*decir'):
            base_form = base_verb.replace('dec', 'd')
        elif fnmatch.fnmatch(verb, '*hacar'):
            base_form = base_verb.replace('hac', 'h')
        else:
            base_form = base_verb

        # Mofifica el verbo base para los verbos en el grupo 13
        # base_verb + d
        base_form = irregular_cast_group_13_b(verb, base_form, irregular_verb_groups)

        # Elimina la i que resulta en un sobrante para los verbos del
        # grupo 13
        if verb in irregular_verb_groups['irregular_verbs_grupo_13_alir'] or verb in irregular_verb_groups['irregular_verbs_grupo_13_aler']:
            suffix = suffix[1:]

        verb_conj.append(base_form + suffix)
    return verb_conj
