# encoding: utf-8
import six; from six.moves import cPickle as pickle

import numpy as np


from pyGDM2 import structures
from pyGDM2 import materials
from pyGDM2 import fields

from pyGDM2 import core
from pyGDM2 import linear

print("\n\n----------------- pyGDM Farfield pattern test -----------------")




# =============================================================================
# setup simulation
# =============================================================================
## ---------- Setup structure
mesh = 'cube'
step = 30.0
geometry = structures.hexagon(step, NSIDE=8,H=3, mesh=mesh)
geometry.T[2] += step
geometry = structures.center_struct(geometry)

material = materials.gold()

n1, n2 = 1.0, 1.0  # constant environment
struct = structures.struct(step, geometry, material, n1,n2, structures.get_normalization(mesh))


## ---------- Setup incident field
field_generator = fields.dipole_electric
kwargs = dict(x0=400.,y0=50.,z0=70., mx=1.,my=0.5,mz=0.3)

wavelengths = [400,600,800]                     # one single wavelength
efield = fields.efield(field_generator, wavelengths=wavelengths, kwargs=kwargs)


## ---------- initialize and run sim
sim = core.simulation(struct, efield)

EFIELD = core.scatter(sim, method='lu')


#%%
#==============================================================================
# Compare Fields calc/reference
#==============================================================================
R=10000.; Nteta=50; Nphi=72
tetamax = np.pi/2.

## --- load reference data
ff_scat_ref = []
## python 2/3 compatibility hack:
try:
    ff_scat = pickle.load(open("test_farfield_scattering.pcl","rb"), encoding='latin1')
except TypeError:
    ff_scat = pickle.load(open("test_farfield_scattering.pcl","rb"))


print("\naverage, max., min. deviation")
error_level = 0
for i in range(3):
    tetalist, philist, I_sc, I_tot, I0 = linear.farfield(
                                sim, field_index=i,
                                r=R, tetamin=0, tetamax=tetamax, Nteta=Nteta, Nphi=Nphi, 
                                polarizerangle='none')
    
    ff_scat_ref.append(I_sc)
    D = (ff_scat[i] - I_sc) / ff_scat[i]
    print("wavelength #{}: {:.5g}, {:.5g}, {:.5g}".format(i, 
                                       np.average(D), np.max(D), np.min(D)))

    if 1E-6 >= np.max(D) > 0:
        error_level = 1
        print("             minor deviation")
    if 1E-4 >= np.max(D) >= 1E-6:
        error_level = 2
        print("             small deviation")
    if np.max(D) > 1E-4:
        error_level = 3
        print("             !! Large deviation detected !!")
    #%% --- test plot of far-field patterns
#    from pyGDM2 import visu
#    import matplotlib.pyplot as plt
#    plt.subplot(121, polar=1); plt.title("calculated")
#    visu.farfield_pattern_2D(tetalist, philist, I_sc, degrees=True, show=False)
#    plt.subplot(122, polar=1); plt.title("reference")
#    visu.farfield_pattern_2D(tetalist, philist, ff_scat[i], degrees=True, show=False)
#    plt.show()

#%%
if error_level == 1:
    print("Minor deviations occurred. This is a normal consequence of a different processor architecture, a different fortran compiler or a double precision compilation (reference is single precision).")
elif error_level == 2:
    print("Small deviations occurred. Probably due to a different processor architecture, fortran compiler or a double precision compilation.")
elif error_level == 3:
    raise ValueError("Significant deviations between reference and calculation occurred (> 1E-4) !!!")

if error_level in [0,1,2]:
    print("\nFarfield pattern test finished succesfully.")



#import pickle
#pickle.dump(ff_scat, open("test_farfield_scattering.pcl","wb"))



