import numpy as np
import math


def αg(αgR, γI):
    """

    Args:
        αgR (float): reference peak ground acceleration on type A ground
        γI: (float): importance factor

    Returns:
        float: design ground acceleration on type A ground

    """
    return αgR * γI


def S(ground_type, spectrum_type):
    """

    Args:
        ground_type (str): Ground type (A, B, C, D or E)
        spectrum_type (int): Spectrum type 1 or 2

    Returns:
        float: soil factor

    """
    data = {}
    if spectrum_type == 1: data = {'A': 1.0, 'B': 1.2, 'C': 1.15, 'D': 1.35, 'E': 1.4}
    if spectrum_type == 2: data = {'A': 1.0, 'B': 1.35, 'C': 1.5, 'D': 1.8, 'E': 1.6}
    return data[ground_type]


def TB(ground_type, spectrum_type):
    """

    Args:
        ground_type (str): Ground type (A, B, C, D or E)
        spectrum_type (int): Spectrum type 1 or 2

    Returns:
        float: The lower limit of the period of the constant spectral acceleration branch

    """
    data = {}
    if spectrum_type == 1: data = {'A': 0.15, 'B': 0.15, 'C': 0.20, 'D': 0.15, 'E': 0.15}
    if spectrum_type == 2: data = {'A': 0.05, 'B': 0.05, 'C': 0.10, 'D': 0.10, 'E': 0.05}
    return data[ground_type]


def TC(ground_type, spectrum_type):
    """

    Args:
        ground_type (str): Ground type (A, B, C, D or E)
        spectrum_type (int): Spectrum type 1 or 2

    Returns:
        float: The upper limit of the period of the constant spectral acceleration branch

    """
    data = {}
    if spectrum_type == 1: data = {'A': 0.40, 'B': 0.50, 'C': 0.60, 'D': 0.80, 'E': 0.5}
    if spectrum_type == 2: data = {'A': 0.25, 'B': 0.25, 'C': 0.25, 'D': 0.30, 'E': 0.25}
    return data[ground_type]


def TD(ground_type, spectrum_type):
    """

    Args:
        ground_type (str): Ground type (A, B, C, D or E)
        spectrum_type (int): Spectrum type 1 or 2

    Returns:
        float: The value defining the beginning of the constant displacement response range of the spectrum

    """
    data = {}
    if spectrum_type == 1: data = {'A': 2.00, 'B': 2.00, 'C': 2.00, 'D': 2.00, 'E': 2.00}
    if spectrum_type == 2: data = {'A': 1.20, 'B': 1.20, 'C': 1.20, 'D': 1.20, 'E': 1.20}
    return data[ground_type]


def Se(T, αg, S, TB, TC, TD,  η = 1.0):
    """

    Args:
        T (float): The vibration period of a linear single-degree-of-freedom system
        αg (float): The design ground acceleration on type A ground (ag = γI*agR)
        S (float): The soil factor
        TB (float): The lower limit of the period of the constant spectral acceleration branch
        TC (float): The upper limit of the period of the constant spectral acceleration branch
        TD (float): The value defining the beginning of the constant displacement response range of the spectrum
        η (float): The damping correction factor with a reference value of η = 1 for 5% viscous damping

    Returns:
        float: The elastic acceleration response spectrum. Given using the expressions:

        .. math::
            :nowrap:

            \\begin{eqnarray}
                0 \le T \le T_B \\rightarrow & S_e(T) & = α_g\cdot S \cdot (1+\dfrac{T}{T_B}\cdot(η\cdot 2.5 -1)) \\\\
                T_B \le T \le T_C \\rightarrow & S_e(T) & = α_g\cdot S \cdot η\cdot 2.5 \\\\
                T_C \le T \le T_D \\rightarrow & S_e(T) & = α_g\cdot S \cdot η\cdot 2.5\cdot \dfrac{T_C}{T} \\\\
                T_D \le T \le 4s \\rightarrow & S_e(T) & = α_g\cdot S \cdot η\cdot 2.5\cdot \dfrac{T_C\cdot T_D}{T^2}
            \\end{eqnarray}

    """
    condlist = [T <= TB,
                T <= TC,
                T <= TD,
                T <= 4]
    choicelist = [αg * S * (1.0 + (T / TB) * (η * 2.5 - 1)),
                  αg * S * η * 2.5,
                  αg * S * η * 2.5 * (TC / T),
                  αg * S * η * 2.5 * (TC * TD / T ** 2)]
    return np.select(condlist, choicelist)


