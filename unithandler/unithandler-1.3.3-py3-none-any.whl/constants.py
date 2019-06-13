from unithandler.base import Constant

# todo finish populating
g = Constant(9.8, 'm/s2')  # acceleration on earth
c = Constant(299792458, 'm/s')  # speed of light in vacuum
G = Constant(6.67408, 'm3kg-1s-2')  # Newtonian constant of gravitation
h = Constant(6.626070040e-34, 'Js')  # Planck constant
e = Constant(1.6021766208e-19, 'C')  # elementary charge
NA = Constant(6.022140857e23, 'mol-1')  # Avogadro's number
R = Constant(8.3144598, 'J/mol/K')  # molar gas constant
k = R/NA  # Boltzmann constant