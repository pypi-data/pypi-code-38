"""
SatNOGS Decoder subpackage initialization
"""
from __future__ import absolute_import, division, print_function

import functools
import re

from .aausat4 import Aausat4
from .acrux1 import Acrux1
from .ax25frames import Ax25frames
from .ax25monitor import Ax25monitor
from .bisonsat import Bisonsat
from .bugsat1 import Bugsat1
from .cas4 import Cas4
from .csim import Csim
from .cubebel1 import Cubebel1
from .cubesatsim import Cubesatsim
from .elfin import Elfin
from .entrysat import Entrysat
from .equisat import Equisat
from .eshail2 import Eshail2
from .fox import Fox
from .irazu import Irazu
from .irvine import Irvine
from .minxss import Minxss
from .mysat import Mysat
from .origamisat1 import Origamisat1
from .pwsat2 import Pwsat2
from .qbee import Qbee
from .siriussat import Siriussat
from .skcube import Skcube
from .strand import Strand
from .us6 import Us6
from .uwe4 import Uwe4

__all__ = [
    'Aausat4',
    'Acrux1',
    'Ax25frames',
    'Ax25monitor',
    'Bisonsat',
    'Bugsat1',
    'Cas4',
    'Cubebel1',
    'Cubesatsim',
    'Csim',
    'Elfin',
    'Entrysat',
    'Eshail2',
    'Equisat',
    'Fox',
    'Irazu',
    'Irvine',
    'Minxss',
    'Mysat',
    'Origamisat1',
    'Pwsat2',
    'Qbee',
    'Siriussat',
    'Skcube',
    'Strand',
    'Us6',
    'Uwe4',
]

FIELD_REGEX = re.compile(
    r':field (?P<field>[\*\w]+): (?P<attribute>.*?)'
    r'(?:(?=:field)|\Z|\n)', re.S)


def get_fields(struct, empty=False):
    '''
    Get fields defined in docstring
    '''
    fields = {}

    try:
        doc_fields = FIELD_REGEX.findall(struct.__doc__)
    except TypeError:
        return fields

    for key, value in doc_fields:
        try:
            fields[key] = functools.reduce(getattr, value.split('.'), struct)
        except AttributeError:
            if empty:
                fields[key] = None

    return fields
