# touchstone.py
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,C0411,E1101,R0205,R0903,R1719,W0611,W0702

# Standard library imports
import itertools
import cmath
import copy
import os
import platform
import random
import uuid
import warnings

# PyPI imports
import numpy as np

with warnings.catch_warnings():
    from _pytest.warning_types import PytestWarning

    warnings.filterwarnings("ignore", category=PytestWarning)
    import pytest
from pmisc import AE, AI

# Intra-package imports
import peng


###
# Global variables
###
FP_ATOL = 1e-8
FP_RTOL = 1e-8


###
# Helper function
###
mfname = lambda nports: "file_{0}.s{1}p".format(uuid.uuid4(), nports)


def all_options():
    """Generate all possible option lines."""
    units_opts = ["", "GHz", "MHz", "KHz", "Hz"]
    type_opts = ["", "S", "Y", "Z", "H", "G"]
    format_opts = ["", "DB", "MA", "RI"]
    z0_opts = ["", "R", "R 75"]
    return itertools.product(units_opts, type_opts, format_opts, z0_opts)


def comp_touchstone_str_data(fname, ref):
    """Compare written Touchstone data."""
    with open(fname, "r") as fobj:
        lines = "".join(fobj.readlines())
    assert lines == ref


def ref_touchstone_data(nports=5, points=3):
    """Create reference data for write_touchstone function."""
    options = dict(units="Hz", ptype="Y", pformat="RI", z0=100.0)
    nums_per_freq = 2 * (nports ** 2)
    rdata = np.arange(1, 1 + (points * nums_per_freq))
    cdata = rdata[::2] + 1j * rdata[1::2]
    data = dict(
        points=points,
        freq=np.arange(1, points + 1),
        pars=np.resize(cdata, (points, nports, nports)),
    )
    ndata = dict(
        points=points,
        freq=np.arange(1, points + 1),
        nf=np.array([3.5, 6.7, 9.1]),
        rc=np.array([1 + 1j, 2 + 2j, 3 + 3j]),
        res=np.array([50.0, 75.0, 25.0]),
    )
    return nports, options, data, ndata


def roundtrip_touchstone(nports, options, data, noise=None):
    """Check write_touchstone function by saving data and then reading it back."""
    with TmpFile(nports) as fname:
        peng.write_touchstone(fname, options, data, noise, frac_length=10, exp_length=2)
        idict = peng.read_touchstone(fname)
    assert idict["nports"] == nports
    assert idict["opts"] == options
    idata = idict["data"]
    npoints = data["freq"].size
    assert npoints == idata["points"]
    rsdata = np.resize(np.copy(data["pars"]), (npoints, nports, nports))
    assert np.allclose(idata["freq"], data["freq"], FP_RTOL, FP_ATOL)
    assert np.allclose(idata["pars"], rsdata, FP_RTOL, FP_ATOL)
    idata = idict["noise"]
    if idata:
        assert idata["freq"].size == noise["points"]
        assert np.allclose(idata["freq"], noise["freq"], FP_RTOL, FP_ATOL)
        assert np.allclose(idata["nf"], noise["nf"], FP_RTOL, FP_ATOL)
        assert np.allclose(idata["rc"], noise["rc"], FP_RTOL, FP_ATOL)
        assert np.allclose(idata["res"], noise["res"], FP_RTOL, FP_ATOL)


def write_file(fobj, opts=None, data=None, eopts=None):
    """Write a sample Touchstone file."""
    lines = []
    lines.append("! Sample file")
    if opts:
        lines.append("# " + " ".join(opts))
    if eopts:
        lines.append("# " + eopts)
    if not data:
        data = [[1, 1, 1]]
    for row in data:
        lines.append(" ".join([str(item) for item in row]))
    lines = [item + "\n" for item in lines]
    fobj.writelines(lines)


###
# Helper class
###
class TmpFile(object):
    """Create a temporary Touchstone file."""

    def __init__(self, nports):  # noqa: D107
        fname = mfname(nports)
        if platform.system().lower() == "windows":  # pragma: no cover
            fname = fname.replace(os.sep, "/")
        self._fname = fname

    def __enter__(self):  # noqa: D105
        return self._fname

    def __exit__(self, exc_type, exc_value, exc_tb):  # noqa: D105
        try:
            os.remove(self._fname)
        except:
            pass
        return False if exc_type is not None else True


