from setuptools import setup, find_packages
from setuptools.extension import Extension
import re
err_string = None
try:
    from Cython.Build import cythonize
except:
    err_string = "Error - mdio requires cython is pre-installed."
try:
    import numpy
except:
    if err_string is None:
        err_string = "Error - mdio requires numpy is pre-installed."
    else:
        err_string = "Error - mdio requires numpy and cython are pre-installed."

if err_string is not None:
    raise ImportError(err_string)

VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
VERSIONFILE = "mdio/_version.py"
verstrline = open(VERSIONFILE, "rt").read()
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RunTimeError("Unable to find version string in {}.".format(VERSIONFILE))

with open("README.md", "r") as f:
    long_description = f.read()

extensions = [Extension(
        name="mdio.xtcutils",
        sources=["mdio/xtcutils.pyx"],
        include_dirs=[".", numpy.get_include()],
        ),
        Extension(
        name="mdio.fastrmsd",
        sources=["mdio/fastrmsd.pyx"],
        include_dirs=[".", numpy.get_include()],
        )
    ]
setup(
    name = 'mdio',
    version = verstr,
    author = 'Charlie Laughton',
    author_email = 'charles.laughton@nottingham.ac.uk',
    description = 'Basic I/O for MD trajectory files',
    long_description = long_description,
    long_description_content_type='text/markdown',
    url = 'https://bitbucket.org/claughton/mdio',
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Development Status :: 3 - Alpha",
    ],
    packages = find_packages(),
    ext_modules = cythonize(extensions),
    install_requires = [
        'six',
        'numpy',
        'cython',
        'netCDF4',
        'scipy',
        'pyparsing',
        'mendeleev',
    ],
)
