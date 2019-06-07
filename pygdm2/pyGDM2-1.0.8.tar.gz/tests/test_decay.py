# encoding: utf-8
import six; from six.moves import cPickle as pickle

import numpy as np

from pyGDM2 import structures
from pyGDM2 import materials
from pyGDM2 import fields

from pyGDM2 import core
from pyGDM2 import linear
from pyGDM2 import tools



print("\n\n----------------- pyGDM Decay rate test -----------------")

# =============================================================================
# Setup simulation
# =============================================================================
## ---------- Setup structure
mesh = 'cube'
step = 7.0
L = 21
geometry = structures.rect_wire(step, L=L/step,H=L/step, W=L/step, mesh=mesh)
geometry.T[2] += step/2.

material = materials.dummy(2.0)

n1, n2 = 1.0, 1.0
struct = structures.struct(step, geometry, material, n1,n2, 
                           structures.get_normalization(mesh),
                           with_radiation_correction=True)
struct = structures.center_struct(struct)



## ---------- Setup incident field
field_generator1 = fields.dipole_electric
field_generator2 = fields.dipole_magnetic
x0 = np.linspace(-250, 250, 25)
y0 = np.linspace(-250, 250, 25)
z0 = struct.geometry.T[2].max() + step/2. + 40

kwargs = dict(x0=x0, y0=y0, z0=z0,    # positions where to evaluate
              mx=0,my=0,mz=0)         # dipole orientation = (0,0,0) --> placeholder
wavelengths = [500]
efield_e = fields.efield(field_generator1, wavelengths=wavelengths, kwargs=kwargs)
efield_m = fields.efield(field_generator2, wavelengths=wavelengths, kwargs=kwargs)

## ---------- Simulation initialization
sim_e = core.simulation(struct, efield_e)
sim_m = core.simulation(struct, efield_m)



#%%
## --- main simulation
print("running main decay simulation...")
SBB_e = core.decay_rate(sim_e, method='lu', verbose=0)
SBB_m = core.decay_rate(sim_m, method='lu', verbose=0)


## list of dipole test orientations
MAP = tools.generate_NF_map(x0.min(),x0.max(),len(x0), y0.min(),y0.max(),len(y0), Z0=z0)
dp_list = [[1, 0, 0], 
           [0, 1, 0], 
           [0, 0, 1]]


## --- load reference data
## python 2/3 compatibility hack:
try:
    de, dm = pickle.load(open("test_decay.pcl","rb"), encoding='latin1')
except TypeError:
    de, dm = pickle.load(open("test_decay.pcl","rb"))
    
de_save_ref, dm_save_ref = [],[]  # for saving a reference


print("\naverage, max., min. deviation")
error_level = 0
for i, (mx,my,mz) in enumerate(dp_list):
    
    SBB_map_e = linear.decay_eval(sim_e, SBB_e[0], mx,my,mz, verbose=0)
    SBB_map_m = linear.decay_eval(sim_m, SBB_m[0], mx,my,mz, verbose=0)
    decay_e, ext = tools.map_to_grid_XY(MAP, SBB_map_e.T[-1])
    decay_m, ext = tools.map_to_grid_XY(MAP, SBB_map_m.T[-1])
    
    D1 = (decay_e - de[i]) / de[i]
    print("e-dipole, orientation #{}: {:.5g}, {:.5g}, {:.5g}".format(i, 
                                       np.average(D1), np.max(D1), np.min(D1)))
    D2 = (decay_m - dm[i]) / de[i]
    print("m-dipole, orientation #{}: {:.5g}, {:.5g}, {:.5g}".format(i, 
                                       np.average(D2), np.max(D2), np.min(D2)))
    
    
    if 1E-6 >= max([np.max(D1), np.max(D2)]) > 0:
        error_level = 1
        print("             minor deviation")
    if 1E-4 >= max([np.max(D1), np.max(D2)]) >= 1E-6:
        error_level = 2
        print("             small deviation")
    if max([np.max(D1), np.max(D2)]) > 1E-4:
        error_level = 3
        print("             !! Large deviation detected !!")
    
    
    ## to save the reference data, use these lists
    de_save_ref.append(decay_e)
    dm_save_ref.append(decay_m)


if error_level == 1:
    print("Minor deviations occurred. This is a normal consequence of a different processor architecture, a different fortran compiler or a double precision compilation (reference is single precision).")
elif error_level == 2:
    print("Small deviations occurred. Probably due to a different processor architecture, fortran compiler or a double precision compilation.")
elif error_level == 3:
    raise ValueError("Significant deviations between reference and calculation occurred (> 1E-4) !!!")

if error_level in [0,1,2]:
    print("\nDecay rate test finished succesfully.")


#import pickle
#pickle.dump([de_save_ref, dm_save_ref], open("test_decay.pcl","wb"))







