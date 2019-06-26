import vcver
import os
import pytest
from vcver.version import _get_scm


def test_happy_case():
    """
    instead of setting up a git repo,
    just testing that vcver's own
    version string matches the
    expected format.
    """
    v = vcver.get_version()
    version, scm = v.split("+")

    try:
        # major / minor should be an int
        major, version_remainder = _get_leading_version_part(version)
        int(major)
        minor, version_remainder = _get_leading_version_part(version_remainder[0])
        int(minor)
        patch, version_remainder = _get_leading_version_part(version_remainder[0])
        int(patch)
        dev, version_remainder = _get_leading_version_part(version_remainder[0])
        # commitcount should be an int
        int(dev[3:])
        assert dev.startswith("dev")
    except Exception as ex:
        msg = "{0} Generated  Version: {1}".format(ex, version)
        raise Exception(msg)

    branch, change_id = scm.split(".")
    assert change_id.startswith("x")
    change_id = change_id[1:]
    # scm_change_id should be a git hash
    assert set(change_id) & set("abcdef1234567890") == set(change_id)


@pytest.mark.skip
def _get_leading_version_part(version):
    version_parts = version.split(".", 1)
    return version_parts[0], version_parts[1:]


def test_child_directory_detected_as_git_repo():
    """
    """
    assert _get_scm(None, os.path.join(os.curdir, "vcver")) is not None
