# Recibe un verbo y devuelve su conjugación en preterito imperfecto indicativo.
# <verb> verbo a conjugar debe ser una cadena de caracteres terminada en
# uno de {ar, er, ir, ár, ér, ír}. De no ser asi devuelve un vector vacio.
# <force_conj>: valor booleano. Si es verdadero fuerza a que el verbo
# sea conjugado por la función sin recurrir al diccionario de irregulares
# (aún si el mismo se encontrase allí)

# @Vendors
import fnmatch

def preterito_imperf_conj(verb, force_conj, mode, configs):
    irregular_verb_exceptions = configs['irregular_verb_exceptions'] 
    if not any(fnmatch.fnmatch(verb, suffix) for suffix in ['*ar', '*er', '*ir', '*ár', '*ér', '*ír']):
        return ['','','','','','']
    verb_conj = []
    suffix_conj = []
    base_verb = verb[0:len(verb)-2]
    if not verb in irregular_verb_exceptions.keys() or force_conj:
        if fnmatch.fnmatch(verb, '*ar') or fnmatch.fnmatch(verb, '*ár'):
            suffix_conj = ['aba', 'abas', 'aba', 'ábamos', 'abais', 'aban']
        if fnmatch.fnmatch(verb, '*er') or fnmatch.fnmatch(verb, '*ér'):
            suffix_conj = ['ía', 'ías', 'ía', 'íamos', 'íais', 'ían']
        if fnmatch.fnmatch(verb, '*ir') or fnmatch.fnmatch(verb, '*ír'):
            suffix_conj = ['ía', 'ías', 'ía', 'íamos', 'íais', 'ían']
    else:
        return irregular_verb_exceptions[verb]['pret_imperf']
    for suffix in suffix_conj:
        verb_conj.append(base_verb + suffix)
    return verb_conj
