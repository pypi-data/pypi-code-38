# Recibe un verbo y devuelve su conjugación en presente indicativo.
# <verb> verbo a conjugar debe ser una cadena de caracteres terminada en
# uno de {ar, er, ir, ár, ér, ír}. De no ser asi devuelve un vector vacio.
# <force_conj>: valor booleano. Si es verdadero fuerza a que el verbo
# sea conjugado por la función sin recurrir al diccionario de irregulares
# (aún si el mismo se encontrase allí)

# @Vendors
import fnmatch

# @Helpers
from .irregularVerbCastHelper import (
    irregular_cast_group_01, 
    irregular_cast_group_02, 
    irregular_cast_group_03, 
    irregular_cast_group_04_b, 
    irregular_cast_group_06, 
    irregular_cast_group_07, 
    irregular_cast_group_08_a, 
    irregular_cast_group_09, 
    irregular_cast_group_10, 
    irregular_cast_group_11, 
    irregular_cast_group_12_a, 
    irregular_cast_group_13_a
)

def presente_conj(verb, force_conj, mode, configs):
    irregular_verb_exceptions = configs['irregular_verb_exceptions'] 
    irregular_verb_groups = configs['irregular_verb_groups']
    config = configs['config']
    if not any(fnmatch.fnmatch(verb, suffix) for suffix in ['*ar', '*er', '*ir', '*ár', '*ér', '*ír']):
        return ['', '', '', '', '', '']
    verb_conj = []
    suffix_conj = []
    base_verb = verb[0:len(verb)-2]
    ncer_flag = False
    ger_gir_flag = False
    guir_flag = False
    if not verb in irregular_verb_exceptions.keys() or force_conj:
        if fnmatch.fnmatch(verb, '*ar') or fnmatch.fnmatch(verb, '*ár'):
            if mode == 0:
                suffix_conj = ['o', 'ás', 'a', 'amos', 'áis', 'an']
            else:
                suffix_conj = ['o', 'as', 'a', 'amos', 'áis', 'an']
        if fnmatch.fnmatch(verb, '*er') or fnmatch.fnmatch(verb, '*ér'):
            if fnmatch.fnmatch(verb, '*ncer'):
                ncer_flag = True
            if fnmatch.fnmatch(verb, '*ger'):
                ger_gir_flag = True
            if mode == 0:
                suffix_conj = ['o', 'és', 'e', 'emos', 'éis', 'en']
            else:
                suffix_conj = ['o', 'es', 'e', 'emos', 'éis', 'en']
        if fnmatch.fnmatch(verb, '*ir') or fnmatch.fnmatch(verb, '*ír'):
            if fnmatch.fnmatch(verb, '*gir'):
                ger_gir_flag = True
            if fnmatch.fnmatch(verb, '*guir'):
                guir_flag = True
            if mode == 0:
                suffix_conj = ['o', 'ís', 'e', 'imos', 'ís', 'en']
            else:
                suffix_conj = ['o', 'es', 'e', 'imos', 'ís', 'en']
    else:
        return irregular_verb_exceptions[verb]['pres']
    for i in range(0, 6):
        base_form = base_verb

        # Conjugación sobre singular no modo argentino (vos en lugar de tú)
        # Conjugación sobre singular con modo argentino activado
        # Conjugación sobre plural de la tercera persona.
        if (i in config['singular'] and not mode == 0) or (mode == 0 and i in config['singular'] and not i in config['segunda_persona']) or (i in config['plural'] and i in config['tercera_persona']):

        # Cambio a la forma base según grupo 01 de los verbos irregulares.
        # e --> ie
            base_form = irregular_cast_group_01(verb, base_form, irregular_verb_groups)
        # Cambio a la forma base según grupo 02 de los verbos irregulares.
        # o --> ue
            base_form = irregular_cast_group_02(verb, base_form, irregular_verb_groups)
        # Cambio a la forma base según grupo 06 de los verbos irregulares.
        # e --> i
            base_form = irregular_cast_group_06(verb, base_form, irregular_verb_groups)
        # Cambio a la forma base según grupo 06 de los verbos irregulares.
        # e --> i
            base_form = irregular_cast_group_07(verb, base_form, irregular_verb_groups)

        # Cambio a la forma base según grupo 08 de los verbos irregulares.
        # e --> ie
            base_form = irregular_cast_group_08_a(verb, base_form, irregular_verb_groups)
        #    base_form = irregular_cast_group_08_b(verb, base_form)
        #    base_form = irregular_cast_group_09(verb, base_form)

        # Cambio a la forma base según grupo 09 de los verbos irregulares.
        # u --> ue
            base_form = irregular_cast_group_09(verb, base_form, irregular_verb_groups)

        # Cambio a la forma base según grupo 09 de los verbos irregulares.
        # i --> ie
            base_form = irregular_cast_group_10(verb, base_form, irregular_verb_groups)

        # Cambio a la forma base según grupo 09 de los verbos irregulares.
        # i --> y
            base_form = irregular_cast_group_11(verb, base_form, irregular_verb_groups)

        # Cambio a la forma base según grupo 09 de los verbos irregulares.
        # o --> ue
            base_form = irregular_cast_group_12_a(verb, base_form, irregular_verb_groups)

        # Cambia la forma base de los verbos terminados en 'decir'
        # 'dec' -> 'dic'
            if fnmatch.fnmatch(verb, '*decir') and not i in config['primera_persona']:
                base_form = base_form.replace("dec", "dic")

        # Conjugación sobre primera persona singular.
        if i in config['singular'] and i in config['primera_persona']:
            # Si el verbo infinitivo termina en ncer se modifica el singular
            # de la primera persona:
            # c --> z
            if ncer_flag:
                base_form = base_form[:len(base_form)-1] + 'z'

            # Si el verbo infinitivo termina en ger/gir se modifica el singular
            # de la primera persona:
            # g --> j
            if ger_gir_flag:
                base_form = base_form[:len(base_form)-1] + 'j'

            # Si el verbo infinitivo termina en guir se modifica el singular
            # de la primera persona:
            # gu --> g
            if guir_flag:
                base_form = base_form[:len(base_form)-2] + 'g'

            # Si el verbo infinitivo termina en 'decir' se modifica el singular
            # de la primera persona
            if fnmatch.fnmatch(verb, '*decir'):
                base_form = base_form.replace('dec', 'dig')

            # Cambia la forma base para los verbos terminados en hacer.
            # c --> g
            if fnmatch.fnmatch(verb, '*hacer'):
                base_form = base_form[:len(base_form)-1] + 'g'

        # Cambio a la forma base según grupo 03 de los verbos irregulares.
        # c --> zc
            base_form = irregular_cast_group_03(verb, base_form, irregular_verb_groups)
        # Cambio a la forma base según grupo 04 de los verbos irregulares.
        # c --> zc
            base_form = irregular_cast_group_04_b(verb, base_form, irregular_verb_groups)
        # Cambio a la forma base según grupo 13 de los verbos irregulares.
        # base_verb + g
            base_form = irregular_cast_group_13_a(verb, base_form, irregular_verb_groups)


        verb_conj.append(base_form + suffix_conj[i])

        # Salvedad para el caso puntual del verbo delinquir.
        if verb == 'delinquir' and i in config['primera_persona'] and i in config['singular']:
            verb_conj[-1] = 'delinco'
    return verb_conj
