import os
print(os.getcwd())

help("modules")

print('start import')

from pyIMD.imd import InertialMassDetermination

print('import success')

# Create the inertial mass determination object
imd = InertialMassDetermination()

print('obj created')
print(imd)