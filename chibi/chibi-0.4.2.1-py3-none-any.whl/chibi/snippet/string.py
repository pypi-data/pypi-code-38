import _string
import io
import gzip as gzip_module
import re
from collections import defaultdict

from .extra_string import codepoint, replacement
from .regex import separate_camelcase_phase_1, separate_camelcase_phase_2


__all__ = [ 'camel_to_snake' ]


def camel_to_snake( s ):
    result = separate_camelcase_phase_1.sub( r'\1_\2', s )
    result = separate_camelcase_phase_2.sub( r'\1_\2', result ).lower()
    return result


def fold_to_ascii( s ):
    if s is None:
        raise NotImplementedError
    if not isinstance( s, str ):
        raise NotImplementedError

    def none_factory():
        return None
    translate_table = codepoint + replacement
    default_translate_table = defaultdict( none_factory, translate_table )

    return s.translate( default_translate_table )


def replace_with_dict( s, d ):
    """
    replaces the substrings in the dictionary keys with their values

    Parameters
    ----------
    s: string
    d: dict

    Returns
    -------
    string

    Examples
    --------
    >>>s1 = "asdf qwer"
    >>>d1 = { 'asdf', 'foo' }
    >>>d2 = { 'qwer', 'bar' }
    >>>replace_with_dict( s1, d1)
    "foo qwer"
    >>>replace_with_dict( s1, d2)
    "asdf bar"
    """
    if s is None:
        return None
    pattern = re.compile( r'\b(' + '|'.join( d.keys() ) + r')\b' )
    return pattern.sub( lambda x: d[ x.group() ], s )


def get_the_number_of_parameters( s ):
    """
    return the number of parameters have a string

    Parameters
    ----------
    s: string

    Example
    -------
    >>>get_the_number_of_parameters( "{}" )
    1
    >>>get_the_number_of_parameters( "pi-piru {}" )
    1
    >>>get_the_number_of_parameters( "{} pi-pipu {}" )
    2
    """
    list_of_params = list( _string.formatter_parser( s ) )
    return len( list_of_params )


def decode( s, code='utf-8' ):
    '''
    decode a string
    '''
    return s.decode( code )


def gzip( s ):
    out = io.BytesIO()
    with gzip_module.GzipFile( fileobj=out, mode='w' ) as f:
        f.write( s.encode() )
    result = out.getvalue()
    return result
