# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
"""Accessible tool for statistical analysis of MEG and EEG data.

For the full documentation see <http://eelbrain.readthedocs.io>.



  "The human brain is like an enormous fish. It's flat
   and slimy, and has gills through which it can see."
                                               - Dr. Quat



"""
# import this first for a chance to reverse mne's non-standard logging practice
from . import mne_fixes

from ._config import configure
from ._celltable import Celltable
from ._data_obj import (
    Datalist, Dataset, Var, Factor, Interaction, Model,
    NDVar, Case, Categorial, Scalar, Sensor, SourceSpace, VolumeSourceSpace,
    UTS, Space,
    choose, combine, align, align1, cellname, shuffled_index
)
from ._experiment import MneExperiment
from ._mne import (
    complete_source_space, labels_from_clusters, morph_source_space, xhemi,
)
from ._ndvar import (
    Butterworth, concatenate, convolve, correlation_coefficient,
    cross_correlation, cwt_morlet, dss,
    filter_data, find_intervals, find_peaks, frequency_response, label_operator,
    neighbor_correlation, psd_welch, rename_dim, resample, segment, set_parc,
    set_tmin,
)
from ._stats.testnd import NDTest, MultiEffectNDTest
from ._trf import boosting, BoostingResult, epoch_impulse_predictor
from ._utils import set_log_level
from ._utils.com import check_for_update

from . import datasets
from . import gui
from . import load
from . import plot
from . import save
from . import table
from . import test
from . import testnd

from .fmtxt import Report


__version__ = '0.30.7'
