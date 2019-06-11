# conftest.py
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0411,C0413,E0012,E0611,E1101,E1103,F0401,W0212

# Standard library imports
import os
import pickle
import sys
import warnings

if sys.hexversion < 0x03000000:
    import __builtin__
else:
    import builtins as __builtin__
# PyPI imports
with warnings.catch_warnings():
    from _pytest.warning_types import PytestWarning

    warnings.filterwarnings("ignore", category=PytestWarning)
    import pytest
import pexdoc.exh


###
# Functions
###
def log(line, append=True):
    """Debug xdist."""
    with open(
        os.path.join(os.environ["HOME"], "xdist-debug.log"), "a" if append else "w"
    ) as fobj:
        fobj.write("{0}\n".format(line))


def pytest_configure(config):
    """Configure Pytest, both slave and master."""
    if not hasattr(config, "slaveinput"):  # Master configuration
        pass


def pytest_configure_node(node):
    """Configure node."""
    # pylint: disable=W0613
    if hasattr(__builtin__, "_EXDOC_EXCLUDE"):
        node.slaveinput["exclude"] = pickle.dumps(__builtin__._EXDOC_EXCLUDE)
    if hasattr(__builtin__, "_EXDOC_FULL_CNAME"):
        node.slaveinput["full_cname"] = pickle.dumps(__builtin__._EXDOC_FULL_CNAME)
    if hasattr(__builtin__, "_EXDOC_CALLABLES_FNAME"):
        node.slaveinput["callables_fname"] = pickle.dumps(
            __builtin__._EXDOC_CALLABLES_FNAME
        )


def pytest_testnodedown(node, error):
    """Integrate received exception handler form sub-process into main one."""
    if error:
        raise RuntimeError("Slave node reported an error")
    if "msg" in node.slaveoutput:
        obj = pickle.loads(node.slaveoutput["msg"])
        if not hasattr(__builtin__, "_EXH_LIST"):
            setattr(__builtin__, "_EXH_LIST", [obj])
        else:
            getattr(__builtin__, "_EXH_LIST").append(obj)


@pytest.fixture(autouse=True, scope="module")
def exhobj(request):
    """
    Get global exception handler in sub-process and send it after tests done.

    This fixture runs in the slave session with NO connection to master except
    through slaveinput/slaveoutput
    """
    xdist_run = hasattr(request.config, "slaveinput")

    def fin():
        """Tear down function."""
        if hasattr(request.config, "slaveoutput") and hasattr(
            request.module.__builtin__, "_EXH"
        ):
            request.config.slaveoutput["msg"] = pickle.dumps(
                getattr(request.module.__builtin__, "_EXH")
            )

    request.addfinalizer(fin)
    if xdist_run:  # sub-process
        modname = "__builtin__" if sys.hexversion < 0x03000000 else "builtins"
        if not hasattr(request.module, "__builtin__"):
            setattr(request.module, "__builtin__", __import__(modname))
        exclude = (
            pickle.loads(request.config.slaveinput["exclude"])
            if "exclude" in request.config.slaveinput
            else None
        )
        full_cname = (
            pickle.loads(request.config.slaveinput["full_cname"])
            if "full_cname" in request.config.slaveinput
            else False
        )
        callables_fname = (
            pickle.loads(request.config.slaveinput["callables_fname"])
            if "callables_fname" in request.config.slaveinput
            else None
        )

        setattr(
            request.module.__builtin__,
            "_EXH",
            pexdoc.exh.ExHandle(
                full_cname=full_cname, exclude=exclude, callables_fname=callables_fname
            ),
        )
