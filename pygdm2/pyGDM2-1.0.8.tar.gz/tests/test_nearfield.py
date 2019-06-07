# encoding: utf-8
import six; from six.moves import cPickle as pickle

import numpy as np

from pyGDM2 import structures
from pyGDM2 import materials
from pyGDM2 import fields

from pyGDM2 import core
from pyGDM2 import linear
from pyGDM2 import tools



print("\n\n----------------- pyGDM nearfield test -----------------")




## ---------- Setup structure
mesh = 'cube'
step = 30.0
geometry = structures.rect_wire(step, L=10,H=4,W=4, mesh=mesh)
geometry = structures.center_struct(geometry)

material = materials.silicon()


n1, n2 = 1.0, 1.0  # constant environment
struct = structures.struct(step, geometry, material, n1,n2, structures.get_normalization(mesh))


field_generator = fields.planewave        # planwave excitation
kwargs = dict(theta = [0.0, 90.0])              # single polarizations
wavelengths = [800.]                     # one single wavelength
efield = fields.efield(field_generator, wavelengths=wavelengths, kwargs=kwargs)


## ---------- Simulation initialization
sim = core.simulation(struct, efield)

EFIELD = core.scatter(sim)





#%%
#==============================================================================
# Compare Fields old/new
#==============================================================================
MAP = tools.generate_NF_map(-500,500,10, -500,500,10, Z0=200)

## --- load reference data
fields_ref = []
## python 2/3 compatibility hack:
try:
    fields = pickle.load(open("test_nearfield.pcl","rb"), encoding='latin1')
except TypeError:
    fields = pickle.load(open("test_nearfield.pcl","rb"))


print("\naverage, max., min. deviation (absolute values of complex)")
error_level = 0
for field_index in range(2):
    Es, E1, Bs, B1 = linear.nearfield(sim, field_index, MAP)
    Ei = tools.get_field_as_list_by_fieldindex(sim, field_index)
    
    fields_ref.append([Es, E1, Bs, B1, Ei])
    field_labels=['E scattered', 'E total', 'B scattered', 'B total', 'E internal']
    print("polarization: ", kwargs['theta'][field_index])
    for i,f in enumerate(fields[field_index]):
        D = np.abs((f-fields_ref[field_index][i])/f)
        
        print("  - field: {}: {:.5g}, {:.5g}, {:.5g}".format(field_labels[i], 
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
    
    

if error_level == 1:
    print("Minor deviations occurred. This is a normal consequence of a different processor architecture, a different fortran compiler or a double precision compilation (reference is single precision).")
elif error_level == 2:
    print("Small deviations occurred. Probably due to a different processor architecture, fortran compiler or a double precision compilation.")
elif error_level == 3:
    raise ValueError("Significant deviations between reference and calculation occurred (> 1E-4) !!!")

if error_level in [0,1,2]:
    print("\nNearfield test finished succesfully.")



#import pickle
#pickle.dump(fields_ref, open("test_nearfield.pcl","wb"))



    
