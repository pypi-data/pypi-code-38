"""
Do we have a version?
"""
from crosscap import __version__

def test_versionYes():
    """
    Is there a __version__?
    """
    assert __version__
