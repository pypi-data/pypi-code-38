""" Concrete stress-strain relation
"""

from . import strength
from . import elastic_deformation


def εc1(fck):
    """
    Compressive strain in the concrete at the peak stress (‰)

    Args:
        fck (float): Characteristic compressive cylinder strength of concrete at 28 days

    Returns:
        float: Given using the expression:

        .. math::
            ε_{c1} = min(0.7\cdot f_{cm}^{0.31}, 2.8)

    """
    fcm = strength.fcm(fck)
    return min(2.8, 0.7*fcm**0.31)


def εc2(fck):
    """
    The strain at reaching the maximum strength (‰)

    Args:
        fck (float): Characteristic compressive cylinder strength of concrete at 28 days

    Returns:
        float: Given using the expressions:

        .. math::
            \\begin{eqnarray}
                ε_{c2} & = & 2.0 & for & f_{ck} \le 50MPa \\\\
                ε_{c2} & = & 2.0 + 0.085(f_{ck}-50)^{0.53} & for & f_{ck} \ge 50MPa
            \\end{eqnarray}

    """
    if fck<50:
        _εc2 = 2.0
    else:
        _εc2 = 2.0+0.085*(fck - 50)**0.53

    return _εc2


def εc3(fck):
    """ (‰)

    Args:
        fck (float): Characteristic compressive cylinder strength of concrete at 28 days

    Returns:
        float: Given using the expressions:

        .. math::
            \\begin{eqnarray}
                ε_{c3} & = & 1.75 & for & f_{ck} \le 50MPa \\\\
                ε_{c3} & = & 1.75 + 0.55(f_{ck}-50)/40 & for & f_{ck} \ge 50MPa
            \\end{eqnarray}

    """
    if fck<50:
        _εc3 = 1.75
    else:
        _εc3 = 1.75+0.55*(fck - 50)/40

    return _εc3


def εcu1(fck):
    """

    Args:
        fck (float): Characteristic compressive cylinder strength of concrete at 28 days

    Returns:
        float: Given using the expressions:

        .. math::
            \\begin{eqnarray}
                ε_{cu1} & = & 3.5 & for & f_{ck} \le 50MPa \\\\
                ε_{cu1} & = & 2.8 + 27 \cdot ((98 - f_{cm})/100)^4 & for & f_{ck} \ge 50MPa
            \\end{eqnarray}

    """
    fcm = strength.fcm(fck)
    if fck<50:
        _εcu1 = 3.5
    else:
        _εcu1 = 2.8 + 27*((98-fcm)/100)**4

    return _εcu1


def εcu2(fck):
    """
    The ultimate strain

    Args:
        fck (float): Characteristic compressive cylinder strength of concrete at 28 days

    Returns:
        float: Given using the expressions:

        .. math::
            \\begin{eqnarray}
                ε_{cu2} & = & 3.5 & for & f_{ck} \le 50MPa \\\\
                ε_{cu2} & = & 2.6 + 35 \cdot ((90 - f_{ck})/100)^4 & for & f_{ck} \ge 50MPa
            \\end{eqnarray}

    """
    if fck<50:
        _εcu2 = 3.5
    else:
        _εcu2 = 2.6 + 35*((90-fck)/100)**4

    return _εcu2


def εcu3(fck):
    """

    Args:
        fck (float): Characteristic compressive cylinder strength of concrete at 28 days

    Returns:
        float: Given using the expressions:

        .. math::
            \\begin{eqnarray}
                ε_{cu2} & = & 3.5 & for & f_{ck} \le 50MPa \\\\
                ε_{cu2} & = & 2.6 + 35 \cdot ((90 - f_{ck})/100)^4 & for & f_{ck} \ge 50MPa
            \\end{eqnarray}

    """
    if fck<50:
        _εcu3 = 3.5
    else:
        _εcu3 = 2.6 + 35*((90-fck)/100)**4

    return _εcu3


def n(fck):
    """

    Args:
        fck (float): Characteristic compressive cylinder strength of concrete at 28 days

    Returns:
        float: Given using the expressions:

        .. math::
            \\begin{eqnarray}
                n & = & 2.0 & for & f_{ck} \le 50MPa \\\\
                n & = & 1.4 + 23.4 \cdot ((90 - f_{ck})/100)^4 & for & f_{ck} \ge 50MPa
            \\end{eqnarray}

    """
    if fck<50:
        _n = 2.0
    else:
        _n = 1.4 + 23.4*((90-fck)/100)**4

    return _n


def σc_nl(fck, εc):
    """
    Stress-strain relation for non-linear structural analysis

    Args:
        fck (float): Characteristic compressive cylinder strength of concrete at 28 days
        εc (float): concrete strain (‰)

    Returns:
        float: Given using the expression:

        .. math::
            \\begin{eqnarray}
                σ_{c} & = & f_{ctm}\dfrac{kη-η^2}{1+(k-2)η} \\\\
                where: & \\\\
                η & = & \dfrac{ε_c}{ε_{c1}} \\\\
                k & = & 1.05\cdot E_{cm} \cdot ε_{c1} / f_{cm}
            \\end{eqnarray}

    """
    _Ecm = elastic_deformation.Ecm(fck)
    _εc1 = εc1(fck)
    _fcm = strength.fcm(fck)

    η = εc / _εc1
    k = 1.05 * _Ecm * _εc1 / _fcm
    _σc = _fcm * (k * η - η * η)/ (1 + η * (k - 2))

    return _σc


def σc_design(fck, αcc, γc, εc):
    """
    Stress-strain relations for the design of cross-sections

    Args:
        fck (float): Characteristic compressive cylinder strength of concrete at 28 days
        αcc (float): Coefficient taking account of long term effects on the compressive strength
                     and of unfavourable effects resulting from the way the load is applied
        γc (float): Safety factor
        εc (float): concrete strain (‰)

    Returns:
        float: Given using the expression:

        .. math::
            \\begin{eqnarray}
                σ_{c} & = & f_{cd}\cdot(1-(1-\dfrac{ε_c}{ε_{c2}})^n) & for & 0\le ε_c \le ε_{c2} \\\\
                σ_{c} & = & f_{cd} & for & ε_{c2}\le ε_c \le ε_{cu2}
            \\end{eqnarray}

    """
    _fcd = strength.fcd(αcc, fck, γc)
    _εc2 = εc2(fck)
    _εcu2 = εcu2(fck)
    _n = n(fck)

    if εc < _εc2:
        _σc = _fcd * ( 1 - (1 - εc / _εc2)**_n)
    else:
        _σc = _fcd

    return _σc


def σc_bilin(fck, αcc, γc, εc):
    """

    Args:
        fck (float): Characteristic compressive cylinder strength of concrete at 28 days
        αcc (float): Coefficient taking account of long term effects on the compressive strength
                     and of unfavourable effects resulting from the way the load is applied
        γc (float): Safety factor
        εc (float): concrete strain (‰)

    Returns:
        float:

    """
    _fcd = strength.fcd(αcc, fck, γc)
    _εc3 = εc3(fck)

    if εc < _εc3:
        _σc = _fcd * εc / _εc3
    else:
        _σc = _fcd

    return _σc


