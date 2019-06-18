
from pyroSAR.gamma import ISPPar, UTM

infile = '/geonfs01_vol1/01_EMS_SALDI_KNP_S1/01_S1_GRD/02_SALDI/xx_SRTM/03_SRTM_HGT_1_Mokala.par'

with ISPPar(infile) as par:
    print(par)

print(UTM(infile).zone)