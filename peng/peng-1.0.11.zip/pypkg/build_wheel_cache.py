#!/usr/bin/env python
# build_wheel_cache.py
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

# Standard library imports
from __future__ import print_function
import os
import subprocess
import sys


###
# Functions
###
# This is a sub-set of the .misc.pcolor function, repeated here because
# this script may be run right after cloning and the module may not be in
# the Python search path
def _os_cmd(cmd):
    """Execute shell command and display standard output."""
    pobj = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, _ = pobj.communicate()
    print(stdout)


def _pcolor(text, color, indent=0):
    """Colorized print to standard output."""
    esc_dict = {
        "black": 30,
        "red": 31,
        "green": 32,
        "yellow": 33,
        "blue": 34,
        "magenta": 35,
        "cyan": 36,
        "white": 37,
        "none": -1,
    }
    if esc_dict[color] != -1:
        return "\033[{color_code}m{indent}{text}\033[0m".format(
            color_code=esc_dict[color], indent=" " * indent, text=text
        )
    return "{indent}{text}".format(indent=" " * indent, text=text)


def _pip_install(pyver, pkg_name):
    """Install package via pip."""
    _os_cmd(
        ["pip{0}".format(pyver), "install", "--upgrade", "--force-reinstall", pkg_name]
    )


def which(name):
    """Search PATH for executable files with the given name."""
    # Inspired by https://twistedmatrix.com/trac/browser/tags/releases/
    # twisted-8.2.0/twisted/python/procutils.py
    # pylint: disable=W0141
    result = []
    path = os.environ.get("PATH", None)
    if path is None:
        return []
    for pdir in os.environ.get("PATH", "").split(os.pathsep):
        fname = os.path.join(pdir, name)
        if os.path.isfile(fname) and os.access(fname, os.X_OK):
            result.append(fname)
    return result[0] if result else None


def load_requirements(pkg_dir, pyver):
    """Get package names from requirements.txt file."""
    pyver = pyver.replace(".", "")
    reqs_dir = os.path.join(pkg_dir, "requirements")
    reqs_files = [
        "main_py{0}.pip".format(pyver),
        "tests_py{0}.pip".format(pyver),
        "docs.pip",
    ]
    ret = []
    for rfile in [os.path.join(reqs_dir, item) for item in reqs_files]:
        with open(os.path.join(reqs_dir, rfile), "r") as fobj:
            lines = [item.strip() for item in fobj.readlines() if item.strip()]
        ret.extend(lines)
    return ret


def build_wheel_cache(pyvers):
    """Build pip wheel cache."""
    pkg_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    pyvers = ["2.7", "3.5", "3.6"] if not pyvers else pyvers
    old_python_path = os.environ["PYTHONPATH"]
    template = "Building {0} wheel cache for Python {1}"
    for pyver in pyvers:
        pycmd = which("python{0}".format(pyver))
        if not pycmd:
            print("Python {0} not found".format(pyver))
            continue
        pipcmd = which("pip{0}".format(pyver))
        if not pipcmd:
            print("pip {0} not found".format(pyver))
            continue
        os.environ["PYTHONPATH"] = ""
        lines = load_requirements(pkg_dir, pyver)
        for line in lines:
            if "numpy" in line:
                numpy_line = line
                break
        else:
            raise RuntimeError("Numpy dependency could not be found")
        for line in lines:
            print(_pcolor(template.format(line, pyver), "cyan"))
            if "scipy" in line:
                # Install numpy before scipy otherwise pip throws an exception
                _pip_install(pyver, numpy_line.strip())
            _os_cmd(["pip{0}".format(pyver), "wheel", line])
        os.environ["PYTHONPATH"] = old_python_path


if __name__ == "__main__":
    build_wheel_cache(sys.argv[1:])
