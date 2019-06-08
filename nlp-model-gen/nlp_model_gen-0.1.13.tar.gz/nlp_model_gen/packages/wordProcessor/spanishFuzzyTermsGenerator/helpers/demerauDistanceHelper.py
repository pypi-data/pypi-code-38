from nlp_model_gen.constants.constants import WORD_PROCESSOR_SPECIAL_CHARS

def get_accent_adjustment(s1, s2, ignore_case):
    """
    Obtiene un valor de ajuste para dos cadenas de acuerdo a los acentos que contengan

    :s1: [String] - Cadena 1

    :s2: [String] - Cadena 2

    :return: [boolean] - True si ambas cadenas contienen acento, False en caso
    contrario.
    """
    lower_s1 = s1
    lower_s2 = s2
    if ignore_case:
        lower_s1 = lower_s1.lower()
        lower_s2 = lower_s2.lower()
    for special_char, non_special_char in WORD_PROCESSOR_SPECIAL_CHARS:
        if special_char in lower_s1 and not special_char in lower_s2:
            if lower_s1.count(special_char) + lower_s1.count(non_special_char) == lower_s2.count(non_special_char):
                return 1
    return 0

def damerau_levenshtein_distance(s1, s2, ignore_case=False):
    """
    Implementación de la función de demerau_levenshtein. Calcula dicha distancia
    entre dos cadenas.

    :s1: Cadena 1 (sin restricciones)

    :s2: Cadena 2 (sin restricciones)

    :ignore_case: Si es True ignora la diferencia entre mayusculas y minusculas

    :return: valor numérico entero que representa la distancia entre estas dos
    cadenas.
    """

    dict = {}
    str1 = s1.lower() if ignore_case else s1
    str2 = s2.lower() if ignore_case else s2
    lenstr1 = len(str1)
    lenstr2 = len(str2)
    for i in range(-1, lenstr1+1):
        dict[(i, -1)] = i + 1
    for j in range(-1, lenstr2+1):
        dict[(-1, j)] = j+1

    for i in range(lenstr1):
        for j in range(lenstr2):
            if str1[i] == str2[j]:
                cost = 0
            else:
                cost = 1
            dict[(i, j)] = min(
                dict[(i-1, j)] + 1, # deletion
                dict[(i, j-1)] + 1, # insertion
                dict[(i-1, j-1)] + cost, # substitution
            )
            if i and j and str1[i] == str2[j-1] and str1[i-1] == str2[j]:
                dict[(i, j)] = min(dict[(i, j)], dict[i-2, j-2] + cost) # transposition

    accent_adjustment = get_accent_adjustment(str1, str2, ignore_case)

    return dict[lenstr1-1, lenstr2-1] - accent_adjustment
