""" Shear
"""

import math
from collections import namedtuple

def VRdc(CRdc, Asl, fck, σcp, bw, d, units='N-mm'):
    """ The design value for the shear resistance :math:`V_{Rd,c}` [N]

    Units are 'N-mm', unless specified otherwise. Alternative options are: 'kN-m'

    .. highlight:: python
    .. code-block:: python
       :linenos:

        vrdc = shear.VRdc(CRdc=0.12,
                               Asl=308,
                               fck=20.,
                               σcp=0.66667,
                               bw=250.,
                               d=539.,
                               units='N-mm')

    Args:
        CRdc (float): 0.18/γc
        Asl (float): [mm2] is the area of the tensile reinforcement
        fck (float): [N/mm2]
        σcp (float):  :math:`σ_{cp}=N_{Ed}/A_c \lt 0.2f_{cd}` [N/mm2]
        bw (float): The smallest width of the cross-section in the tensile area. [mm]
        d (float): Effective depth of the cross-section. [mm]

    Returns:
        VRdc (dict):

        Result value in [N], unless specified otherwise. Intermediate results are always 'N-mm'

        Given using the expressions

        .. math::
            V_{Rd,c} = max \\left\{\\begin{matrix}
            [C_{Rd,c} \cdot k \cdot(100\cdot ρ_l\cdot f_{ck})^{1/3} + k_1 \cdot σ_{cp}] \cdot b_w \cdot d \\\\
            (v_{min} + k_1 \cdot σ_{cp}) \cdot b_w \cdot d
            \\end{matrix}\\right.

        where:

        - :math:`k=1 + \sqrt{\dfrac{200}{d}} <= 2.0`

        - :math:`ρ_l=\dfrac{A_{sl}}{b_w \cdot d}<=0.02`

        - :math:`k_1 = 0.15`

    """
    _VRdc = {}

    if units == 'N-mm':
        pass
    elif units == 'kN-m':
        Asl = Asl * 10**6
        fck *= 0.001
        σcp *= 0.001
        bw *= 1000
        d *= 1000
    else:
        pass


    ρl = min(Asl / (bw * d), 0.02)
    k = min(1 + (200.0 / d)**0.5, 2.0)
    vmin = 0.035 * k**1.5 * fck**0.5
    k1 = 0.15

    VRdc1 = (CRdc * k * math.pow((100 * ρl * fck), (1/3)) + k1 * σcp) * bw * d
    VRdc2 = (vmin + k1 * σcp) * bw * d

    _VRdc['ρl'] = ρl
    _VRdc['k'] = k
    _VRdc['vmin'] = vmin
    _VRdc['k1'] = k1
    _VRdc['VRdc1'] = VRdc1
    _VRdc['VRdc2'] = VRdc2
    _VRdc['value'] = max(VRdc1, VRdc2)

    if units == 'N-mm':
        pass
    elif units == 'kN-m':
        _VRdc['value'] *= 0.001
    else:
        pass

    return _VRdc


def VRdmax(bw, d, fck, fyk, fywk, θ, αcw = 1.0, γc = 1.5, units='N-mm-rad'):
    """ Maximum value for the shear resistance :math:`V_{Rd,max}` [N]

    Units are 'N-mm', unless specified otherwise. Alternative options are: 'kN-m-rad'

    .. highlight:: python
    .. code-block:: python
       :linenos:

        vrdmax = shear.VRdmax(bw=250.,
                              d=539.,
                              fck=20.,
                              fyk=500.,
                              fywk=500.,
                              θ=np.pi/4,
                              αcw = 1.0,
                              γc = 1.5,
                              units='N-mm-rad')

    Args:
        bw (float): The smallest width of the cross-section in the tensile area. [mm]
        d (float): Effective depth of the cross-section. [mm]
        fck (float): [N/mm2]
        fyk (float): [N/mm2]
        fywk (float): [N/mm2]
        θ (float): Τhe angle between the concrete compression strut and the beam axis is the angle
            between the concrete compression strut and the beam axis [rad]
        αcw (float): Coefficient taking account of the state of the stress in the compression chord


    Returns:
        VRdmax (dict):

        Result value in [N], unless specified otherwise. Intermediate results are always 'N-mm'

        Given using the expression

        .. math::
            V_{Rd,max} = \dfrac{α_{cw}\cdot b_w \cdot z \cdot ν_1 \cdot f_{cd}}{\cot θ + \\tan θ}


    """
    if units == 'N-mm-rad':
        pass
    elif units == 'kN-m-rad':
        bw *= 1000
        d *= 1000
        fck *= 0.001
        fyk *= 0.001
        fywk *= 0.001
    else:
        pass

    _VRdmax = {}

    z = 0.9 * d
    fcd = fck / γc

    if fywk<0.8*fyk:
        if fck <= 60:
            v1 = 0.6
        else:
            v1 = max(0.5, 0.9-fck/200)
    else:
        v1 = 0.6 * (1-fck/250)

    _VRdmax['z'] = z
    _VRdmax['fcd'] = fcd
    _VRdmax['v1'] = v1

    _VRdmax['value'] = αcw * bw * z * v1 * fcd  / (math.tan(θ) + 1/math.tan(θ))

    if units == 'N-mm-rad':
        pass
    elif units == 'kN-m-rad':
        _VRdmax['value'] *= 0.001
    else:
        pass

    return _VRdmax


def VRds(nw, diaw, d, fyk, fywk, θ, s, γs = 1.15, units='N-mm-rad'):
    """ Shear resistance for members with vertical shear reinforcement :math:`V_{Rd,s}` [N]

    Units are 'N-mm-rad', unless specified otherwise. Alternative options are: 'kN-m-rad'

    .. highlight:: python
    .. code-block:: python
       :linenos:

        vrds = shear.VRds(nw=2.,
                          diaw = 8,
                          d=539,
                          fyk=500.,
                          fywk=500.,
                          θ=np.pi/4,
                          s = 169,
                          γs = 1.15,
                          units='N-mm-rad')

    Args:
        nw (float): number of hoop legs.
        diaw (float): hoop bars diameter. [mm]
        d (float): Effective depth of the cross-section. [mm]
        fyk (float): [N/mm2]
        fywk (float): [N/mm2]
        θ (float): Τhe angle between the concrete compression strut and the beam axis is the angle
            between the concrete compression strut and the beam axis [rad]
        s (float): the spacing of the stirrups [mm]


    Returns:
        VRds (dict):

        Result value in [N], unless specified otherwise. Intermediate results are always 'N-mm'

        Given using the expression

        .. math::
            V_{Rd,max} = \dfrac{A_{sw}}{s} \cdot z \cdot f_{ywd} \cdot \cot θ

    """
    if units == 'N-mm-rad':
        pass
    elif units == 'kN-m-rad':
        diaw = 1000. * diaw
        d = 1000. * d
        fyk = 0.001 * fyk
        fywk = 0.001 * fywk
        s = 1000. * s
    else:
        pass

    _VRds = {}

    z = 0.9 * d
    Asw = nw * math.pi * diaw**2 /4

    if fywk<0.8*fyk:
        fywd = min(0.8*fywk, fywk/γs)
    else:
        fywd = fywk/γs

    _VRds['Asw'] = Asw
    _VRds['fywd'] = fywd

    _VRds['value'] = (Asw / s) * z * fywd * (1./math.tan(θ))



    if units == 'N-mm-rad':
        pass
    elif units == 'kN-m-rad':
        _VRds['value'] *= 0.001
    else:
        pass

    return _VRds

