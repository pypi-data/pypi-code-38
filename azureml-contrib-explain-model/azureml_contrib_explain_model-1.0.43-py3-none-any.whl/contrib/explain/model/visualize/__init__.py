# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Module for Explanation Dashboard widget."""

from .ExplanationDashboard import ExplanationDashboard

__all__ = ['ExplanationDashboard']


def _jupyter_nbextension_paths():
    return [{
        'section': 'notebook',
        'src': 'static',
        'dest': 'microsoft-mli-widget',
        'require': 'microsoft-mli-widget/extension'
    }]
