from __future__ import print_function, division

import numpy as np
import matplotlib.pyplot as plt

from pyGDM2 import fields
from pyGDM2 import tools
from pyGDM2 import visu

from pyGDM2 import visu3d
#%%


## --- single focused beam, left circular polarized
field_generator_1 = fields.focused_planewave
kwargs1 = dict(theta=None, spotsize=200,
               xSpot=0, ySpot=0,
               polarization_state=(np.cos(np.pi/4.), np.cos(np.pi/4.), np.pi/2., 0))

## --- right circular polarized plane wave
#field_generator_2 = fields.planewave
#kwargs2 = dict(polarization_state=(np.cos(np.pi/4.), np.cos(np.pi/4.), -np.pi/2., 0))


## --- gaussian, left circular polarized
field_generator_2 = fields.gaussian
kwargs2 = dict(theta=None, spotsize=200,
               polarization_state=(np.cos(np.pi/4.), np.cos(np.pi/4.), np.pi/2., 0))




## --- test-setting for field-evaluation
n3 = 1.0
n2 = 1.0
n1 = 1.0
spacing = 5000.0

## --- 2D evaluation volume (plane)
projection = 'XZ'
r_probe = tools.generate_NF_map(-1000,1000,50, -500,1000,50,0, projection=projection)

## --- evaluate the field-generators on the test XZ-map
wavelength = 800
NF_1 = tools.evaluate_incident_field(field_generator_1, wavelength, kwargs1, r_probe,
                                   n1=n1,n2=n2,n3=n3, spacing=spacing)
NF_2 = tools.evaluate_incident_field(field_generator_2, wavelength, kwargs2, r_probe,
                                   n1=n1,n2=n2,n3=n3, spacing=spacing)



plt.figure(figsize=(10,5))
plt.subplot(121, aspect='equal')
v = visu.vectorfield(NF_1, complex_part='real', projection=projection,
                     tit=projection+' real part, focused pw', show=0)

plt.subplot(122, aspect='equal')
v = visu.vectorfield(NF_2, complex_part='real', projection=projection,
                     tit=projection+' real part, planewave', show=0)

plt.show()
#print (np.abs(NF_1-NF_2).sum())


#%%
visu3d.animate_vectorfield(NF_1, scale=50)