class WriteTmpFile(object):
    """Create a temporary Touchstone file."""

    def __init__(self, fname, opts=None, data=None, eopts=None):  # noqa: D107
        if platform.system().lower() == "windows":  # pragma: no cover
            fname = fname.replace(os.sep, "/")
        self._fname = fname
        self._opts = opts or []
        self._data = data or [[1, 1, 1]]
        self._eopts = eopts

    def __enter__(self):  # noqa: D105
        with open(self._fname, "w") as fobj:
            write_file(fobj, self._opts, self._data, self._eopts)

    def __exit__(self, exc_type, exc_value, exc_tb):  # noqa: D105
        try:
            os.remove(self._fname)
        except:
            pass
        return False if exc_type is not None else True


###
# Test functions
###
def test_read_touchstone():
    """Test read_touchstone function behavior."""
    # pylint: disable=R0915
    obj = peng.read_touchstone
    # Test parsing of options line
    fname = mfname(4)
    for units, ptype, pformat, res in all_options():
        opts = [units, ptype, pformat, res]
        if all([not item for item in opts]):
            opts = [" "]
        else:
            random.shuffle(opts)
        with WriteTmpFile(fname, opts, [33 * [1]]):
            ret = obj(fname)
            assert ret["nports"] == 4
            assert ret["opts"] == dict(
                units=units or "GHz",
                ptype=ptype or "S",
                pformat=pformat or "MA",
                z0=75.0 if res == "R 75" else 50.0,
            )
    # Test multiple options line after first are ignored
    fname = mfname(8)
    with WriteTmpFile(fname, ["R 12", "KHz"], [129 * [1]], eopts="R 100 Z"):
        ret = obj(fname)
        assert ret["nports"] == 8
        assert ret["opts"] == dict(units="KHz", ptype="S", pformat="MA", z0=12)
    # Test file with one data point
    fname = mfname(1)
    data = [[1, 2, 3]]
    with WriteTmpFile(fname, ["RI"], data):
        ret = obj(fname)
    assert ret["nports"] == 1
    assert ret["opts"] == dict(units="GHz", ptype="S", pformat="RI", z0=50)
    assert (ret["data"]["freq"] == 1e9 * np.array([1.0])).all()
    assert (ret["data"]["pars"] == np.array([2 + 3j])).all()
    assert ret["noise"] == {}
    assert ret["data"]["points"] == 1
    # Test 1-port data parsing (and end of line comments)
    fname = mfname(1)
    data = [[1, 2, 3], [4, 5, "6 ! this is an end of line comment"], [7, 8, 9]]
    with WriteTmpFile(fname, ["RI"], data):
        ret = obj(fname)
    assert ret["nports"] == 1
    assert ret["opts"] == dict(units="GHz", ptype="S", pformat="RI", z0=50)
    assert (ret["data"]["freq"] == 1e9 * np.array([1.0, 4.0, 7.0])).all()
    ref = np.array([2 + 3j, 5 + 6j, 8 + 9j])
    assert (ret["data"]["pars"] == ref).all()
    assert ret["noise"] == {}
    assert ret["data"]["points"] == 3
    # Test 2-port data parsing
    # Real and imaginary format
    fname = mfname(2)
    data = [[1, 2, 3, 4, 5, 1.1, 7, 2.2, 3.3], [2, 8, 9, 10, 11, 12, 13, 14, 15]]
    with WriteTmpFile(fname, ["RI"], data):
        ret = obj(fname)
    assert ret["nports"] == 2
    assert ret["opts"] == dict(units="GHz", ptype="S", pformat="RI", z0=50)
    assert (ret["data"]["freq"] == 1e9 * np.array([1.0, 2.0])).all()
    ref = np.array(
        [
            [[2 + 3j, 1.1 + 7j], [4 + 5j, 2.2 + 3.3j]],
            [[8 + 9j, 12 + 13j], [10 + 11j, 14 + 15j]],
        ]
    )
    assert (ret["data"]["pars"] == ref).all()
    assert ret["data"]["points"] == 2
    assert ret["noise"] == {}
    # Magnitude and angle
    with WriteTmpFile(fname, ["MA"], data):
        ret = obj(fname)
    assert ret["nports"] == 2
    assert ret["opts"] == dict(units="GHz", ptype="S", pformat="MA", z0=50)
    assert (ret["data"]["freq"] == 1e9 * np.array([1.0, 2.0])).all()
    d2r = lambda x: 1j * np.deg2rad(x)
    ref = np.array(
        [
            [
                [2 * cmath.exp(d2r(3)), 1.1 * cmath.exp(d2r(7))],
                [4 * cmath.exp(d2r(5)), 2.2 * cmath.exp(d2r(3.3))],
            ],
            [
                [8 * cmath.exp(d2r(9)), 12 * cmath.exp(d2r(13))],
                [10 * cmath.exp(d2r(11)), 14 * cmath.exp(d2r(15))],
            ],
        ]
    )
    assert (ret["data"]["pars"] == ref).all()
    assert ret["data"]["points"] == 2
    assert ret["noise"] == {}
    # Decibel-angle
    with WriteTmpFile(fname, ["DB"], data):
        ret = obj(fname)
    assert ret["nports"] == 2
    assert ret["opts"] == dict(units="GHz", ptype="S", pformat="DB", z0=50)
    assert (ret["data"]["freq"] == 1e9 * np.array([1.0, 2.0])).all()
    idb = lambda x: 10 ** (x / 20.0)
    ref = np.array(
        [
            [
                [idb(2) * cmath.exp(d2r(3)), idb(1.1) * cmath.exp(d2r(7))],
                [idb(4) * cmath.exp(d2r(5)), idb(2.2) * cmath.exp(d2r(3.3))],
            ],
            [
                [idb(8) * cmath.exp(d2r(9)), idb(12) * cmath.exp(d2r(13))],
                [idb(10) * cmath.exp(d2r(11)), idb(14) * cmath.exp(d2r(15))],
            ],
        ]
    )
    assert (ret["data"]["pars"] == ref).all()
    assert ret["data"]["points"] == 2
    assert ret["noise"] == {}
    # Test 3-port data parsing
    # Real and imaginary format
    fname = mfname(3)
    data = [
        [1, 2, 3, 4, 5, 1.1, 7],
        [2.2, 3.3, 10, 20, 5.5, 6.6],
        [2, 1, 4, 3, 1.5, 1.6],
        [2, 9, 0, 5, 4, 1, 3.3],
        [20, 30, 40, 50, 32.5, 56.7],
        [60, 70, 80, 90.5, 45, 55],
    ]
    with WriteTmpFile(fname, ["RI"], data):
        ret = obj(fname)
    assert ret["nports"] == 3
    assert ret["opts"] == dict(units="GHz", ptype="S", pformat="RI", z0=50)
    assert (ret["data"]["freq"] == 1e9 * np.array([1.0, 2.0])).all()
    ref = np.array(
        [
            [
                [2 + 3j, 4 + 5j, 1.1 + 7j],
                [2.2 + 3.3j, 10 + 20j, 5.5 + 6.6j],
                [2 + 1j, 4 + 3j, 1.5 + 1.6j],
            ],
            [
                [9 + 0j, 5 + 4j, 1 + 3.3j],
                [20 + 30j, 40 + 50j, 32.5 + 56.7j],
                [60 + 70j, 80 + 90.5j, 45 + 55j],
            ],
        ]
    )
    assert (ret["data"]["pars"] == ref).all()
    assert ret["data"]["points"] == 2
    assert ret["noise"] == {}
    # Noise data
    # 1 point
    fname = mfname(2)
    data = [[1, 2, 3, 4, 5, 1.1, 7, 2.2, 3.3], [0.5, 1, 2, 3, 4]]
    with WriteTmpFile(fname, ["RI"], data):
        ret = obj(fname)
    assert ret["nports"] == 2
    assert ret["opts"] == dict(units="GHz", ptype="S", pformat="RI", z0=50)
    assert (ret["data"]["freq"] == 1e9 * np.array([1.0])).all()
    ref = np.array([[[2 + 3j, 1.1 + 7j], [4 + 5j, 2.2 + 3.3j]]])
    assert (ret["data"]["pars"] == ref).all()
    assert ret["data"]["points"] == 1
    assert (ret["noise"]["freq"] == 1e9 * np.array([0.5])).all()
    assert (ret["noise"]["nf"] == np.array([1])).all()
    assert (ret["noise"]["rc"] == np.array([2 * cmath.exp(3j)])).all()
    assert (ret["noise"]["res"] == np.array([4])).all()
    assert ret["noise"]["points"] == 1
    # Multiple points
    fname = mfname(2)
    data = [
        [1, 2, 3, 4, 5, 1.1, 7, 2.2, 3.3],
        [2, 8, 9, 10, 11, 12, 13, 14, 15],
        [3, 2, 2, 3, 3, 4, 4, 5, 5],
        [0.5, 1, 2, 3, 4],
        [1.5, 5, 6, 7, 8],
        [2.5, 9, 10, 11, 12],
        [3.5, 13.5, 14, 15.7, 16],
    ]
    with WriteTmpFile(fname, ["RI"], data):
        ret = obj(fname)
    assert ret["nports"] == 2
    assert ret["opts"] == dict(units="GHz", ptype="S", pformat="RI", z0=50)
    assert (ret["data"]["freq"] == 1e9 * np.array([1.0, 2.0, 3.0])).all()
    ref = np.array(
        [
            [[2 + 3j, 1.1 + 7j], [4 + 5j, 2.2 + 3.3j]],
            [[8 + 9j, 12 + 13j], [10 + 11j, 14 + 15j]],
            [[2 + 2j, 4 + 4j], [3 + 3j, 5 + 5j]],
        ]
    )
    assert (ret["data"]["pars"] == ref).all()
    assert ret["data"]["points"] == 3
    assert (ret["noise"]["freq"] == 1e9 * np.array([0.5, 1.5, 2.5, 3.5])).all()
    assert (ret["noise"]["nf"] == np.array([1, 5, 9, 13.5])).all()
    ref = np.array(
        [
            2 * cmath.exp(3j),
            6 * cmath.exp(7j),
            10 * cmath.exp(11j),
            14 * cmath.exp(15.7j),
        ]
    )
    assert (ret["noise"]["rc"] == ref).all()
    assert (ret["noise"]["res"] == np.array([4, 8, 12, 16])).all()
    assert ret["noise"]["points"] == 4


