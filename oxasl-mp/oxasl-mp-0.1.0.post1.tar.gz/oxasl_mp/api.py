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

def decode_mp(wsp):
    """
    Run multiphase decoding on a full multiphase data set
    """
    if wsp.mp is None:
        wsp.sub("mp")

    wsp.log.write("\nPerforming multiphase decoding:     ")
    if wsp.asldata.is_var_repeats():
        raise ValueError("Multiphase ASL data with variable repeats not currently supported")
    nrepeats = wsp.asldata.rpts[0]

    # Make sure phase cycles are together in the data and data for each
    # PLD is in a block
    wsp.mp.asldata = wsp.asldata.reorder(out_order="lrt")

    # Prepare a data set to put each decoded PLD into
    diffdata = np.zeros(list(wsp.asldata.data.shape)[:3] + [wsp.asldata.ntis])

    options = {
        "method" : "vb",
        "noise" : "white",
        "model" : "asl_multiphase",
        "data" : wsp.asldata,
        "nph" : wsp.asldata.nphases,
        "ntis" : wsp.asldata.ntis,
        "repeats" : nrepeats,
        "save-mean" : True,
        "save-model-fit" : True,
        "max-iterations": 30,
    }

    # Spatial mode
    if wsp.mp_spatial:
        options.update({
            "method" : "spatialvb",
            "param-spatial-priors" : "MN+",
            #"convergence" : "maxits",
            #"max-iterations": 30,
        })

    # Additional user-specified multiphase fitting options override the above
    options.update(wsp.ifnone("mp_options", {}))

    # Run Fabber using multiphase model
    result = fabber(options, output=LOAD, progress_log=wsp.log, log=wsp.fsllog)
    wsp.log.write("\n")

    # Write out full multiphase fitting output
    for key, value in result.items():
        setattr(wsp.mp, key, value)

    # Write Fabber log as text file
    if result["logfile"] is not None and wsp.mp.savedir is not None:
        wsp.mp.set_item("logfile", result["logfile"], save_fn=str)

    if wsp.asldata.ntis == 1:
        diffdata[..., 0] = result["mean_mag"].data
    else:
        for idx in range(wsp.asldata.ntis):
            diffdata[..., idx] = result["mean_mag%i" % (idx+1)].data

    # Set the full multiphase-decoded differenced data output on the workspace
    wsp.mp.asldata_decoded = wsp.mp.asldata.derived(diffdata, iaf='diff', order='rt', rpts=1)
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
        OptionCategory.__init__(self, "oxasl_mp", **kwargs)

    def groups(self, parser):
        groups = []
        group = IgnorableOptionGroup(parser, "Multiphase Options", ignore=self.ignore)
        group.add_option("--mp-spatial", help="Enable spatial smoothing on multiphase fitting step", action="store_true", default=False)
        group.add_option("--mp-options", help="File containing additional options for multiphase fitting step", type="optfile")
        groups.append(group)
        return groups
