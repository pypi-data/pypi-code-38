from pyroSAR import identify
from pyroSAR.snap.auxil import split, groupbyWorkers
from pyroSAR.snap.util import geocode

filename = '/home/truc_jh/Desktop/S1_ARD/data/S1A_IW_GRDH_1SDV_20180101T170648_20180101T170713_019964_021FFD_DA78.zip'
# filename = '/home/truc_jh/Desktop/S1_ARD/data/S1A_IW_GRDH_1SDV_20180826T053453_20180826T053518_023413_028C38_716B.zip'

outdir = '/home/truc_jh/Desktop/S1_ARD/data/SNAP/stack'

scene = identify(filename)

wf = geocode(scene, outdir, test=False, returnWF=True, polarizations='VV', groupsize=1)

# print(wf)
#
# groups = groupbyWorkers(wf, 100)
#
# wf2 = split(wf, groups)
#
# print(wf2)
