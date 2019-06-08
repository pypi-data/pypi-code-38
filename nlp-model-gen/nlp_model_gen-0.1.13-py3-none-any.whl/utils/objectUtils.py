# @Vendors
import copy

# Utilidades para trabajar con diccionarios.

def fillDict(dict, keys):
    """
    Busca las keys especificadas en un diccionario y devuelve las keys que matcheen
    o None en su defecto

    :dict: [Dict] - diccionario sobre el que iterar

    :keys: [List(String)] - claves requeridas

    :return: [List(Any)] - lista con todas las claves que cumplen la condición
    """
    return [dict[k] if k in dict.keys() else None for k in keys]

def destructure(dict, keys):
    """
    Simula el comportamiento de una asignación por destructuración de js.

    :dict: [Dict] - diccionrio sobre el cual se buscaran las claves

    :keys: [List(String)] - claves requeridas

    :return: [Dict] - Diccionario con todas las claves que se encuentran
    """
    for key in keys:
        if key.__name__ in dict.keys():
            key = dict[key.__name__]

def get_elements_from_dict(dict, exceptions):
    """
    Devuelve todos los elementos de un diccionario con excepción de las claves
    especificadas como excepción.

    :dict: [Dict] - diccionario sobre el cual obtener las claves

    :keys: [List(String)] - claves requeridas

    :return: [List(Any)] - lista con todas las claves que cumplen la condición
    """
    keys = dict.keys()
    return [dict[key] if key in keys else None and key not in exceptions for key in keys]

def update_dict(origin_dict, new_data=None, deletion_keys=None): 
    """
    Actualiza los datos en un diccionario a partir de otro.

    :origin_dict: [Dict] - Diccionario original

    :new_data: [Dict] - Diccionario que contiene las keys a modificar / nuevas.

    :deletion_keys: [List(string)] - Keys a eliminar del diccionario

    :return: [Dict] - Copia del diccionario original con las modificaciones solicitadas.
    """
    origin_dict_copy = copy.deepcopy(origin_dict)
    if new_data is None:
        new_data = dict({})
    if deletion_keys is None:
        deletion_keys = list([])
    for key in new_data.keys():
        origin_dict_copy[key] = new_data[key]
    for key in deletion_keys:
        if key in origin_dict_copy.keys():
            del origin_dict_copy[key]
    return origin_dict_copy

def remove_object_from_list(object_list, search_object):
    """
    Elimina de una lista al objeto cuyas keys coincidan en valor con el patron pasado como parametro.

    :list: [List] - Lista original.

    :search_object: [Dict] - Objeto patron de comparación.
    """
    if object_list is None or search_object is None:
        return
    for element in object_list:
        found = True
        for key in search_object.keys():
            if not key in element.keys() or search_object[key] != element[key]:
                found = False
                break
        if found is True:
            object_list.remove(element)
            return

def transform_dict_key_data_to_int(dictionary):
    """
    Convierte las keys de un diccionario en valores enteros. Devuelve el mismo diccionario con las keys 
    transformads en valores enteros.

    :dictionary: [Dict] - Diccionario a convertir

    :return: [Dict] - Diccionario con las keys convertidas
    """
    aux_dict = dict({})
    for key in dictionary:
        aux_dict[int(key)] = dictionary[key]
    return aux_dict
    