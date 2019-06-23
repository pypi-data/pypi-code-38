""" Concrete elastic deformation
"""


import math
# from pyconc.CivilFuncts.Ec2.Ch3.Concrete import Strength

from . import strength


def Ecm(fck):
    """ Modulus of elasticity

    Args:
        fck (float): Characteristic (5%) compressive strength of concrete [MPa]

    Returns:
        float: Given using the expression:

        .. math::
            E_{cm}=22 (\dfrac{f_{cm}}{10})^{0.3}

    """
    return 22 * math.pow((strength.fcm(fck) / 10), 0.3)


def ν(cracked):
    """ Poisson's ratio

    Args:
        cracked (bool): True for cracked, False for uncracked

    Returns:
        float: 0.0 for cracked, 0.2 for uncracked

    """
    if cracked is True:
        return 0.0
    else:
        return 0.2
