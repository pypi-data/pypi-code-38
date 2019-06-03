import unittest

import os, sys, glob
thisdir = os.path.dirname(__file__)
libpath = os.path.join(thisdir, '../c3dp')
if not libpath in sys.path:
    sys.path.insert(0, libpath)

import masking_nexus_givenKernel as mask

sample='collimator_plastic_temperature.nxs'
masked='clampcell_Si_1e11_mostCorrect_masked.nxs'
datadir = os.path.join(thisdir, '../mantid/{}' .format(sample)) #the mantid nexus file to be masked
masked_dir=os.path.join(thisdir, '../mantid/{}' .format(masked)) #the masked file to be used
name=sample #the name of the result want to be saved

saved_file_path=os.path.abspath(os.path.join(thisdir, '../mantid/{}_masked.nxs'.format(name)))

def test_masking():
    mask.masking(datadir,masked_dir, saved_file_path)

if __name__ == '__main__':
    test_masking()
