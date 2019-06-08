# Función auxiliar utilizada para reemplazar en una cadena de derecha a izquierda
def replace_right(source, target, replacement, replacements=None):
    return replacement.join(source.rsplit(target, replacements))

# Excepciones al diptongo ue
h_exceptions = ['desosar', 'oler']

# Las funciones/métodos implementados a continuación definen los cambios
# a realizar para cada grupo particular de verbos irregulares.
# Esto no incluye a los verbos incluidos en el diccionario de verbos
# irregulares, sino que atañe a los verbos en los
def irregular_cast_group_01(verb, base_verb, irregular_verb_groups):
    if verb in irregular_verb_groups['irregular_verbs_grupo_01_ar'] or verb in irregular_verb_groups['irregular_verbs_grupo_01_er'] or verb in irregular_verb_groups['irregular_verbs_grupo_01_ir']:
        return replace_right(base_verb, 'e', 'ie', 1)
    else:
        return base_verb

def irregular_cast_group_02(verb, base_verb, irregular_verb_groups):
    if verb in irregular_verb_groups['irregular_verbs_grupo_02_ar'] or verb in irregular_verb_groups['irregular_verbs_grupo_02_er']:
        # Verifica la existencia del diptongo "ue" que pasa a "hue"
        if verb in h_exceptions:
            return replace_right(base_verb, 'o', 'hue', 1)
        else:
            return replace_right(base_verb, 'o', 'ue', 1)
    else:
        return base_verb

def irregular_cast_group_03(verb, base_verb, irregular_verb_groups):
    if verb in irregular_verb_groups['irregular_verbs_grupo_03_acer'] or verb in irregular_verb_groups['irregular_verbs_grupo_03_ecer'] or verb in irregular_verb_groups['irregular_verbs_grupo_03_ocer'] or verb in irregular_verb_groups['irregular_verbs_grupo_03_ucer']:
        return replace_right(base_verb, 'c', 'zc', 1)
    else:
        return base_verb

def irregular_cast_group_04_a(verb, base_verb, irregular_verb_groups):
    if verb in irregular_verb_groups['irregular_verbs_grupo_04_ducir']:
        return replace_right(base_verb, 'c', 'j', 1)
    else:
        return base_verb

def irregular_cast_group_04_b(verb, base_verb, irregular_verb_groups):
    if verb in irregular_verb_groups['irregular_verbs_grupo_04_ducir']:
        return replace_right(base_verb, 'c', 'zc', 1)
    else:
        return base_verb

def irregular_cast_group_05(verb, base_verb, irregular_verb_groups):
    if verb in irregular_verb_groups['irregular_verbs_grupo_05_er'] or verb in irregular_verb_groups['irregular_verbs_grupo_05_nir'] or verb in irregular_verb_groups['irregular_verbs_grupo_05_ullir']:
        return replace_right(base_verb, 'i', '', 1)
    else:
        return base_verb

def irregular_cast_group_05_a(verb, base_verb, irregular_verb_groups):
    if verb in irregular_verb_groups['irregular_verbs_grupo_05_er'] or verb in irregular_verb_groups['irregular_verbs_grupo_05_nir'] or verb in irregular_verb_groups['irregular_verbs_grupo_05_ullir']:
        modified_verb = replace_right(base_verb, 'i', '$', 1)
        modified_verb = replace_right(modified_verb, 'i', '', 1)
        return replace_right(modified_verb, '$', 'i', 1)
    else:
        return base_verb

def irregular_cast_group_06(verb, base_verb, irregular_verb_groups):
    if verb in irregular_verb_groups['irregular_verbs_grupo_06_ir']:
        return replace_right(base_verb, 'e', 'i', 1)
    else:
        return base_verb

def irregular_cast_group_07(verb, base_verb, irregular_verb_groups):
    if verb in irregular_verb_groups['irregular_verbs_grupo_07_eir'] or verb in irregular_verb_groups['irregular_verbs_grupo_07_enir']:
        return replace_right(base_verb, 'e', 'i', 1)
    else:
        return base_verb

def irregular_cast_group_07_a(verb, base_verb, irregular_verb_groups):
    if verb in irregular_verb_groups['irregular_verbs_grupo_07_eir'] or verb in irregular_verb_groups['irregular_verbs_grupo_07_enir']:
        return replace_right(base_verb, 'i', '', 1)
    else:
        return base_verb

def irregular_cast_group_07_b(verb, base_verb, irregular_verb_groups):
    if verb in irregular_verb_groups['irregular_verbs_grupo_07_eir'] or verb in irregular_verb_groups['irregular_verbs_grupo_07_enir']:
        modified_verb = replace_right(base_verb, 'i', '$', 1)
        modified_verb = replace_right(modified_verb, 'i', '', 1)
        return replace_right(modified_verb, '$', 'i', 1)
    else:
        return base_verb

def irregular_cast_group_08_a(verb, base_verb, irregular_verb_groups):
    if verb in irregular_verb_groups['irregular_verbs_grupo_08_ir']:
        return replace_right(base_verb, 'e', 'ie', 1)
    else:
        return base_verb

def irregular_cast_group_08_b(verb, base_verb, irregular_verb_groups):
    if verb in irregular_verb_groups['irregular_verbs_grupo_08_ir']:
        return replace_right(base_verb, 'e', 'i', 1)
    else:
        return base_verb

def irregular_cast_group_09(verb, base_verb, irregular_verb_groups):
    if verb in irregular_verb_groups['irregular_verbs_grupo_09_u']:
        return replace_right(base_verb, 'u', 'ue', 1)
    else:
        return base_verb

def irregular_cast_group_10(verb, base_verb, irregular_verb_groups):
    if verb in irregular_verb_groups['irregular_verbs_grupo_10_irir']:
        return replace_right(base_verb, 'i', 'ie', 1)
    else:
        return base_verb

def irregular_cast_group_11(verb, base_verb, irregular_verb_groups):
    if verb in irregular_verb_groups['irregular_verbs_grupo_11_uir']:
        return base_verb + 'y'
    else:
        return base_verb

def irregular_cast_group_12_a(verb, base_verb, irregular_verb_groups):
    if verb in irregular_verb_groups['irregular_verbs_grupo_12_o']:
        return replace_right(base_verb, 'o', 'ue', 1)
    else:
        return base_verb

def irregular_cast_group_12_b(verb, base_verb, irregular_verb_groups):
    if verb in irregular_verb_groups['irregular_verbs_grupo_12_o']:
        return replace_right(base_verb, 'o', 'u', 1)
    else:
        return base_verb

def irregular_cast_group_13_a(verb, base_verb, irregular_verb_groups):
    if verb in irregular_verb_groups['irregular_verbs_grupo_13_aler'] or verb in irregular_verb_groups['irregular_verbs_grupo_13_alir']:
        return base_verb + 'g'
    else:
        return base_verb

def irregular_cast_group_13_b(verb, base_verb, irregular_verb_groups):
    if verb in irregular_verb_groups['irregular_verbs_grupo_13_aler'] or verb in irregular_verb_groups['irregular_verbs_grupo_13_alir']:
        return base_verb + 'd'
    else:
        return base_verb
        