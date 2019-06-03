from mantid.simpleapi import *
from matplotlib import pyplot as plt
import sys

thisdir = os.path.abspath(os.path.dirname(__file__))
if thisdir not in sys.path:
    sys.path.insert(0, thisdir)


def detector_position_for_reduction(path, conf, SNAP_definition_file, saved_file_path):
    sim=Load(path)

    AddSampleLog(sim, LogName='det_arc1', LogText= '{}'.format(conf.mon1), LogType='Number Series', NumberType='Double')
    AddSampleLog(sim, LogName='det_arc2', LogText= '{}'.format(conf.mon2), LogType='Number Series', NumberType='Double')
    LoadInstrument(sim, Filename=SNAP_definition_file, RewriteSpectraMap='True')
    SaveNexus(sim, saved_file_path)



