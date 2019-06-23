""" Concrete strength
"""

import math


def fcd(acc, fck, γc):
    """Design value for the compressive strength of concrete

    Args:
        acc (float): Coefficient taking account of long term effects on the compressive strength
                     and of unfavourable effects resulting from the way the load is applied
        fck (float): Characteristic (5%) compressive strength of concrete
        γc (float): Safety factor

    Returns:
        float: Given using the expression:

        .. math::
            f_{cd}=a_{cc}\dfrac{f_{ck}}{γ_c}

    """
    return acc * fck / γc


def fcm(fck):
    """ Mean compressive strength at 28 days

    Args:
        fck (float): Characteristic (5%) compressive strength of concrete [MPa]

    Returns:
        float: Given using the expression:

        .. math::
            f_{cm}=f_{ck} + 8

    """
    return fck + 8


def fctm(fck):
    """ Mean tensile strength at 28 days

    Args:
        fck (float): Characteristic (5%) compressive strength of concrete [MPa]

    Returns:
        float: Given using the expression:

        .. math::

           f_{ctm} = 0.30\cdot f_{ck}^{2/3} for f_{ck}\le 50MPa

           f_{ctm} = 2.12\cdot ln(1+f_{cm}/10) for f_{ck}> 50MPa

    """
    if fck <= 50:
        _fctm = 0.3 * fck**(2.0 / 3.0)
#        _fctm = 0.3 * math.pow(fck, (2.0 / 3.0))
    else:
        _fctm = 2.12 * math.log(1 + (fcm(fck) / 10))

    return _fctm


def fctk005(fck):
    """ Characteristic (5% fractile) tensile strength of concrete [MPa]

    Args:
        fck (float): Characteristic (5%) compressive strength of concrete [MPa]

    Returns:
        float: Given using the expression:

        .. math::
            f_{ctk,0.05}=0.7\cdot f_{ctm}

    """
    return 0.7 * fctm(fck)


def fctk095(fck):
    """ Characteristic (95% fractile) tensile strength of concrete [MPa]

    Args:
        fck (float): Characteristic (5%) compressive strength of concrete [MPa]

    Returns:
        float: Given using the expression:

        .. math::
            f_{ctk,0.95}=1.3\cdot f_{ctm}

    """
    return 1.3 * fctm(fck)
