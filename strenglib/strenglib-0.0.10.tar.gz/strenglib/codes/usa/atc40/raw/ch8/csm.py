import math

def PF1(m, φ):
    """ Modal participation factor for the first natural mode

    .. highlight:: python
    .. code-block:: python
       :linenos:


        PF1 = csm_atc40.PF1(m=np.array([39.08, 39.08, 39.08]),
                            φ=np.array([0.0483, 0.0920, 0.1217]))


    Args:
        m (np.array): mass assigned to level i
        φ (np.array): amplitude of mode 1 al level i

    Returns:
        float: Given using the expression:

        .. math::  PF_1 = \dfrac{\sum(m_i \cdot φ_i)}{\sum(m_i \cdot φ_i^2)}
    """
    return sum(m*φ)/sum(m*φ*φ)


def α1(m, φ):
    """ Modal mass coefficient for the first natural mode

    .. highlight:: python
    .. code-block:: python
       :linenos:


        α1 = csm_atc40.α1(m=np.array([39.08, 39.08, 39.08]),
                          φ=np.array([0.0483, 0.0920, 0.1217]))


    Args:
        m (np.array): mass assigned to level i
        φ (np.array): amplitude of mode 1 al level i

    Returns:
        float: Given using the expression:

        .. math::  α_1 = \dfrac{\sum(m_i \cdot φ_i)^2}{\sum(m_i) \cdot \sum(m_i \cdot φ_i^2)}
    """
    return sum(m * φ)**2 / (sum(m)*sum(m*φ*φ))


def Sa(V, W, α1):
    """ The spectral acceleration

    .. highlight:: python
    .. code-block:: python
       :linenos:

        Sa = csm_atc40.Sa(V=bl.y_ini,
                          W=sum(m),
                          α1=α1) # Βάζω όπου W τη μάζα ώστε να βγει το Sa σε m/sec2 και όχι σε g


    Args:
        V (float): base shear
        W (float): building weight (dead plus likely live loads...eg g+0.3q)
        α1 (float): modal mass coefficient for the first natural mode

    Returns:
        float: Given using the expression:

        .. math::  S_a = \dfrac{V/W}{α_1}
    """
    return (V/W)/α1


def Sd(Δroof, PF1, φroof1):
    return Δroof / (PF1*φroof1)


def T(Sa, Sd):
    return 2*math.pi*(Sd/Sa)**0.5


def β0(dy, ay, dpi, api):
    return (2/math.pi)*(ay*dpi-dy*api)/(api*dpi)


def βeff(β, β0, behavior):
    # Το όριο του 0.45 φαίνεται στa Figure 8-15, 8-16
    if β0 > 0.45:
        β0 = 0.45

    _κ = κ(β0, behavior)
    return β + _κ * β0


def κ(β0, behavior):
    # Το όριο του 0.45 φαίνεται στa Figure 8-15, 8-16
    if β0 > 0.45:
        β0 = 0.45

    if behavior == 'A':
        if β0 <= 0.1625:
            return 1.0
        else:
            return 1.13 - 0.51 * math.pi / 2 * β0
    elif behavior == 'B':
        if β0 <= 0.25:
            return 0.67
        else:
            return 0.845 - 0.446 * math.pi / 2 * β0
    else:
        return 0.33


def SRA(βeff, behavior):
    if behavior == 'A':
        minSRA = 0.33
    elif behavior == 'B':
        minSRA = 0.44
    else:
        minSRA = 0.56

    return max(minSRA, ((3.21 - 0.68 * math.log(100 * βeff)) / 2.12))


def SRV(βeff, behavior):
    if behavior == 'A':
        minSRV = 0.50
    elif behavior == 'B':
        minSRV = 0.56
    else:
        minSRV = 0.69

    return max(minSRV, ((2.31 - 0.41 * math.log(100 * βeff)) / 1.65))