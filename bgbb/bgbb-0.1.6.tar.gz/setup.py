import re
from setuptools import find_packages, setup


def read_version():
    "https://stackoverflow.com/a/7071358/386279"
    VERSIONFILE = "bgbb/_version.py"

    with open(VERSIONFILE, "rt") as fp:
        verstrline = fp.read()
    VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
    mo = re.search(VSRE, verstrline, re.M)
    if mo:
        verstr = mo.group(1)
    else:
        raise RuntimeError(
            "Unable to find version string in %s." % (VERSIONFILE,)
        )
    return verstr


verstr = read_version()

setup(
    name="bgbb",
    version=verstr,
    packages=find_packages(),
    install_requires=[
        "lifetimes==0.9",
        # See Readme for databricks library restrictions
        "numba>=0.34,<=0.38",
        "scipy",
        "pandas",
        "numpy",
        "pyarrow",
        "pyspark",
    ],
    license=["Apache 2.0", "MIT"],
    extras_require={"test": ["pytest"]},
    classifiers=["Programming Language :: Python :: 3.5"],
)
