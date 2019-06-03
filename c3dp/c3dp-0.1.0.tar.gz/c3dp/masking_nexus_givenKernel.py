from mantid.simpleapi import *
from matplotlib import pyplot as plt
import sys

thisdir = os.path.abspath(os.path.dirname(__file__))
if thisdir not in sys.path:
    sys.path.insert(0, thisdir)


def masking(path, Masked_detector_path, saved_file_path):
    nxs=Load(path)
    masked_detector=Load(Masked_detector_path)
    MaskDetectors(nxs, MaskedWorkspace=masked_detector)
    SaveNexus(nxs, saved_file_path)












