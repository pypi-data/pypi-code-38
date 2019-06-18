"""
OXASL plugin for processing multiphase ASL data

Copyright (c) 2019 Univerisity of Oxford
"""
import numpy as np

from fsl.wrappers import LOAD

from oxasl import basil
from oxasl.options import OptionCategory, IgnorableOptionGroup
from oxasl.reporting import Report
from oxasl.wrappers import fabber

from ._version import __version__

def _decode_mp_pld(wsp):
    """
    Run multiphase decoding on a single PLD
    """
    options = {
        "method" : "vb",
        "noise" : "white",
        "model" : "asl_multiphase",
        "data" : wsp.asldata,
        "nph" : wsp.asldata.nphases,
        "save-mean" : True,
        "save-model-fit" : True,
    }

    # Run Fabber using multiphase model
    result = fabber(options, output=LOAD, progress_log=wsp.log, log=wsp.fsllog)
    wsp.log.write("\n")

    for key, value in result.items():
        setattr(wsp, key, value)

    # Write log as text file
    if wsp.logfile is not None and wsp.savedir is not None:
        wsp.set_item("logfile", wsp.logfile, save_fn=str)

def decode_mp(wsp):
    """
    Run multiphase decoding on a full multiphase data set
    """
    if wsp.mp is None:
        wsp.sub("mp")

    wsp.log.write("\nPerforming multiphase decoding\n")

    # Make sure phase cycles are together in the data
    wsp.mp.asldata = wsp.asldata.reorder(out_order="lrt")

    # Prepare a data set to put each decoded PLD into
    diffdata = np.zeros(list(wsp.asldata.data.shape)[:3] + [wsp.asldata.ntis])

    # Do multiphase modelling on each TI/PLD saving the magnitude output
    # in the diffdata
    for idx in range(wsp.asldata.ntis):
        wsp.log.write("\n - Fitting PLD %i: " % (idx+1))
        wsp_pld = wsp.mp.sub("pld%i" % (idx+1))
        wsp_pld.asldata = wsp.mp.asldata.single_ti(idx)
        _decode_mp_pld(wsp_pld)
        diffdata[..., idx] = wsp_pld.mean_mag.data

    # Set the full multiphase-decoded differenced data output on the workspace
    wsp.mp.asldata_decoded = wsp.mp.asldata.derived(diffdata, iaf='diff', order='rt')
    wsp.log.write("\nDONE multiphase decoding\n")

def model_mp(wsp):
    """
    Do modelling on multiphase ASL data

    :param wsp: Workspace object

    Required workspace attributes
    -----------------------------

      - ``asldata`` - ASLImage containing multiphase data

    Optional workspace attributes
    -----------------------------

    See ``MultiphaseOptions`` for other options

    Workspace attributes updated
    ----------------------------

      - ``mp``         - Sub-workspace containing multiphase decoding output
      - ``basil``      - Sub-workspace containing modelling of decoded output
      - ``output``     - Sub workspace containing native/structural/standard space
                         parameter maps
    """
    from oxasl import oxford_asl

    # Do multiphase decoding
    decode_mp(wsp)

    # Do conventional ASL modelling
    wsp.sub("basil")
    wsp.basil.asldata = wsp.mp.asldata_decoded
    basil.basil(wsp.basil, output_wsp=wsp.basil)

    # Write output
    wsp.sub("output")
    oxford_asl.output_native(wsp.output, wsp.basil)

    # Re-do registration using PWI map.
    oxford_asl.redo_reg(wsp, wsp.output.native.perfusion)

    # Write output in transformed spaces
    oxford_asl.output_trans(wsp.output)

    wsp.log.write("\nDONE processing\n")

class MultiphaseOptions(OptionCategory):
    """
    OptionCategory which contains options for preprocessing multiphase ASL data
    """
    def __init__(self, **kwargs):
        OptionCategory.__init__(self, "oxasl_ve", **kwargs)

    def groups(self, parser):
        ret = []
        g = IgnorableOptionGroup(parser, "Multiphase Options")
        ret.append(g)
        return ret
