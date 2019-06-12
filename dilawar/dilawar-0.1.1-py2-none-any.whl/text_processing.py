"""text_processing.py: 

Text processing functions.

"""
    
__author__           = "Dilawar Singh"
__copyright__        = "Copyright 2016, Dilawar Singh"
__credits__          = ["NCBS Bangalore"]
__license__          = "GNU GPL"
__version__          = "1.0.0"
__maintainer__       = "Dilawar Singh"
__email__            = "dilawars@ncbs.res.in"
__status__           = "Development"

import re

float_regex_ = re.compile( r'[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?' )

def to_float( token ):
    val = token
    try:
        val = float( token )
    except Exception as e:
        pass
    return val

def remove_special_char( txt ):
    return re.sub( r'_|\+|\-|\%', ' ', txt )

def find_floats( text ):
    """Find all floats in given string
    """
    global float_regex_
    assert type( text ) == str
    return [ to_float( m.group(0) ) for m  in float_regex_.finditer( text ) ]

def arrays2csv( outfile, **kwargs ):
    """Write given vector/array to a CSV file. The separator is ',' by default.
    It can not be changed. It can not be changed. It can not be changed.

    The argument order will be preserved if python-3.6+ is used. Not
    implementing the order preservation here.
    """
    header = map( remove_special_char, kwargs.keys( ) )
    sep = ','
    with open( outfile, 'w' ) as f:
        f.write( sep.join( header ) + '\n' )
        cols = kwargs.values( )
        for x in zip( *cols ):
            x = map( str, x )
            f.write( sep.join( x ) + '\n' )


# deprecated
def find_all_floats( txt ):
    return find_floats( txt )