@pytest.mark.touchstone
def test_read_touchstone_exceptions():
    """Test read function exceptions."""
    obj = peng.read_touchstone
    msg = "File __not_a_file__ could not be found"
    AE(obj, OSError, msg, "__not_a_file__")
    msg = "File {0} does not have a valid extension"
    items = ["file.zzz", "file.s10a3p"]
    for item in items:
        with WriteTmpFile(item):
            AE(obj, RuntimeError, msg.format(item), item)
    msg = "First non-comment line is not the option line"
    fname = mfname(1)
    with WriteTmpFile(fname):
        AE(obj, RuntimeError, msg, fname)
    # Add an invalid option to options line
    for units, ptype, pformat, res in all_options():
        opts = [units, ptype, pformat, res, "noopt"]
        if all([not item for item in opts]):
            opts = [" "]
        else:
            random.shuffle(opts)
        with WriteTmpFile(fname, opts):
            AE(obj, RuntimeError, "Illegal option line", fname)
    # No data
    with WriteTmpFile(fname, ["MA"], [""]):
        AE(obj, RuntimeError, "File {0} has no data".format(fname), fname)
    # Invalid data line
    with WriteTmpFile(fname, ["MA"], [[1, 2, 3], [3.5, "a", 7]]):
        AE(obj, RuntimeError, "Illegal data in line 4", fname)
    # Frequency not increasing
    fname = mfname(1)
    with WriteTmpFile(fname, ["MA"], [[1, 2, 3], [2, 3, 4], [2, 5, 6]]):
        AE(obj, RuntimeError, "Frequency must increase", fname)
    # Noise data
    fname = mfname(2)
    data = [
        [1, 2, 3, 4, 5, 7, 8, 9, 10],
        [11, 12, 13, 14, 15, 16, 17, 18, 19],
        ["! Noise data"],
        [2, 11, 12, 13, 14],
        [1, 15, 16, 17, 18],
    ]
    with WriteTmpFile(fname, ["MA"], data):
        AE(obj, RuntimeError, "Noise frequency must increase", fname)
    fname = mfname(2)
    data = [
        [1, 2, 3, 4, 5, 7, 8, 9, 10],
        [11, 12, 13, 14, 15, 16, 17, 18, 19],
        ["! Noise data"],
        [2, 11, 12, 13, 14],
        [4, 15, 16, 17, 18, 19],
    ]
    with WriteTmpFile(fname, ["MA"], data):
        AE(obj, RuntimeError, "Malformed noise data", fname)


