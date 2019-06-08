# Recibe un verbo y devuelve su conjugación en preterito perfecto simple indicativo.
# <verb> verbo a conjugar debe ser una cadena de caracteres terminada en
# uno de {ar, er, ir, ár, ér, ír}. De no ser asi devuelve un vector vacio.
# <force_conj>: valor booleano. Si es verdadero fuerza a que el verbo
# sea conjugado por la función sin recurrir al diccionario de irregulares
# (aún si el mismo se encontrase allí)

# @Vendors
import fnmatch

# @Helpers
from .irregularVerbCastHelper import (
    irregular_cast_group_04_a,
    irregular_cast_group_06,
    irregular_cast_group_07,
    irregular_cast_group_08_b,
    irregular_cast_group_11,
    irregular_cast_group_12_b
)

def preterito_perf_simple_conj(verb, force_conj, mode, configs):
    irregular_verb_exceptions = configs['irregular_verb_exceptions'] 
    irregular_verb_groups = configs['irregular_verb_groups']
    config = configs['config']
    if not any(fnmatch.fnmatch(verb, suffix) for suffix in ['*ar', '*er', '*ir', '*ár', '*ér', '*ír']):
        return ['', '', '', '', '', '']
    verb_conj = []
    suffix_conj = []
    base_verb = verb[0:len(verb)-2]
    car_flag = False
    zar_flag = False
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
                suffix_conj = ['ué', 'aste', 'ó', 'amos', 'asteis', 'aron']
            elif fnmatch.fnmatch(verb, '*guar'):
                suffix_conj = ['üé', 'aste', 'ó', 'amos', 'asteis', 'aron']
            else:
                suffix_conj = ['é', 'aste', 'ó', 'amos', 'asteis', 'aron']
        if fnmatch.fnmatch(verb, '*er') or fnmatch.fnmatch(verb, '*ér'):
            suffix_conj = ['í', 'iste', 'ió', 'imos', 'isteis', 'ieron']
        if fnmatch.fnmatch(verb, '*ir') or fnmatch.fnmatch(verb, '*ír'):
            suffix_conj = ['í', 'iste', 'ió', 'imos', 'isteis', 'ieron']
    else:
        return irregular_verb_exceptions[verb]['pret_perf']
    for i in range(0, 6):
        if  fnmatch.fnmatch(verb, '*decir'):
            base_form = base_verb.replace('dec', 'dij')
        elif fnmatch.fnmatch(verb, '*hacer'):
            base_form = base_verb.replace('hac', 'hic')
        else:
            base_form = base_verb

        # Si el verbo infinitivo termina en ncer se modifica el singular
        # de la primera persona:
        # c --> qu
        if car_flag and i in config['primera_persona'] and i in config['singular']:
            base_form = base_form[:len(base_form)-1] + 'qu'

        # Si el verbo infinitivo termina en zar se modifica el singular
        # de la primera persona:
        # z --> c
        if zar_flag and i in config['primera_persona'] and i in config['singular']:
            base_form = base_form[:len(base_form)-1] + 'c'

        # Si el verbo infinitivo termina en guar se modifica el singular
        # de la primera persona:
        # z --> c
        if guar_flag and i in config['primera_persona'] and i in config['singular']:
            base_form = base_form[:len(base_form)-1]


        # Para los verbos contenidos en el grupo 04 se aplica el cambio de base
        # según lo definido para el preterito del grupo 04 de verbos irregulares.
        # c --> j
        base_form = irregular_cast_group_04_a(verb, base_form, irregular_verb_groups)

        # Conjugación sobre la tercera persona de los verbos en el grupo 05.
        if i in config['tercera_persona']:

            if verb in irregular_verb_groups['irregular_verbs_grupo_05_er'] or verb in irregular_verb_groups['irregular_verbs_grupo_05_nir'] or verb in irregular_verb_groups['irregular_verbs_grupo_05_ullir']:
            # Elimina la i inicial al sufijo para la conjugación.
                suffix_conj[i] = suffix_conj[i][1:]

            # Cambia la forma base del grupo segun lo dispueto para el grupo 06.
            # e --> i
            base_form = irregular_cast_group_06(verb, base_form, irregular_verb_groups)

            # Cambia la forma base del grupo segun lo dispueto para el grupo 07.
            # e --> i
            base_form = irregular_cast_group_07(verb, base_form, irregular_verb_groups)

            # Cambia la forma base del grupo segun lo dispueto para el grupo 08.
            # e --> i
            base_form = irregular_cast_group_08_b(verb, base_form, irregular_verb_groups)

            # Cambia la forma base del grupo segun lo dispueto para el grupo 11.
            # base_form + y
            base_form = irregular_cast_group_11(verb, base_form, irregular_verb_groups)

            # Cambia la forma base del grupo segun lo dispueto para el grupo 12.
            # o --> u
            base_form = irregular_cast_group_12_b(verb, base_form, irregular_verb_groups)

            # Cambia la forma base para los verbos terminados en hacer (singular).
            # c --> z
            if i in config['singular'] and fnmatch.fnmatch(verb, '*hacer'):
                base_form = base_form[:len(base_form)-1] + 'z'


        # Elimina la i sobrante que queda al conjugar estos verbos.
        if i in config['tercera_persona'] and (verb in irregular_verb_groups['irregular_verbs_grupo_07_eir'] or verb in irregular_verb_groups['irregular_verbs_grupo_07_enir'] or (fnmatch.fnmatch(verb, '*uir') and not verb in irregular_verb_groups['irregular_verbs_grupo_06_ir'])):
            suffix_conj[i] = suffix_conj[i][1:]

        # Elimina la i sobrante que queda al conjugar los verbos del grupo 04
        # en el plural de la tercera persona
        if i in config['tercera_persona'] and i in config['plural'] and (verb in irregular_verb_groups['irregular_verbs_grupo_04_ducir'] or fnmatch.fnmatch(verb, '*decir')):
            suffix_conj[i] = suffix_conj[i][1:]

        # Modifica el sufijo para los verbos del grupo 04 en primera y tercera
        # persona.
        # Primera persona: é por e
        # Tercera persona: ó por o
        if i in config['primera_persona'] and i in config['singular'] and (verb in irregular_verb_groups['irregular_verbs_grupo_04_ducir']  or fnmatch.fnmatch(verb, '*decir') or fnmatch.fnmatch(verb, '*hacer')):
            verb_conj.append(base_form + 'e')
        elif i in config['tercera_persona'] and i in config['singular'] and (verb in irregular_verb_groups['irregular_verbs_grupo_04_ducir']  or fnmatch.fnmatch(verb, '*decir') or fnmatch.fnmatch(verb, '*hacer')):
            verb_conj.append(base_form + 'o')
        else:
            verb_conj.append(base_form + suffix_conj[i])

    return verb_conj
