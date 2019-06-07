# encoding: utf-8
"""
Example script, comparing pyGDM with Mie theory for a constant ref.-index 
dielectric sphere (n=2)

"""
import numpy as np
import copy

from pyGDM2 import structures
from pyGDM2 import materials
from pyGDM2 import fields

from pyGDM2 import core
from pyGDM2 import tools
from pyGDM2 import linear


print("\n\n----------------- pyGDM scattering test -----------------")

#==============================================================================
# pyGDM setup
#==============================================================================
## ---------- Setup scale-factors for differntly fine meshes
## --- cubic
factors_cube = [0.8, 1.0, 1.25]

## --- hexagonal
factors_hex = [0.75, 1.0, 1.2]




#==============================================================================
# Setup incident field
#==============================================================================
field_generator = fields.planewave
## log-interval spectrum (denser at low lambda):
wavelengths = np.exp(np.linspace(np.log(300), np.log(1000), 30))
kwargs = dict(theta = [0.0])
efield = fields.efield(field_generator, wavelengths=wavelengths, kwargs=kwargs)




#==============================================================================
# Setup geometry (sphere D=300nm) / environment
#==============================================================================
material = materials.dummy(2.0)
n1, n2 = 1.0, 1.0     # vacuum environment


print("setting up test-simulations... ")
## --- cubic mesh
sim_cube = []
for fact in factors_cube:
    step = 37.5/fact
    radius = 4.*fact     # 37.5*4 = 150nm  -->  D=300nm
    geometry = structures.sphere(step, R=radius, mesh='cube')
    
    struct = structures.struct(step, geometry, material, n1,n2, 
                                   structures.get_normalization('cube'))
    
    sim = core.simulation(struct, efield) 
    sim_cube.append( copy.deepcopy(sim) )


## --- hexagonal mesh
sim_hex = []
for fact in factors_hex:
    step = 37.5/fact
    radius = 4.*fact
    geometry = structures.sphere(step, R=radius, mesh='hex', ORIENTATION=2)
    
    struct = structures.struct(step, geometry, material, n1,n2, 
                                   structures.get_normalization('hex'))
    
    sim = core.simulation(struct, efield) 
    sim_hex.append( copy.deepcopy(sim) )
print("done.")





#%%
#==============================================================================
# run the simulations
#==============================================================================
print("Running simulations:")

## --- cubic mesh
a_ext_cube = []
labels_cube = []
for sim in sim_cube:
    print('(cube) ----- N_dipoles = {} ...'.format(len(sim.struct.geometry)))
    
    E = core.scatter(sim, method='lu', verbose=False)
    
    ## extinction spectrum
    field_kwargs = tools.get_possible_field_params_spectra(sim)[0]
    wl, spec = tools.calculate_spectrum(sim, field_kwargs, linear.extinct)
    a_ext = spec.T[0]
    a_geo = tools.get_geometric_cross_section(sim)
    
    a_ext_cube.append(a_ext/a_geo)
    labels_cube.append(len(sim.struct.geometry))
    print('done.')


## --- hexagonal mesh
a_ext_hex = []
labels_hex = []
for sim in sim_hex:
    print('(hex) ----- N_dipoles = {} ...'.format(len(sim.struct.geometry)))
    
    E = core.scatter(sim, method='lu', verbose=False)

    ## extinction spectrum
    field_kwargs = tools.get_possible_field_params_spectra(sim)[0]
    wl, spec = tools.calculate_spectrum(sim, field_kwargs, linear.extinct)
    a_ext = spec.T[0]
    a_geo = tools.get_geometric_cross_section(sim)
    
    a_ext_hex.append(a_ext/a_geo)
    labels_hex.append(len(sim.struct.geometry))
    print('done.')

print("simulations done, loading reference...\n")
## Save reference data
#spectra = [wl]
#for i, (ae, lab) in enumerate(zip(a_ext_cube, labels_cube)):
#    spectra.append(ae)
#for i, (ae, lab) in enumerate(zip(a_ext_hex, labels_hex)):
#    spectra.append(ae)
#np.savetxt("test_scattering_dielectric_sphere.dat", np.transpose(spectra),
#           header='wavelength (nm), 3x cube mesh, 3x hex mesh test spectra')



#%%
reference_data = np.loadtxt("test_scattering_dielectric_sphere.dat").T


delta_wl = wl - reference_data[0]
delta_cube1 = (a_ext_cube[0] - reference_data[1]) / reference_data[1]
delta_cube2 = (a_ext_cube[1] - reference_data[2]) / reference_data[2]
delta_cube3 = (a_ext_cube[2] - reference_data[3]) / reference_data[3]
delta_hex1 = (a_ext_hex[0] - reference_data[4]) / reference_data[4]
delta_hex2 = (a_ext_hex[1] - reference_data[5]) / reference_data[5]
delta_hex3 = (a_ext_hex[2] - reference_data[6]) / reference_data[6]


if np.round(np.sum(delta_wl), 1) != 0 :
    raise ValueError("Test not consistent! It seems that not the same wavelengths have been used.")

error_level = 0
print("average, max., min. deviation")
for i,D in enumerate([delta_cube1,delta_cube2,delta_cube3, delta_hex1,delta_hex2,delta_hex3]):
    D = np.abs(D)
    print("Spectra #{}: {:.5g}, {:.5g}, {:.5g}".format(i, 
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
    print("\nScattering test finished succesfully.")


