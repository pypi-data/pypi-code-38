from unithandler.base import Unit, UnitFloat, SI_DERIVED_UNITS

# todo figure out how to handle g/kg nicely
# SI base units
m = Unit('m')  # meter
kg = UnitFloat(1000, 'g')  # kilogram
s = Unit('s')  # second
A = Unit('A')  # ampere
K = Unit('K')  # kelvin
mol = Unit('mol')  # mole
cd = Unit('cd')  # candela
# convenience importing by full unit name
meter = m
kilogram = kg
second = s
ampere = A
kelvin = K
mole = mol
candela = cd

# SI derived units
Hz = Unit('/s')  # hertz
N = Unit(SI_DERIVED_UNITS['N'])  # newton
Pa = Unit(SI_DERIVED_UNITS['Pa'])  # pascal
J = Unit(SI_DERIVED_UNITS['J'])  # joule
W = Unit(SI_DERIVED_UNITS['W'])  # watt
C = Unit(SI_DERIVED_UNITS['C'])  # coulomb
V = Unit(SI_DERIVED_UNITS['V'])  # volt
F = Unit(SI_DERIVED_UNITS['F'])  # farad
ohm = Unit(SI_DERIVED_UNITS[f'\u2126'])  # ohm
S = Unit(SI_DERIVED_UNITS['S'])  # siemens
Wb = Unit(SI_DERIVED_UNITS['Wb'])  # weber
T = Unit(SI_DERIVED_UNITS['T'])  # tesla
H = Unit(SI_DERIVED_UNITS['H'])  # henry
lm = Unit(SI_DERIVED_UNITS['lm'])  # lumen
lx = Unit(SI_DERIVED_UNITS['lx'])  # lux
kat = Unit(SI_DERIVED_UNITS['kat'])  # katal
# convenience importing by full unit name
hertz = Hz
newton = N
pascal = Pa
joule = J
watt = W
coulomb = C
volt = V
farad = F
siemens = S
weber = Wb
tesla = T
henry = H
lumen = lm
lux = lx
katal = kat