@pytest.mark.touchstone
def test_write_touchstone_exceptions():
    """Test write_touchstone function exceptions."""
    obj = peng.write_touchstone
    _, options, data, noise = ref_touchstone_data()
    AI(obj, "fname", 45, options, data)
    AI(obj, "options", "file.s2p", "a", data)
    AI(obj, "data", "file.s2p", options, "a")
    AI(obj, "noise", "file.s2p", options, data, "a")
    items = ["a", -1, 3.0]
    for item in items:
        AI(obj, "frac_length", "file.s5p", options, data, None, item)
    items = ["a", -1, 0, 2.1]
    for item in items:
        AI(obj, "exp_length", "file.s5p", options, data, None, 3, item)
    msg = "File sdata.ddd does not have a valid extension"
    AE(obj, RuntimeError, msg, "sdata.ddd", options, data)
    msg = "Noise data only supported in two-port files"
    AE(obj, RuntimeError, msg, "sdata.s4p", options, data, noise)
    msg = "Malformed data"
    data = dict(points=1, freq=np.array([1]), pars=np.array([1, 2, 3, 4]))
    AE(obj, RuntimeError, msg, "sdata.s1p", options, data)


def test_write_touchstone():
    """Test write_touchstone function behavior."""
    obj = peng.write_touchstone
    nports, options, data, _ = ref_touchstone_data(5, 1)
    ref = """# Hz Y RI R 100.0
1.0E+0 +1.0E+0 +2.0E+0 +3.0E+0 +4.0E+0 +5.0E+0 +6.0E+0 +7.0E+0 +8.0E+0
       +9.0E+0 +1.0E+1 +1.1E+1 +1.2E+1 +1.3E+1 +1.4E+1 +1.5E+1 +1.6E+1
       +1.7E+1 +1.8E+1 +1.9E+1 +2.0E+1 +2.1E+1 +2.2E+1 +2.3E+1 +2.4E+1
       +2.5E+1 +2.6E+1 +2.7E+1 +2.8E+1 +2.9E+1 +3.0E+1 +3.1E+1 +3.2E+1
       +3.3E+1 +3.4E+1 +3.5E+1 +3.6E+1 +3.7E+1 +3.8E+1 +3.9E+1 +4.0E+1
       +4.1E+1 +4.2E+1 +4.3E+1 +4.4E+1 +4.5E+1 +4.6E+1 +4.7E+1 +4.8E+1
       +4.9E+1 +5.0E+1
"""
    with TmpFile(nports) as fname:
        obj(fname, options, data, frac_length=1, exp_length=1)
        comp_touchstone_str_data(fname, ref)
    nports, options, data, _ = ref_touchstone_data(5, 2)
    ref = """# Hz Y RI R 100.0
1.00E+0 +1.00E+0 +2.00E+0 +3.00E+0 +4.00E+0 +5.00E+0 +6.00E+0 +7.00E+0 +8.00E+0
        +9.00E+0 +1.00E+1 +1.10E+1 +1.20E+1 +1.30E+1 +1.40E+1 +1.50E+1 +1.60E+1
        +1.70E+1 +1.80E+1 +1.90E+1 +2.00E+1 +2.10E+1 +2.20E+1 +2.30E+1 +2.40E+1
        +2.50E+1 +2.60E+1 +2.70E+1 +2.80E+1 +2.90E+1 +3.00E+1 +3.10E+1 +3.20E+1
        +3.30E+1 +3.40E+1 +3.50E+1 +3.60E+1 +3.70E+1 +3.80E+1 +3.90E+1 +4.00E+1
        +4.10E+1 +4.20E+1 +4.30E+1 +4.40E+1 +4.50E+1 +4.60E+1 +4.70E+1 +4.80E+1
        +4.90E+1 +5.00E+1
2.00E+0 +5.10E+1 +5.20E+1 +5.30E+1 +5.40E+1 +5.50E+1 +5.60E+1 +5.70E+1 +5.80E+1
        +5.90E+1 +6.00E+1 +6.10E+1 +6.20E+1 +6.30E+1 +6.40E+1 +6.50E+1 +6.60E+1
        +6.70E+1 +6.80E+1 +6.90E+1 +7.00E+1 +7.10E+1 +7.20E+1 +7.30E+1 +7.40E+1
        +7.50E+1 +7.60E+1 +7.70E+1 +7.80E+1 +7.90E+1 +8.00E+1 +8.10E+1 +8.20E+1
        +8.30E+1 +8.40E+1 +8.50E+1 +8.60E+1 +8.70E+1 +8.80E+1 +8.90E+1 +9.00E+1
        +9.10E+1 +9.20E+1 +9.30E+1 +9.40E+1 +9.50E+1 +9.60E+1 +9.70E+1 +9.80E+1
        +9.90E+1 +1.00E+2
"""
    with TmpFile(nports) as fname:
        obj(fname, options, data, frac_length=2, exp_length=1)
        comp_touchstone_str_data(fname, ref)
    #
    nports, options, data, _ = ref_touchstone_data(5, 10)
    options["pformat"] = "MA"
    roundtrip_touchstone(nports, options, data)
    options["pformat"] = "DB"
    # Check that data shape does not matter
    data["pars"] = np.resize(data["pars"], data["pars"].size)
    rdata = np.copy(data["pars"])
    roundtrip_touchstone(nports, options, data)
    # Test data is not mutated in call
    assert np.all(rdata == data["pars"])
    nports, options, data, _ = ref_touchstone_data(2, 10)
    roundtrip_touchstone(nports, options, data)
    nports, options, data, noise = ref_touchstone_data(2, 3)
    roundtrip_touchstone(nports, options, data, noise)