def SDe(T, Se):
    """

    Args:
        T (float): The vibration period of a linear single-degree-of-freedom system
        Se (float):The elastic acceleration response spectrum

    Returns:
        float: The elastic displacement response spectrum. Given using the expression:

        .. math::
            S_{De}=S_e(T)\cdot(\dfrac{T}{2π})^2

    """
    return Se * (T / (2 * math.pi)) ** 2


def dg(αg, S, TC, TD):
    """

    Args:
        αg (float): The design ground acceleration on type A ground (ag = γI*agR)
        S (float): The soil factor
        TC (float): The upper limit of the period of the constant spectral acceleration branch
        TD (float): The value defining the beginning of the constant displacement response range of the spectrum

    Returns:
        float: Design ground displacement. Given using the expression:

         .. math::
            d_{g}=0.025\cdot α_g \cdot S \cdot T_C  \cdot T_D

    """
    return 0.025 * αg * S * TC * TD


def Sd(T, αg, S, TB, TC, TD, q, β=0.2):
    """

    Args:
        T (float): The vibration period of a linear single-degree-of-freedom system
        αg (float): The design ground acceleration on type A ground (ag = γI*agR)
        S (float): The soil factor
        TB (float): The lower limit of the period of the constant spectral acceleration branch
        TC (float): The upper limit of the period of the constant spectral acceleration branch
        TD (float): The value defining the beginning of the constant displacement response range of the spectrum
        q (float): The behaviour factor
        β (float): The lower bound factor for the horizontal design spectrum. Recommended value for β is 0.2

    Returns:
        float: Design spectrum for elastic analysis. Given using the expressions:

        .. math::
            :nowrap:

            \\begin{eqnarray}
                0 \le T \le T_B \\rightarrow & S_d(T) & = α_g\cdot S \cdot (\dfrac{2}{3}+\dfrac{T}{T_B}\cdot(\dfrac{2.5}{q} - \dfrac{2}{3})) \\\\
                T_B \le T \le T_C \\rightarrow & S_d(T) & = α_g\cdot S \cdot \dfrac{2.5}{q} \\\\
                T_C \le T \le T_D \\rightarrow & S_d(T) & = α_g\cdot S \cdot \dfrac{2.5}{q} \cdot \dfrac{T_C}{T} \ge β \cdot α_g \\\\
                T_D \le T \le 4s \\rightarrow & S_d(T) & = α_g\cdot S \cdot \dfrac{2.5}{q} \cdot \dfrac{T_C\cdot T_D}{T^2} \ge β \cdot α_g
            \\end{eqnarray}

    """
    condlist = [T <= TB,
                T <= TC,
                T <= TD,
                T <= 4]
    choicelist = [αg * S * (2.0 / 3.0 + (T / TB) * (2.5 / q - 2.0 / 3.0)),
                    αg * S * 2.5 / q,
                    np.maximum(αg * S * (2.5 / q) * (TC / T), β * αg),
                    np.maximum(αg * S * (2.5 / q) * (TC * TD / T**2), β * αg)]
    return np.select(condlist, choicelist)


def η(ξ):
    """

    Args:
        ξ (float): the viscous damping ratio of the structure[%]

    Returns:
        float: The value of the damping correction factor. Given using the expressions:

        .. math::
            η = \sqrt{\dfrac{10}{5+ξ}} \ge 0.55
    """

    return max(0.55, (10. / (5. + ξ)) ** 0.5)

