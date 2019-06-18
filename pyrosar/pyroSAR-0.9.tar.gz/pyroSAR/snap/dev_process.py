import os
from pyroSAR import identify
from pyroSAR.snap import geocode

maindir = '/geonfs01_vol1/ve39vem/S1_ARD/data'
# maindir = '/home/john/Desktop/S1_ARD/data'
# maindir = '/home/truc_jh/Desktop/S1_ARD/data'

filename = os.path.join(maindir, 'S1A_IW_GRDH_1SDV_20180829T170656_20180829T170721_023464_028DE0_F7BD.zip')
subset = os.path.join(maindir, 'test_subset.shp')

dem_id = 'TDX90m'
dem_file = os.path.join(maindir, 'DEM', 'S1A__IW___A_20180829T170656_dem_snap_AW3D30.tif')

id = identify(filename)

scenedir = os.path.join(maindir, 'SNAP2', '{}_{}'.format(id.outname_base(), dem_id))
correct_egm = False if dem_id == 'TDX90m' else True
print(scenedir)
geocode(infile=id,
        externalDEMFile=dem_file,
        externalDEMApplyEGM=correct_egm,
        externalDEMNoDataValue=-9999.0,
        outdir=scenedir, shapefile=subset,
        tr=90, scaling='db', test=True,
        export_extra=['incidenceAngleFromEllipsoid',
                      'localIncidenceAngle',
                      'projectedLocalIncidenceAngle'])
