import astropy.units as u
import periodictable as pt
from ..atomicmass import atomicmass

def test_atomicmass():
    assert atomicmass('Na') == pt.Na.mass * u.u, 'Na mass failure'
    assert atomicmass('H2O') == pt.formulas.formula('H2O').mass * u.u, (
        'H2O mass failure')
    assert atomicmass('AAb') is None, 'Bad species failure'