# -*- coding: utf-8 -*-

from __future__ import division

from j5basic import Units
from j5test import Utils
import operator

# TODO: Design decisions:
#  * How should Units and Scalars (Units with values) relate?
#    * What should arithmetic operations on Units do? Produce Scalars or derived Units
#    * Should we have Scalar classes derived from the numeric classes?
#  * How should derived Units be created?
#    * Units that are simply a scale of another (e.g. milli-X)
#    * Units that are combinations of others (e.g. meters per second squared)
#  * Should we have a registry of Units?
#    * This could use cached Units when they are automatically derived
#  * How are we going to handle string formatting?
#  * Should we use implementing-an-API as a way of declaring Units?
# Things to implement later:
#  * Families of related units (milli, centi, etc, etc for SI, feet, inches, etc for UK)
#  * Ways of setting up modules declaring sets of Units
#  * Handle composite units (pounds and cents, hours minutes and seconds, etc)

# Decisions:
#  * It makes more sense for operations on Units to produce Scalars, since that's the more common case
#  * We still need a way of declaring Units operationally
#  * An API-way of declaring Units would rock (i.e. them registering themselves)

def test_unit_class_creation():
    """Creation of Unit classes should successfully produce types"""
    m = Units.BaseUnit("m")
    assert isinstance(m, Units.Unit)
    # assert isinstance(m, type)

def test_unit_class_calculation():
    """Calculations on Units should result in derived Units"""
    m = Units.BaseUnit("m")
    mm = m / 1000
    assert isinstance(mm, Units.Unit)
    # assert isinstance(mm, type)
    # assert issubclass(mm, m)

    assert m / mm == Units.Unit("", {}, Units.Conversion(operator.mul, 1000))
    r = mm * 1000
    assert r.base_units == m.base_units
    assert r.op == m.op
    assert r == m
    assert mm * 1000 == m
    m_sq = m * m
    assert m_sq == m * m
    assert isinstance(m_sq, Units.Unit)
    # assert not issubclass(m_sq, m)
    s = Units.BaseUnit("s")
    h = s * 3600
    assert 1/s == 3600/h

def test_scalar_calculation():
    """tests that scalars created from units can be used in calculations"""
    m = Units.BaseUnit("m")
    s = Units.BaseUnit("s")
    mm = m / 1000
    x = m(35)
    assert x == mm(35000)
    assert m(35) + m(3) == m(38)
    assert m(35) - mm(3) == mm(34997)
    assert Utils.raises(ValueError, operator.add, m(35), 3)
    assert m(35) * 3 == m(105)
    assert m(35) * m(3) == (m*m)(35*3)
    assert Utils.raises(ValueError, operator.add, 3, m(35))
    assert 3 * m(35) == m(105)
    assert m(35) * m(3) == (m*m)(35*3)
    assert s(12.0) / 4.0 == s(3.0)
    assert 12.0 / s(4.0) == (1/s)(3.0)
    assert -s(5) == s(1) - s(6)
    assert +s(5) == s(1) + s(4)
    assert abs(s(-4)) == s(4)
    # These conversions are of debatable value, but are included at the moment
    assert float(m(35.0)) == 35.0
    assert int(m(35.2)) == 35
    assert int(mm(33000)) == 33000

def test_unit_class_combination():
    """Calculations involving multiple Units should be consistent"""
    m = Units.BaseUnit("m")
    km = 1000 * m
    s = Units.BaseUnit("s")
    min = s * 60
    hour = min * 60
    m_per_s = m / s
    assert isinstance(m_per_s, Units.Unit)
    km_per_hour = km / hour
    # assert issubclass(km_per_hour, m_per_s)
    assert m_per_s(10) == km_per_hour(36)
    assert m_per_s(9) < km_per_hour(36)
    assert m_per_s(20) > km_per_hour(70)

def test_random_calls_for_coverage():
    assert Units.Identity(3) == 3
    m = Units.BaseUnit("m")
    km = 1000 * m
    assert repr(km) == "Unit(m, SequentialConversion(Conversion(<built-in function mul>, *(1000,))))"
    assert repr(m)
