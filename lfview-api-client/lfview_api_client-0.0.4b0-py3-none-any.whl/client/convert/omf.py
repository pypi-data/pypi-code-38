"""Function for converting OMF files to Views"""
from __future__ import absolute_import

import steno3d
from .steno3d import steno3d_to_view


def omf_to_view(omf_file):
    """Translate an OMF project into a View

    Input:
    **omf_file** - Valid OMF file or instance of OMF project; see
    :class:`omf.base.Project`
    """
    steno3d_project = steno3d.Project.from_omf(omf_file)
    view = steno3d_to_view(steno3d_project)
    return view
