from unithandler.base import Constant
from unithandler.siunits import second, meter, kelvin, kilogram, mole

# time
minute = second * 60 / 'min'
hour = minute * 60 / 'hour/min'
day = hour * 24 / 'day/hour'
year = day * 365 / 'year/day'

# distance
foot = meter / 3.28084 / 'ft'
inch = meter / 39.3701 / 'in'
mile = meter * 1609.34 / 'mile'
nmile = meter * 1851 / 'nmile'

# temperature
# C = kelvin + 273.15

# volume
liter = meter ** 3 / 1000 / 'L'

# mass
g = kilogram * 1000 / 'g'
lb = kilogram * 0.453592 / 'lb'

# concentration
molar = mole / liter
M = molar