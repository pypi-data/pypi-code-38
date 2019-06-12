#!/usr/bin/env python
"""
retrieve parameters from HiST .DMCdata experiment .xml files
"""
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Any


def xmlparam(fn: Path) -> Dict[str, Any]:
    """
    reads necessary camera parameters into dict

    * kinetic rate (1/frame rate) seconds
    * resolution pixels
    * binning pixels


    This is probably not the "correct" way to do this, but it is good enough for our purposes.

    Parameters
    ----------

    fn : pathlib.Path
        filename of XML file corresponding to .DMCdata file

    Returns
    -------

    params : dict
        camera parameters of interest
    """
    tree = ET.parse(fn)  # type: ignore

    root = tree.getroot()

    children = root.getchildren()

    data = children[1]

    params: Dict[str, Any] = {}

    diter = data.iter()
    for el in diter:
        txt = el.text
        if txt == 'Binning (H x V)':
            txt = next(diter).text
            params['binning'] = int(txt)
        elif txt == 'ROI H Pixels':
            txt = next(diter).text
            params['horizpixels'] = int(txt)
        elif txt == 'ROI V Pixels':
            txt = next(diter).text
            params['vertpixels'] = int(txt)
        elif txt == 'Freq':
            txt = next(diter).text
            params['pulsefreq'] = float(txt)
            params['kineticrate'] = 1 / params['pulsefreq']

    return params
