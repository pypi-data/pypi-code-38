#!/usr/bin/env python
# vim: set fileencoding=utf-8 :


from ._library import remove_highlights
from .galbally_iqm_features import compute_quality_features
from .msu_iqa_features import compute_msu_iqa_features



def get_config():
    """
    Returns a string containing the configuration information.

    """
    import bob.extension
    return bob.extension.get_config(__name__)


# gets sphinx autodoc done right - don't remove it
__all__ = [_ for _ in dir() if not _.startswith('_')]
