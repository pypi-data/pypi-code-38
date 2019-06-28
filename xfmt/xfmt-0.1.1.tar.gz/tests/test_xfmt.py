"""
This is for pytest to find and stop being upset not finding any tests.

>>> 'Happy?'[:-1]
'Happy'
"""
# pylint: disable=C0111,W0621
import os

import pytest  # type: ignore
from xfmt import json_fmt, misc

_BAD_SAMPELS = [
    "mumbo_jumbo.json",
    "nested_directory/argle_bargle.json",
    "short_and_squat.py",
]
_GOOD_SAMPLES = ["spruce.json", "great_and_small.py"]
_OTHER_SAMPLES = ["nesbitt.sh"]
_SAMPLES_PATH = os.path.normpath(os.path.join(__file__, "..", "..", "samples"))


@pytest.fixture()
def formatters():
    yield misc.get_formatters()


def test_collect_finds_all_samples():
    # Sort to ignore order of paths
    # Use lists, instead of say sets, to pay attention to number of occurrences
    expected = sorted(_BAD_SAMPELS + _GOOD_SAMPLES + _OTHER_SAMPLES)
    actual = sorted(misc.collect(_SAMPLES_PATH))

    assert actual == expected


def test_get_formatters_finds_all_formatters(formatters):
    types = {type(f) for f in formatters}
    assert json_fmt.JsonFormatter in types


@pytest.mark.parametrize("relpath", _BAD_SAMPELS)
def test_check_fails_bad_samples(relpath, formatters):
    assert misc.check(os.path.join(_SAMPLES_PATH, relpath), formatters, False)


@pytest.mark.parametrize("relpath", _GOOD_SAMPLES)
def test_check_passes_good_samples(relpath, formatters):
    assert not misc.check(os.path.join(_SAMPLES_PATH, relpath), formatters, False)


@pytest.mark.parametrize("relpath", _OTHER_SAMPLES)
def test_check_raises_on_other_samples(relpath, formatters):
    with pytest.raises(LookupError):
        misc.check(os.path.join(_SAMPLES_PATH, relpath), formatters, False)
