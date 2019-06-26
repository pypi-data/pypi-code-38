"Function to fix old data files from NYU/KIT system"
import numpy as np


def fix_ptb_eeg_events(raw):
    """Fix events from a vmrk file recorded with psychtoolbox/stim tracker

    Parameters
    ----------
    raw : RawBrainVision
        MNE-Python object with psychtoolbox events.
    """
    events = raw.get_brainvision_events()

    if not np.all(events[:, 1] == 1):
        err = ("Not KIT psychtoolbox input data (not all durations are 1)")
        raise ValueError(err)

    # invert trigger codes
    events[:, 2] = np.invert(events[:, 2].astype(np.uint8))

    # extend duration until next tigger start
    events[:-1, 1] = np.diff(events[:, 0])

    # remove 0 events
    idx = np.nonzero(events[:, 2])[0]
    events = events[idx]

    raw.set_brainvision_events(events)
