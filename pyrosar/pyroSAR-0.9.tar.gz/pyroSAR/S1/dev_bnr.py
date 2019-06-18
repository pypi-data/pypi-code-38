import os
import shutil
import numpy as np
from pyroSAR import identify
import xml.etree.ElementTree as ET

from osgeo import gdal
from osgeo.gdalconst import GA_Update

import pyroSAR.S1.linesimplify as ls

# maindir = 'E:\\DATA\\S1_ARD\\data'
maindir = '/home/truc_jh/Desktop/S1_ARD/data'

scene = os.path.join(maindir, 'S1A_IW_GRDH_1SDV_20180101T170648_20180101T170713_019964_021FFD_DA78.zip')

dem_gamma = os.path.join(maindir, 'DEM', 'alps_dem_gamma_AW3D30')

outdir = os.path.join(maindir, 'GAMMA', 'stack', 'process')

unpacked = os.path.join(outdir, 'S1A_IW_GRDH_1SDV_20180101T170648_20180101T170713_019964_021FFD_DA78.SAFE')
if not os.path.isdir(unpacked):
    scene = identify(scene)
    scene.unpack(outdir)
else:
    scene = identify(unpacked)

if scene.compression is not None:
    raise RuntimeError('scene is not yet unpacked')

blocksize = 2000

# compute noise scaling factor
if scene.meta['IPF_version'] >= 2.9:
    print('border noise removal not necessary for IPF version {}'.format(scene.meta['IPF_version']))
elif scene.meta['IPF_version'] <= 2.5:
    knoise = {'IW': 75088.7, 'EW': 56065.87}[scene.acquisition_mode]
    cads = scene.getFileObj(scene.findfiles('calibration-s1[ab]-[ie]w-grd-(?:hh|vv)')[0])
    caltree = ET.fromstring(cads.read())
    cads.close()
    adn = float(caltree.find('.//calibrationVector/dn').text.split()[0])
    if scene.meta['IPF_version'] < 2.34:
        scalingFactor = knoise * adn
    else:
        scalingFactor = knoise * adn * adn
else:
    scalingFactor = 1

# read noise vectors from corresponding annotation xml
noisefile = scene.getFileObj(scene.findfiles('noise-s1[ab]-[ie]w-grd-(?:hh|vv)')[0])
noisetree = ET.fromstring(noisefile.read())
noisefile.close()
noiseVectors = noisetree.findall('.//noiseVector')

# define boundaries of image subsets to be masked (4x the first lines/samples of the image boundaries)
subsets = [(0, 0, blocksize, scene.lines)]

# extract column indices of noise vectors
yi = np.array([int(x.find('line').text) for x in noiseVectors])

# create links to the tif files for a master co-polarization and all other polarizations as slaves
master = scene.findfiles('s1.*(?:vv|hh).*tiff')[0]
ras_master = gdal.Open(master, GA_Update)
ras_slaves = [gdal.Open(x, GA_Update) for x in scene.findfiles('s1.*tiff') if x != master]

outband_master = ras_master.GetRasterBand(1)
outband_slaves = [x.GetRasterBand(1) for x in ras_slaves]

# iterate over the four image subsets
for subset in subsets:
    print(subset)
    xmin, ymin, xmax, ymax = subset
    xdiff = xmax - xmin
    ydiff = ymax - ymin
    # linear interpolation of noise vectors to array
    noise_interp = np.empty((ydiff, xdiff), dtype=float)
    for i in range(0, len(noiseVectors)):
        if ymin <= yi[i] <= ymax:
            # extract row indices of noise vector
            xi = [int(x) for x in noiseVectors[i].find('pixel').text.split()]
            # extract noise values
            noise = [float(x) for x in noiseVectors[i].find('noiseLut').text.split()]
            # interpolate values along rows
            noise_interp[yi[i] - ymin, :] = np.interp(range(0, xdiff), xi, noise)
    for i in range(0, xdiff):
        yi_t = yi[(ymin <= yi) & (yi <= ymax)] - ymin
        # interpolate values along columns
        noise_interp[:, i] = np.interp(range(0, ydiff), yi_t, noise_interp[:, i][yi_t])
    
    # read subset of image to array and subtract interpolated noise (denoising)
    mat_master = outband_master.ReadAsArray(*[xmin, ymin, xdiff, ydiff])
    denoisedBlock = mat_master.astype(float) ** 2 - noise_interp * scalingFactor
    # mask out all pixels with a value below 0.5 in the denoised block or 30 in the original block
    denoisedBlock[(denoisedBlock < 0.5) | (mat_master < 30)] = 0
    denoisedBlock = np.sqrt(denoisedBlock)
    
    
    # helper functions for masking out negative values
    def helper1(x):
        return len(x) - np.argmax(x > 0)
    
    
    def helper2(x):
        return len(x) - np.argmax(x[::-1] > 0)

    border = np.apply_along_axis(helper1, 1, denoisedBlock)
    result = ls.reduce(border, plot=True, straighten=True)
