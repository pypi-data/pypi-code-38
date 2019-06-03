
import unittest

import os, sys
from mcvine import run_script
thisdir = os.path.dirname(__file__)

scattered = os.path.join(thisdir, '../beam/clampcellSi_scattered-neutrons_1e9_det-50_105_new')  # path to scattered neutrons from clamp cell and sample
sample = 'collimator_plastic_temperature' #name of the sample assembly
ncount = 1e7
nodes = int(20)
sourceTosample=0.0
detector_size=0.5
output_name_version=1e7

instr = os.path.join(thisdir, '../c3dp/myinstrument.py')
output=os.path.join(thisdir, '../outputSim/{}_{}' .format(sample,output_name_version))

def test_run_collimator():

    run_script.run_mpi(instr, output,
                       beam=scattered, ncount=ncount,
                       nodes=nodes,angleMon1=-50., angleMon2=105., sample=sample,
                       sourceTosample_x=sourceTosample, sourceTosample_y=sourceTosample,
                       sourceTosample_z=sourceTosample,
                       detector_size=detector_size ,overwrite_datafiles=True)


if __name__ == '__main__':
    test_run_collimator()

