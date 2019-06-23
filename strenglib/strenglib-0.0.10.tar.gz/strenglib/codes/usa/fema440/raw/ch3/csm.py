import math
from ....atc40.raw.ch8 import csm as csm_atc40


def Teq(T0, μ, α):
    if μ <= 1.0:
        return T0
    else:
        return T0 * (μ / (1 + α*μ - α))**0.5


def β0(μ, α):
    if μ<1.0:
        return 0.
    else:
        return (2/math.pi)*((μ-1)*(1-α))/(μ*(1+α*μ-α))