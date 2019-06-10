import json
import re

from . import regex as chibi_regex
from .string import camel_to_snake
from chibi.snippet.is_type import is_like_list


def keys_to_snake_case( d ):
    """
    transforma los keys de un dicionaria a snake case

    Returns
    =======
    dict

    Examples
    ========
    >>>keys_to_snake_case( { "HolaMundo": "hola mundo" } )
    { "hola_mundo": "hola_mundo" }
    """
    result = {}
    for k, v in d.items():
        if isinstance( k, str ):
            k = camel_to_snake( k )
        if isinstance( v, ( dict, list, tuple ) ):
            v = __inner_keys_to_snake_case( v )
        result[k] = v
    return result


def replace_keys( d, dr ):
    """
    replace the the keys of a dictionary using another dictioanry for guide

    Parameters
    ----------
    d: dict
        dict is going to have replace his keys
    dr: dict
        dict is going to use for remplace his keys

    Examples
    ========
    >>>replace_keys( { 'a': 'a' }, { 'a': 'b' } )
    {'b':'a'}
    """
    if is_like_list( d ):
        for v in d:
            replace_keys( v, dr )
    elif isinstance( d, dict ):
        for k, value in d.items():
            try:
                new_key = dr[k]
                del d[k]
                d[ new_key ] = value
            except KeyError as e:
                pass
            replace_keys( value, dr )


def rename_keys( d, func ):
    """
    rename the keys in a dict using a function

    Parameters
    ==========
    d: dict
        target dict
    func: callable
        function is going to rename rename the keys

    Returns
    =======
    dict

    Examples
    ========
    >>>rename_keys( { 'a': 'a' }, lambda k: k.upper() )
    {'A':'a'}
    """
    if not callable( func ):
        raise NotImplementedError
    result = {}
    for k, v in d.items():
        result[ func( k ) ] = v
        if isinstance( v, dict ):
            rename_keys( v, func )
    return result


def lower_keys( d ):
    """
    lower all the keys in the dict

    Parameters
    ==========
    d: dict
        target dict

    Returns
    =======
    dict

    Examples
    ========
    >>>lower_keys( { 'A': 'a' } )
    {'a':'a'}
    """
    return rename_keys( d, func=lambda x: x.lower() )


def pop_regex( d, regex ):
    """
    do pop to the keys match with the regex and form a new dict with
    those keys and values

    parameters
    ==========
    d: dict
        target dict
    regex: str or regex
        string to compile the regex or a regex object

    Returns
    =======
    dict

    Examples
    ========
    >>>origin = { "a": "a", "b": "b", "aa": "aa" }
    >>>pop_regex( origin, r'a*' )
    { "a": "a", "aa": "aa" }
    >>>origin == { "b": "b" }
    True
    """
    if isinstance( regex, str ):
        regex = re.compile( regex )
    keys = [ k for k in d.keys() ]
    result = {}
    for k in keys:
        if chibi_regex.test( regex, k ):
            result[ k ] = d.pop( k )
    return result


def get_regex( d, regex ):
    """
    hace get a las llaves del dicionario que concuerden con el regex
    y forma un nuevo dicionario con ese

    parameters
    ==========
    d: dict
        dicionarrio que se le haran los gets
    regex: str or regex
        string que se compilara para ser regex

    Examples
    ========
    >>>origin = { "a": "a", "b": "b", "aa": "aa" }
    >>>pop_regex( origin, r'a*' )
    { "a": "a", "aa": "aa" }
    >>>origin == { "a": "a", "b": "b", "aa": "aa" }
    True
    """
    if isinstance( regex, str ):
        regex = re.compile( regex )
    keys = [ k for k in d.keys() ]
    result = {}
    for k in keys:
        if chibi_regex.test( regex, k ):
            result[ k ] = d.get( k )
    return result


def delete_list_of_keys( d, *keys ):
    """
    elimina las keys de un dicionario

    Parameters
    ==========
    d: dict
        dicionario del que se eliminaran las keys
    keys: tuple
        llaves a eliminar

    Examples
    ========
    >>>origin = { 'a': 'a', 'b': 'b': 'c': 'c' }
    >>>delete_list_of_keys( origin, 'b', 'c' )
    { 'a': 'a' }
    origin == { 'a': 'a' }
    """
    for key in keys:
        del d[ key ]
    return d


def get_list_of_keys( d, *keys ):
    """
    crea un nuevo dicionario con el subconjunto de llaves

    Parameters
    ==========
    d: dict
    keys: tuple

    Examples
    ========
    >>>origin = { 'a': 'a', 'b': 'b': 'c': 'c' }
    >>>get_list_of_keys( origin, 'b', 'c' )
    { 'b': 'b': 'c': 'c' }
    """
    return { key: d[ key ] for key in keys }


def get_from_dict( d, **kw ):
    """
    crea un nuevo dicionario usando el kw
    la llave del kw es la llave del dicionario
    y el valor de kw es el nombre de la nueva llave

    Parameters
    ==========
    d: dict
    kw: dict

    Examples
    ========
    >>>origin = { 'a': 'a', 'b': 'b': 'c': 'c' }
    >>>get_from_dict( origin, a='d', c='e' )
    { 'd': 'a': 'e': 'c' }
    """
    return { v: d[ k ] for k, v in kw.items() }


def remove_value( d, element ):
    """
    elimina los items de un dicionario en el que su value es element

    Parameters
    ==========
    d: dict
    element: object

    Returns
    =======
    dict

    Examples
    ========
    >>>remove_value( { 'a': 1, 'b': 2, 'c': 1 }, 1 )
    { 'b': 2 }
    """
    keys_to_delete = []
    for key, value in d.items():
        if value is element:
            keys_to_delete.append( key )
            continue
        if isinstance( value, dict ):
            r = remove_value( value, element )
        elif isinstance( value, list ):
            r = __remove_element__list( value, element )
        else:
            continue
        if r:
            d[ key ] = r
        else:
            keys_to_delete.append( key )

    delete_list_of_keys( d, *keys_to_delete )
    return d


def remove_nones( d ):
    """
    elimina los Nones de un dicionario

    Parameters
    ==========
    d: dict

    Returns
    =======
    dict

    Examples
    ========
    >>>remove_nones( { 'a': None, 'b': 2, 'c': None } )
    { 'b': 2 }
    """
    return remove_value( d, None )


def hate_ordered_dict( d ):
    """
    elimina los orderer dicts
    """
    return json.loads( json.dumps( d ) )


def remove_xml_notatation( d ):
    if isinstance( d, dict ):
        result = {}
        for k, v in d.items():
            if k.startswith( '#' ) or k.startswith( '@' ) or ':' in k:
                new_k = k[1:]
                new_k = new_k.replace( ':', '_' )
                k = new_k
            result[ k ] = remove_xml_notatation( v )
        return result
    elif isinstance( d, list ):
        return [ remove_xml_notatation( i ) for i in d ]
    return d


def __remove_element__list( l, element ):
    result = []
    for i in l:
        if i is element:
            continue
        if isinstance( i, list ):
            result.append( __remove_element__list( i, element ) )
        if isinstance( i, dict ):
            result.append( remove_value( i, element ) )

    return result


def __inner_keys_to_snake_case( d ):
    if isinstance( d, dict ):
        return keys_to_snake_case( d )
    elif isinstance( d, list ):
        return [ __inner_keys_to_snake_case( a ) for a in d ]
    elif isinstance( d, tuple ):
        return tuple( __inner_keys_to_snake_case( a ) for a in d )
    return d
