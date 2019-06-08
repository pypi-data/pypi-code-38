# Recibe un verbo y devuelve su conjugación en preterito imperfecto subjuntivo.
# <verb> verbo a conjugar debe ser una cadena de caracteres terminada en
# uno de {ar, er, ir, ár, ér, ír}. De no ser asi devuelve un vector vacio.
# <force_conj>: valor booleano. Si es verdadero fuerza a que el verbo
# sea conjugado por la función sin recurrir al diccionario de irregulares
# (aún si el mismo se encontrase allí)

# @Vendors
import fnmatch

# @Helpers
from .irregularVerbCastHelper import (
    irregular_cast_group_04_a,
    irregular_cast_group_06,
    irregular_cast_group_07,
    irregular_cast_group_08_b,
    irregular_cast_group_12_b
)

def condicional_simple_B_conj(verb, force_conj, mode, configs):
    irregular_verb_exceptions = configs['irregular_verb_exceptions'] 
    irregular_verb_groups = configs['irregular_verb_groups']
    if not any(fnmatch.fnmatch(verb, suffix) for suffix in ['*ar', '*er', '*ir', '*ár', '*ér', '*ír']):
        return ['', '', '', '', '', '']
    verb_conj = []
    suffix_conj = []
    base_verb = verb[0:len(verb)-2]
    if not verb in irregular_verb_exceptions.keys() or force_conj:
        if fnmatch.fnmatch(verb, '*ar') or fnmatch.fnmatch(verb, '*ár'):
            suffix_conj = ['ase', 'ases', 'ase', 'ásemos', 'aseis', 'asen']
        if fnmatch.fnmatch(verb, '*er') or fnmatch.fnmatch(verb, '*ér'):
            suffix_conj = ['iese', 'ieses', 'iese', 'iésemos', 'ieseis', 'iesen']
        if fnmatch.fnmatch(verb, '*ir') or fnmatch.fnmatch(verb, '*ír'):
            suffix_conj = ['iese', 'ieses', 'iese', 'iésemos', 'ieseis', 'iesen']
    else:
        return irregular_verb_exceptions[verb]['condB']
    for i in range(0, 6):
        if  fnmatch.fnmatch(verb, '*decir'):
            base_form = base_verb.replace('dec', 'dij')
        elif  fnmatch.fnmatch(verb, '*hacer'):
            base_form = base_verb.replace('hac', 'hic')
        else:
            base_form = base_verb

        # Para los verbos en el grupo 04 se aplica el cambio de base
        # definido para el pret imperfecto subjuntivo.
        # c --> j
        base_form = irregular_cast_group_04_a(verb, base_form, irregular_verb_groups)

        # Para los verbos en el grupo 06 se aplica el cambio de base
        # definido para el pret imperfecto subjuntivo.
        # e --> i
        base_form = irregular_cast_group_06(verb, base_form, irregular_verb_groups)

        # Para los verbos en el grupo 07 se aplica el cambio de base
        # definido para el pret imperfecto subjuntivo.
        # e --> i
        base_form = irregular_cast_group_07(verb, base_form, irregular_verb_groups)

        # Para los verbos en el grupo 08 se aplica el cambio de base
        # definido para el pret imperfecto subjuntivo.
        # e --> i
        base_form = irregular_cast_group_08_b(verb, base_form, irregular_verb_groups)

        # Para los verbos en el grupo 12 se aplica el cambio de base
        # definido para el pret imperfecto subjuntivo.
        # o --> u
        base_form = irregular_cast_group_12_b(verb, base_form, irregular_verb_groups)

        # Para los verbos terminados en 'uir' agrega una 'y' a la forma
        # base.
        if fnmatch.fnmatch(verb, '*uir') and not verb in irregular_verb_groups['irregular_verbs_grupo_06_ir']:
            base_form += 'y'


        # Elimina la i del sufijo para los verbos del grupo 04, 05 y los
        # terminados en 'uir'.
        if verb in irregular_verb_groups['irregular_verbs_grupo_04_ducir'] or verb in irregular_verb_groups['irregular_verbs_grupo_05_er'] or verb in irregular_verb_groups['irregular_verbs_grupo_05_nir'] or verb in irregular_verb_groups['irregular_verbs_grupo_05_ullir'] or verb in irregular_verb_groups['irregular_verbs_grupo_07_eir'] or verb in irregular_verb_groups['irregular_verbs_grupo_07_enir'] or (fnmatch.fnmatch(verb, '*uir') and not verb in irregular_verb_groups['irregular_verbs_grupo_06_ir']) or fnmatch.fnmatch(verb, '*decir'):
            if fnmatch.fnmatch(suffix_conj[i], 'i*'):
                suffix_conj[i] = suffix_conj[i][1:]

        verb_conj.append(base_form + suffix_conj[i])

    return verb_conj
