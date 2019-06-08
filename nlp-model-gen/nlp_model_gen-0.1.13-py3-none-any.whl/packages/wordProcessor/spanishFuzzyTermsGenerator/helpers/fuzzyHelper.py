def replace_char(string_as_list, position, length, replacements):
    """
    Reemplaza una aparición de un potencial termino de confusión por
    aquellas variantes identificadas en el archivo de configuración.

    :string_as_list: cadena como lista.

    :position: posicion del caracter a reemplazar

    :length: cantidad de caracteres a reemplazar (por el un único reemplazo)

    :replacements: lista de reemplazos posibles para la posición
    """
    replaced_strings = []
    for replacement in replacements:
        str_copy = string_as_list.copy()
        if length > 1:
            for i in reversed(range(1, length)):
                del str_copy[position + i]
        str_copy[position] = replacement
        replaced_strings.append(''.join(str_copy))
    return replaced_strings

def swap(arr, p0, p1):
    """
    Intercambia los valores de dos posiciones de un arreglo.
    """
    arr_list = list(arr)
    aux = arr_list[p0]
    arr_list[p0] = arr_list[p1]
    arr_list[p1] = aux
    return "".join(arr_list)

def rnd_confuse_char(string, configs, new_string_arr=None, init_position=0):
    """
    Intercambia un caracter de la palabra pasada por parametro por otro
    definido en el diccionario de confusiones. Aplica recursivamente los
    reemplazos describiendo un arbol de reemplazos para lograr todas 
    las posibilidades y combinaciones de reemplazos.

    :param string: Palabra a la cual se le deben aplicar los cambios
    de caracter.

    :return: Arreglo con las posibles confusiones de caracteres para una
    palabra.
    """
    confuse_chars = configs['confuse_chars']
    confuse_chars_max_length = configs['confuse_chars_max_length']
    length = len(string)
    if init_position >= length: 
        return []
    if new_string_arr is None:
        new_string_arr = []
    i = init_position
    while i < length:
        string_as_list = list(string)
        for j in range(1, confuse_chars_max_length + 1):
            token_length = j
            position_to = i + token_length
            if string[i:position_to] in confuse_chars and position_to < length:
                replaced_strings = replace_char(string_as_list, i, token_length, confuse_chars[string[i:position_to]])
                for replaced_string in replaced_strings:
                    rnd_confuse_char(replaced_string, configs, new_string_arr, i + 1)
                new_string_arr.extend(replaced_strings)
        i += 1
    return new_string_arr

def rnd_char_del(string, configs):
    """
    Elimina un caracter de la palabra.

    :return: Arreglo con todas las posibles eliminaciones de letras para
    la palabra.
    """
    string_length = len(string)
    new_string_arr = []
    for i in range(0, string_length):
        string_as_list = list(string)
        del string_as_list[i]
        new_string = ''.join(string_as_list)
        new_string_arr.append(new_string)
    return new_string_arr

def rnd_char_change(string, configs):
    """
    Realiza un intercambio entre dos caracteres consecutivos de la palabra
    con la que fue instanciada la clase.

    :return: Arreglo con todos los cambios de caracteres consecutivos posibles
    para la palabra
    """
    i = 0
    j = i + 1
    new_string_arr = []
    string = string
    while j < len(string):
        string = swap(string, i, j)
        new_string_arr.append(string)
        string = swap(string, i, j)
        i = j
        j += 1
    return new_string_arr

def rnd_duplicate_char(string, configs):
    """
    Duplica un caracter de la palabra con la que fue instanciada la clase.

    :return: Arreglo con todas las duplicaciones de caracteres posibles.
    """
    i = 0
    j = len(string)
    new_string_arr = []
    while i < j:
        if i == 0:
            new_string_arr.append(string[0:1] + string[0:1] + string[1:j])
        else:
            new_string_arr.append(string[0:i] + string[i:i+1] + string[i:j])
        i += 1
    return new_string_arr