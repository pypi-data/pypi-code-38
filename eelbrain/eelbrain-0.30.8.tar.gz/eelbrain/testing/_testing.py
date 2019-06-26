# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>
"Utilities for testing"
from contextlib import ContextDecorator, contextmanager
from distutils.version import LooseVersion
from functools import reduce, wraps
from importlib import import_module
from importlib.util import spec_from_file_location, module_from_spec
import os
from operator import mul
from pathlib import Path
import shutil
import tempfile

from nose.plugins.skip import SkipTest
import numpy as np
from numpy.testing import assert_array_equal

import eelbrain._wxgui
from .._data_obj import Dataset, NDVar, Var, Factor, isdatalist, isdatacontainer, isuv


class TempDir(str):
    "After MNE-Python mne.utils"
    def __new__(cls):
        return str.__new__(cls, tempfile.mkdtemp())

    def __del__(self):
        shutil.rmtree(self, ignore_errors=True)


def assert_dataset_equal(ds1, ds2, decimal=None):
    """
    Raise an assertion if two Datasets are not equal up to desired precision.

    Parameters
    ----------
    ds1, ds2 : Dataset
        Datasets to compare.
    decimal : None | int
        Desired precision (default is exact match).
    """
    assert ds1.keys() == ds2.keys()
    for k in ds1.keys():
        assert_dataobj_equal(ds1[k], ds2[k], decimal=decimal)
    assert ds1.info.keys() == ds2.info.keys()


def assert_dataobj_equal(d1, d2, decimal=None, name=True):
    """Assert that two data-objects are equal up to desired precision.

    Parameters
    ----------
    d1, d2 : data-objects
        Data-objects to compare.
    decimal : None | int
        Desired precision (default is exact match).
    name : bool
        Assert that ``d1.name == d2.name``.
    """
    if not isdatacontainer(d1):
        raise TypeError(f"d1 is not a data-object but {d1!r}")
    elif not isdatacontainer(d2):
        raise TypeError(f"d2 is not a data-object but {d2!r}")
    else:
        assert type(d1) == type(d2)
    if name:
        assert d1.name == d2.name
    assert len(d1) == len(d2)
    if isuv(d1):
        if isinstance(d1, Var):
            is_equal = np.isclose(d1.x, d2.x, equal_nan=True, rtol=0, atol=10**-decimal if decimal else 0)
        else:
            is_equal = d1 == d2
        if not np.all(is_equal):
            ds = Dataset()
            ds['value'] = d1
            ds['target'] = d2
            ds['unequal'] = Factor(is_equal, labels={True: '', False: 'x'})
            if isinstance(d1, Var):
                ds['difference'] = d1 - d2
            raise AssertionError(f'Two {d1.__class__.__name__}s named {d1.name!r} have unequal values:\n\n{ds}')
    elif isinstance(d1, NDVar):
        assert d1.dims == d2.dims
        if decimal:
            is_different = np.max(np.abs(d1.x - d2.x)) >= 10**-decimal
        else:
            is_different = np.any(d1.x != d2.x)

        if is_different:
            n = reduce(mul, d1.x.shape)
            n_different = (d1.x != d2.x).sum()
            mean_diff = np.abs(d1.x - d2.x).sum() / n_different
            raise AssertionError(f"NDVars names {d1.name!r} have unequal values. Difference in {n_different} of {n} values, average difference={mean_diff}.")
    elif isdatalist(d1):
        assert all(item1 == item2 for item1, item2 in zip(d1, d2))


def assert_source_space_equal(src1, src2):
    """Assert that two SourceSpace objects are identical

    Parameters
    ----------
    src1, src2 : SourceSpace objects
        SourceSpace objects to compare.
    """
    assert_array_equal(src1.vertices[0], src2.vertices[0])
    assert_array_equal(src1.vertices[1], src2.vertices[1])
    assert src1.subject == src2.subject
    assert src1.src == src2.src
    assert src1.subjects_dir == src2.subjects_dir


class GUITestContext(ContextDecorator):
    modules = (
        eelbrain._wxgui.select_epochs,
        eelbrain._wxgui.select_components,
        eelbrain._wxgui.history,
    )

    def __init__(self):
        self._i = 0

    def __enter__(self):
        self._i += 1
        if self._i == 1:
            for mod in self.modules:
                mod.TEST_MODE = True

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._i -= 1
        if self._i == 0:
            for mod in self.modules:
                mod.TEST_MODE = False


gui_test = GUITestContext()


@contextmanager
def working_directory(wd):
    "Context for temporarily changing the working directory"
    cwd = os.getcwd()
    os.chdir(wd)
    try:
        yield
    finally:
        os.chdir(cwd)


def import_attr(path, attr):
    spec = spec_from_file_location('module', path)
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    return getattr(mod, attr)


def requires_mne_sample_data(function):
    import mne

    if mne.datasets.sample.data_path(download=False):
        @wraps(function)
        def decorator(*args, **kwargs):
            return function(*args, **kwargs)
    else:
        @wraps(function)
        def decorator(*args, **kwargs):
            raise SkipTest('Skipped %s, requires mne sample data' % function.__name__)
    return decorator


def requires_pyarrow(function):
    "Sometimes broken under env-dev on Unix"
    @wraps(function)
    def decorator(*args, **kwargs):
        try:
            import pyarrow
        except ImportError:
            raise SkipTest(f'Skipped {function.__name__} because of pyarrow import error')
        else:
            return function(*args, **kwargs)
    return decorator


def requires_r_ez(function):
    from .._utils.r_bridge import r, r_warning_filter

    with r_warning_filter:
        success = r('require(ez)')[0]

    if success:
        @wraps(function)
        def decorator(*args, **kwargs):
            return function(*args, **kwargs)
    else:
        @wraps(function)
        def decorator(*args, **kwargs):
            raise SkipTest(f'Skipped {function.__name__}, requires r-ez')
    return decorator


def skip_on_windows(function):
    @wraps(function)
    def decorator(*args, **kwargs):
        if os.name == 'nt':
            raise SkipTest(f'Skipped {function.__name__} on Windows')
        else:
            return function(*args, **kwargs)
    return decorator


def file_path(name):
    "Path to test data file in the test_data directory"
    path = Path(__file__).parents[2] / 'test_data' / name
    if path.exists():
        return path
    else:
        raise IOError("Testing file does not exist. Test can only be executed from source repository.")


def path(string):
    "OS-independent path check"
    return str(Path(string))
