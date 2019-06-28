"""
unit transformation using in quantum chemistry

"""

ATOMIC_UNIT = 'au'

UNITS = {
    "LENGTH_UNITS" : {
        "m" : 1,
        "dm": 1e-1,
        "cm": 1e-2,
        "mm": 1e-3,
        "um": 1e-6,
        "nm": 1e-9,
        "ang" : 1e-10,
        "pm": 1e-12,
        "fm": 1e-15,
        "bohr" : 5.29177210904*1e-11,
        ATOMIC_UNIT : 5.29177210904*1e-11,
    },

    "MASS_UNITS" : {
        "kg" : 1,
        ATOMIC_UNIT : 9.1093837015*1e-31,
    },


    "ENERGY_UNITS" : {
        "j" : 1,
        'kj' : 1e3,
        "cal" : 4.184,
        "kcal" : 4.184*1e3,
        "ev" : 1.602176634*1e-19,
        "hartree" : 4.3597447222072*1e-18,
        ATOMIC_UNIT : 4.3597447222072*1e-18,
    },


    "NUMBER_UNITS" : {
        "1" : 1,
        "mol" : 6.02214076*1e23,
    },

    "TIME_UNITS" : {
        "s" : 1,
        "ms" : 1e-3,
        "us" : 1e-6,
        "ns" : 1e-9,
        "ps" : 1e-12,
        "fs" : 1e-15,
        ATOMIC_UNIT : 2.4188843265857*1e-17,
    }

}


def get_atomic_unit(length):
    if length == 1:
        return ATOMIC_UNIT
    return [ATOMIC_UNIT] * length


def trans_basic_unit(src, dest, unit):
    """
    general function for unit transformation
    """
    assert isinstance(unit, str), "unit should be a string"
    UNIT_TYPE = unit.upper()+"_UNITS"
    assert UNIT_TYPE in UNITS
    assert isinstance(src, str) and isinstance(dest, str), "src and dest {0} unit should be string".format(unit)
    src = src.lower()
    dest = dest.lower()
    unit_units = UNITS[UNIT_TYPE]
    assert src in unit_units and dest in unit_units,\
        "src {1} and dest {2} {0} unit should be valid {0} unit".format(unit, src, dest)
    return float(unit_units[src]) / float(unit_units[dest])


def trans_length(src, dest="Ang"):
    """
    >>> abs(trans_length("ang") - 1.) < 1e-5
    True
    >>> abs(trans_length("nm", "ang") - 10) < 1e-5
    True
    >>> abs(trans_length("bohr", "ang") - 0.529177210904) < 1e-5
    True
    """
    return trans_basic_unit(src, dest, unit="length")

def trans_time(src, dest="fs"):
    """
    >>> abs(trans_time("ps") - 1E3) < 1e-5
    True
    >>> abs(trans_time("ns", "ps") - 1E3) < 1e-5
    True
    >>> abs(trans_time("ms", "fs") - 1E12) < 1e-5
    True
    """
    return trans_basic_unit(src, dest, unit="time")

def trans_abs_energy(src, dest="eV"):
    """
    >>> abs(trans_abs_energy("ev") - 1.) < 1e-5
    True
    >>> abs(trans_abs_energy("eV", "hartree") - 0.0367493) < 1e-5
    True
    >>> abs(trans_abs_energy("kcal", "cal")- 1000) < 1e-5
    True
    """
    return trans_basic_unit(src, dest, unit="energy")

def trans_energy(src, dest="eV"):
    """
    >>> abs(trans_energy("hartree") - 27.211386245988653) < 1e-5
    True
    >>> abs(trans_energy("kJ/mol", "eV") - 1/96.485) < 1e-5
    True
    >>> abs(trans_energy("kcal/mol", "au") - 1/627.50) < 1e-5
    True
    """
    src = (src+'/1').split("/")[:2]
    dest = (dest+'/1').split("/")[:2]
    return trans_basic_unit(src[0], dest[0], "energy") / trans_basic_unit(src[1], dest[1], "number")

def trans_velocity(src, dest="ang/ps"):
    """
    >>> abs(trans_velocity("hartree") - 27.211386245988653) < 1e-5
    True
    >>> abs(trans_velocity("kJ/mol", "eV") - 1/96.485) < 1e-5
    True
    >>> abs(trans_velocity("kcal/mol", "au") - 1/627.50) < 1e-5
    True
    """
    SEG_LENGTH = 2
    if src == ATOMIC_UNIT: 
        src = get_atomic_unit(SEG_LENGTH)
    else:
        src = src.split("/")
    assert len(src) == SEG_LENGTH
        
    if dest == ATOMIC_UNIT:
        dest = [dest] * SEG_LENGTH
    else:
        dest = dest.split("/")
    assert len(dest) == SEG_LENGTH
    return trans_basic_unit(src[0], dest[0], "length") / trans_basic_unit(src[1], dest[1], "time")



def trans_force(src, dest="eV/Ang"):
    """
    >>> abs(trans_velocity("hartree") - 27.211386245988653) < 1e-5
    True
    >>> abs(trans_velocity("kJ/mol", "eV") - 1/96.485) < 1e-5
    True
    >>> abs(trans_velocity("kcal/mol", "au") - 1/627.50) < 1e-5
    True
    """
    SEG_LENGTH = 2
    if src == ATOMIC_UNIT: 
        src = get_atomic_unit(SEG_LENGTH)
    else:
        src = src.split("/")
    assert len(src) == SEG_LENGTH
        
    if dest == ATOMIC_UNIT:
        dest = [dest] * SEG_LENGTH
    else:
        dest = dest.split("/")
    assert len(dest) == SEG_LENGTH
    return trans_basic_unit(src[0], dest[0], "energy") / trans_basic_unit(src[1], dest[1], "length")


def test():
    cases = [
        {
            "function" : trans_length,
            "src" : "ang",
            "dest" : "ang",
            "exp" : 1,
        },
        {
            "function" : trans_length,
            "src" : "nm",
            "dest" : "ang",
            "exp" : 10,
        },
        {
            "function" : trans_length,
            "src" : "nm",
            "dest" : "fm",
            "exp" : 1e6,
        },
        {
            "function" : trans_length,
            "src" : "ang",
            "dest" : "au",
            "exp" : 1/0.529,
        },

    ]

    for case in cases:
        func = case['function']
        src  = case['src']
        dest = case['dest']
        exp  = case['exp']
        print(func(src, dest)-exp < 1e-5)



if __name__ == '__main__':
    test()




