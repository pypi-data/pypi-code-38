
import h5py
from astropy.io import ascii

catalogFile = '../catalogs/2MRS.csv'
cat = ascii.read(catalogFile,format='ecsv')
#create_all(catalogFile)
#cat = read_catalog()

print(cat)
print(cat.columns)

ras, decs = cat["RAJ2000"], cat["DEJ2000"]
cz = cat["cz"]
magk = cat["Ktmag"]

with h5py.File('../catalogs/2MRS.hdf5', 'w') as f:
    f.create_dataset('ra', data=ras)
    f.create_dataset('dec', data=decs)
    f.create_dataset('cz', data=cz)
    f.create_dataset('magk', data=magk)

