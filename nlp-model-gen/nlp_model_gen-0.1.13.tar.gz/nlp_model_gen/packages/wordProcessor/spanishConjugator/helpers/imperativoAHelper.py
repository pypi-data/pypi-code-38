# Recibe un verbo y devuelve su conjugación en imperativo.
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
    irregular_cast_group_08_b,
    irregular_cast_group_09,
    irregular_cast_group_10,
    irregular_cast_group_11,
    irregular_cast_group_12_a,
    irregular_cast_group_12_b,
    irregular_cast_group_13_a
)

def imperativo_A_conj(verb, force_conj, mode, configs):
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
    car_flag = False
    zar_flag = False
    guir_flag = False
    guar_flag = False
    if not verb in irregular_verb_exceptions.keys() or force_conj:
        if fnmatch.fnmatch(verb, '*ar') or fnmatch.fnmatch(verb, '*ár'):
            if fnmatch.fnmatch(verb, '*car'):
                car_flag = True
            if fnmatch.fnmatch(verb, '*zar'):
                zar_flag = True
            if fnmatch.fnmatch(verb, '*guar'):
                guar_flag = True
            if fnmatch.fnmatch(verb, '*gar'):
                suffix_conj = ['', 'á', 'ue', 'uemos', 'ad', 'uen']
            else:
                suffix_conj = ['', 'á', 'e', 'emos', 'ad', 'en']
            if mode != 0:
                suffix_conj[1] = 'a'
        if fnmatch.fnmatch(verb, '*er') or fnmatch.fnmatch(verb, '*ér'):
            if fnmatch.fnmatch(verb, '*ncer'):
                ncer_flag = True
            if fnmatch.fnmatch(verb, '*ger'):
                ger_gir_flag = True
            suffix_conj = ['', 'é', 'a', 'amos', 'ed', 'an']
        if fnmatch.fnmatch(verb, '*ir'):
            if fnmatch.fnmatch(verb, '*gir'):
                ger_gir_flag = True
            if fnmatch.fnmatch(verb, '*guir'):
                guir_flag = True
            if mode == 0:
                suffix_conj = ['', 'í', 'a', 'amos', 'id', 'an']
            else:
                suffix_conj = ['', 'e', 'a', 'amos', 'id', 'an']
        if fnmatch.fnmatch(verb, '*ír'):
            if fnmatch.fnmatch(verb, '*gír'):
                ger_gir_flag = True
            if fnmatch.fnmatch(verb, '*guír'):
                guir_flag = True
            if mode == 0:
                suffix_conj = ['', 'eí', 'ía', 'iamos', 'eíd', 'ían']
            else:
                suffix_conj = ['', 'íe', 'ía', 'iamos', 'eíd', 'ían']
    else:
        return irregular_verb_exceptions[verb]['impA']
    verb_conj.append('')
    for i in range(1, 6):
        base_form = base_verb

        # Conjugación sobre singular no modo argentino (vos en lugar de tú)
        # Conjugación sobre singular con modo argentino activado
        # Conjugación sobre plural de la tercera persona.
        if (i in config['singular'] and not mode == 0) or (mode == 0 and i in config['singular'] and not i in config['segunda_persona']) or (i in config['plural'] and i in config['tercera_persona']):

            # Cambio a la forma definida para el grupo de irregulares 01
            # e --> ie
            base_form = irregular_cast_group_01(verb, base_form, irregular_verb_groups)
            # Cambio a la forma definida para el grupo de irregulares 02
            # o --> ue
            base_form = irregular_cast_group_02(verb, base_form, irregular_verb_groups)


        # Conjugación para todas las formas con excepción del singular de
        # la segunda persona.
        if not (i in config['segunda_persona']):

            # Cambio a la forma definida pra el grupo de irregulares 03
            # c --> zc
            base_form = irregular_cast_group_03(verb, base_form, irregular_verb_groups)

            # Cambio a la forma definida para el grupo de irregulares 04,
            # c --> zc
            base_form = irregular_cast_group_04_b(verb, base_form, irregular_verb_groups)

        # Conjugación para todas las formas con excepción del plural de la
        # segunda persona (en modo "vos" se omite también la segunda).
        if mode != 0 and not (i in config['segunda_persona'] and i in config['plural']) or not i in config['segunda_persona']:
            # Cambio según los dispuesto para los verbos del grupo 06.
            # e --> i
            base_form = irregular_cast_group_06(verb, base_form, irregular_verb_groups)


            # Cambio según los dispuesto para los verbos del grupo 07.
            # e --> i
            base_form = irregular_cast_group_07(verb, base_form, irregular_verb_groups)

            # Cambio según los dispuesto para los verbos del grupo 10.
            # e --> ie
            base_form = irregular_cast_group_10(verb, base_form, irregular_verb_groups)

            # Cambio a la forma base según grupo 09 de los verbos irregulares.
            # i --> y
            base_form = irregular_cast_group_11(verb, base_form, irregular_verb_groups)

        # Conjugación para todas las formas con excepción del plural de la
        # segunda y primea persona (en modo "vos" se omite también la segunda singular).
        if (not mode == 0 and (i in config['singular'] or i in config['tercera_persona'])) or (mode == 0 and ((i in config['singular'] and not i in config['segunda_persona']) or i in config['tercera_persona'])):

            # Cambio según los dispuesto para los verbos del grupo 08.
            # e --> ie
            base_form = irregular_cast_group_08_a(verb, base_form, irregular_verb_groups)

            # Cambio según los dispuesto para los verbos del grupo 12.
            # o --> u
            base_form = irregular_cast_group_12_a(verb, base_form, irregular_verb_groups)

        # Conjugación para tercera persona plural.
        if i in config['primera_persona'] and i in config['plural']:

            # Cambio según los dispuesto para los verbos del grupo 08.
            # e --> i
            base_form = irregular_cast_group_08_b(verb, base_form, irregular_verb_groups)

            # Cambio según los dispuesto para los verbos del grupo 12.
            # o --> u
            base_form = irregular_cast_group_12_b(verb, base_form, irregular_verb_groups)


        if i in config['tercera_persona']:

            # Cambio según los dispuesto para los verbos del grupo 09.
            # u --> ue
            base_form = irregular_cast_group_09(verb, base_form, irregular_verb_groups)

        # Conjugación para tercera persona y primera persona
        if i in config['primera_persona'] or i in config['tercera_persona']:

            # Cambio exclusivo para el verbo delinquir.
            # qu --> c
            if verb == 'delinquir':
                base_form.replace('qu', 'c')

            # Si el verbo infinitivo termina en ncer:
            # c --> z
            if ncer_flag:
                base_form = base_form[:len(base_form)-1] + 'z'

            # Si el verbo infinitivo termina en ger/gir:
            # g --> j
            if ger_gir_flag:
                base_form = base_form[:len(base_form)-1] + 'j'

            # Si el verbo infinitivo termina en car:
            # c --> qu
            if car_flag:
                base_form = base_form[:len(base_form)-1] + 'qu'

            # Si el verbo infinitivo termina en zar:
            # z --> c
            if zar_flag:
                base_form = base_form[:len(base_form)-1] + 'c'

            # Si el verbo infinitivo termina en guir:
            # gu --> g
            if guir_flag:
                base_form = base_form[:len(base_form)-1]

            # Si el verbo infinitivo termina en guar:
            # u --> ü
            if guar_flag:
                base_form = base_form[:len(base_form)-1] + 'ü'

        # Conjugacion para primera persona y tercera persona
        if i in config['tercera_persona'] or i in config['primera_persona']:

            # Cambio según los dispuesto para los verbos del grupo 13.
            # base_form + g
            base_form = irregular_cast_group_13_a(verb, base_form, irregular_verb_groups)

            # Cambio para los verbos terminados en 'decir'
            # dec --> dig
            if fnmatch.fnmatch(verb, '*decir'):
                base_form = base_form.replace('dec', 'dig')

            # Cambio para los verbos terminados en 'hacer'
            # hac --> hag
            if fnmatch.fnmatch(verb, '*hacer'):
                base_form = base_form.replace('hac', 'hag')

        if i in config['segunda_persona'] and i in config['singular']:

            # Cambio para los verbos terminados en 'decir'
            # dec --> d
            if fnmatch.fnmatch(verb, '*decir'):
                if mode != 0:
                    base_form = base_form.replace('dec', 'd')
                suffix_conj[i] = 'í'

            # Cambio para los verbos terminados en 'hacer'
            if fnmatch.fnmatch(verb, '*hacer'):
                if mode != 0:
                    base_form = base_form.replace('hac', 'ha')
                    suffix_conj[i] = 'z'


            # Cambio para los verbos en el grupo 09 (modo vos desactivado).
            # u --> ue
            if mode != 0:
                base_form = irregular_cast_group_09(verb, base_form, irregular_verb_groups)


        # Elimina el último caracter a los verbos del grupo 07, de modo
        # de aprovechar el sufijo especifico para los verbor terminado en
        # ír.
        if verb in irregular_verb_groups['irregular_verbs_grupo_07_eir']:
            base_form = base_form[:len(base_form)-1]

        verb_conj.append(base_form + suffix_conj[i])
    return verb_conj
