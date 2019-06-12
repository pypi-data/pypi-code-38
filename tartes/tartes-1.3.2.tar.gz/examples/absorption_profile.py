import tartes
from pylab import *

print(tartes)

nlayer = 200           # number of layers
ssa = [20] * nlayer      # nlayer layers with the same SSA... (in m^2/kg)
density = [300] * nlayer  # and the same density               (in kg/m^3)
# all the layer are 0.01 m thick, the snowpack is nlayer*0.01m deep
thickness = [0.01] * nlayer

wavelengths = [400e-9, 500e-9, 600e-9, 700e-9, 800e-9, 900e-9]


for wl in wavelengths:
    z, absorption_profile = tartes.absorption_profile(
        wl, ssa, density, thickness, soilalbedo=0.50)
    semilogx(absorption_profile, -z, label='%g nm' % (wl * 1e9))

    albedo = tartes.albedo(wl, ssa, density, thickness, soilalbedo=0.50)
    print(1 - sum(absorption_profile), " ", albedo)

ylabel('depth(m)')
xlabel('absorbed energy (for 1W/m2 incident)')
legend(loc='best')
show()
