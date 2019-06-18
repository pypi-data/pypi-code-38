import os
from pyroSAR import identify
from pyroSAR import gamma
from pyroSAR.gamma.auxil import par2hdr
from pyroSAR.gamma.api import diff
from pyroSAR.auxdata import dem_autoload, dem_create

from spatialist import Vector, Raster

maindir = '/home/truc_jh/Desktop/S1_ARD/data'

scene = os.path.join(maindir, 'S1B_IW_GRDH_1SDV_20180827T052558_20180827T052623_012444_016F26_3DE1.zip')

procdir = os.path.join(maindir, 'GAMMA', 'test_S1B')

id = identify(scene)

site = os.path.join(maindir, 'testsite_alps.shp')

tr = (20, 20)

buffer = 10

dem_snap = os.path.join(procdir, 'dem_aw3d30_snap_b{:02d}.tif'.format(buffer))
dem_gamma = os.path.join(procdir, 'dem_aw3d30_gamma_b{:02d}'.format(buffer))

if not os.path.isfile(dem_snap):
    with Vector(site) as vec:
        vrt = dem_autoload(geometries=[vec],
                           demType='AW3D30',
                           vrt='/vsimem/dem_tmp.vrt',
                           buffer=buffer / 10)
        # create a DEM GTiff file from the VRT
        dem_create(src=vrt, dst=dem_snap,
                   # t_srs=32632, tr=tr,
                   geoid_convert=True)

if not os.path.isfile(dem_gamma):
    inlist = ['UTM', 'WGS84', 1, 32, 0, os.path.basename(dem_gamma), '', '', '', '', '',
              '-{0} {1}'.format(*tr), '']
    
    # with Raster(dem_snap) as ras:
    #     post_lon, post_lat = ras.res
    # inlist = ['EQA', 'WGS84', 1, os.path.basename(dem_gamma), '', '', '', '', '',
    #           '-{0} {1}'.format(post_lon, post_lat), '']
    
    parfile = dem_gamma + '.par'
    if not os.path.isfile(parfile):
        diff.create_dem_par(DEM_par=parfile,
                            inlist=inlist)
    diff.dem_import(input_DEM=dem_snap,
                    DEM=dem_gamma,
                    DEM_par=parfile)
    par2hdr(parfile, parfile.replace('.par', '.hdr'))


subdir = os.path.join(procdir, os.path.basename(dem_gamma) + '_proc')
if not os.path.isdir(subdir):
    print(dem_gamma)
    os.makedirs(subdir)
    gamma.geocode(scene=scene,
                  dem=dem_gamma,
                  tempdir=os.path.join(subdir, 'process'),
                  outdir=subdir,
                  targetres=20,
                  scaling='db',
                  export_extra=['inc_geo', 'ls_map_geo'])
