from unithandler.base import Unit, UnitFloat, si_derived_units

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
N = Unit(si_derived_units['N'])  # newton
Pa = Unit(si_derived_units['Pa'])  # pascal
J = Unit(si_derived_units['J'])  # joule
W = Unit(si_derived_units['W'])  # watt
C = Unit(si_derived_units['C'])  # coulomb
V = Unit(si_derived_units['V'])  # volt
F = Unit(si_derived_units['F'])  # farad
ohm = Unit(si_derived_units[f'\u2126'])  # ohm
S = Unit(si_derived_units['S'])  # siemens
Wb = Unit(si_derived_units['Wb'])  # weber
T = Unit(si_derived_units['T'])  # tesla
H = Unit(si_derived_units['H'])  # henry
lm = Unit(si_derived_units['lm'])  # lumen
lx = Unit(si_derived_units['lx'])  # lux
kat = Unit(si_derived_units['kat'])  # katal
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
