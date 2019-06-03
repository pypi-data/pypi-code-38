import unittest
import os, sys, glob
thisdir = os.path.dirname(__file__)
libpath = os.path.join(thisdir, '../c3dp')
if not libpath in sys.path:
    sys.path.insert(0, libpath)

import convert2nxs as cx
import rotate_detector_for_reduction_mantid as rot
import conf

sample='collimator_plastic_temperature'
number_of_neutrons='10000000.0'

datadir = os.path.join(thisdir, '../outputSim/{}_{}' .format(sample,number_of_neutrons)) #the out detector files from simulation
name=sample #the name of the result want to be saved
template=os.path.join(thisdir, '../mantid/template.nxs')
SNAP_definition_file=os.path.join(thisdir, '../mantid/SNAP_virtual_Definition.xml')
saved_file_name=os.path.abspath(os.path.join(thisdir, '../mantid/{}.nxs'.format(name)))


def test_conver2nxs():

    cx.create_nexus(datadir,saved_file_name,template )

    rot. detector_position_for_reduction(saved_file_name, conf, SNAP_definition_file, saved_file_name)


if __name__ == '__main__':
    test_conver2nxs()

