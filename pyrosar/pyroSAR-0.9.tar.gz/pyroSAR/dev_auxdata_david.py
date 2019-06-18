import os
from pyroSAR.auxdata import dem_autoload, dem_create
from pyroSAR.gamma.dem import dem_autocreate
from spatialist import Vector

filename = '/home/truc_jh/Desktop/S1_ARD/data/testsite_alps.shp'

maindir = '/home/truc_jh/Desktop/DEM_test'

if not os.path.isdir(maindir):
    os.makedirs(maindir)

types = ['AW3D30']
# types = ['AW3D30', 'SRTM 1Sec HGT', 'SRTM 3Sec', 'TDX90m']

for demType in types:
    
    outname = os.path.join(maindir, '{}_alps_large.tif'.format(demType.replace(' ', '-')))
    
    vrt = outname.replace('.tif', '.vrt')
    if not os.path.isfile(vrt):
        with Vector(filename) as vec:
            vrt = dem_autoload([vec], demType=demType, vrt=vrt, buffer=3.0,
                               username='john.truckenbrodt@uni-jena.de', password='Rbv823rv%&')
    
    if not os.path.isfile(outname):
        dem_create(vrt, outname)
    
    # outname_utm = outname.replace('.tif', '_utm.tif')
    # if not os.path.isfile(outname_utm):
    #     dem_create(vrt, outname_utm, t_srs=32632, tr=(30, 30), geoid_convert=False)
    
    outname_ellp = outname.replace('.tif', '_wgs84_ellp.tif')
    if not os.path.isfile(outname_ellp):
        dem_create(vrt, outname_ellp, geoid_convert=True)
    #
    # outname_gamma = outname.replace('.tif', '_gamma_utm_ellp')
    # if not os.path.isfile(outname_gamma):
    #     with Vector(filename) as vec:
    #         dem_autocreate(vec, demType, outname_gamma,
    #                        buffer=0.05, t_srs=32632, tr=(30, 30))
