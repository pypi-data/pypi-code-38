import numpy as np
import astropy.units as u
from ..interpu import interpu


def test_interpu():
    x = np.arange(20) * u.km
    y = x**3 - 3*x**2*u.km + 5*u.km**3

    points = np.random.rand(10)*20.

    result0 = np.interp(points, x.value, y.value)

    points1 = points*u.km
    points1 = points1.to(u.imperial.mi)
    result1 = interpu(points1, x, y)

    assert np.all(np.abs(result0 - result1.value) < 1e-8)
