from __future__ import print_function

import os
import sys

from setuptools import setup

VERSION = (1, 4, 1)  # no need to adapt version in other locations

AUTHOR = "Uwe Schmitt"
AUTHOR_EMAIL = "uwe.schmitt@id.ethz.ch"

DESCRIPTION = "pytest plugin for regression tests"

LICENSE = "https://opensource.org/licenses/MIT"

URL = "https://gitlab.com/uweschmitt/pytest-regtest"

LONG_DESCRIPTION = ""

if len(sys.argv) > 1 and "dist" in sys.argv[1] and "wheel" not in sys.argv[1]:

    HERE = os.path.dirname(os.path.abspath(__file__))
    LONG_DESCRIPTION = open(os.path.join(HERE, "README.md")).read()

if __name__ == "__main__":

    setup(
        version="%d.%d.%d" % VERSION,
        name="pytest-regtest",
        py_modules=["pytest_regtest"],
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        url=URL,
        license=LICENSE,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        long_description_content_type="text/markdown",
        # the following makes a plugin available to pytest
        entry_points={"pytest11": ["regtest = pytest_regtest"]},
        install_requires=["pytest>=4.1.0"],
    )
