# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
from distutils.version import LooseVersion

import mne

MNE_EPOCHS = mne.BaseEpochs
MNE_RAW = mne.io.BaseRaw
MNE_EVOKED = mne.Evoked
MNE_LABEL = (mne.Label, mne.label.BiHemiLabel)

# VolVectorSourceEstimate added for 0.18
if LooseVersion(mne.__version__) >= LooseVersion('0.18'):
    MNE_VOLUME_STC = (mne.VolSourceEstimate, mne.VolVectorSourceEstimate)
else:
    MNE_VOLUME_STC = mne.VolSourceEstimate
