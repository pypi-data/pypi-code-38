"""
The setup script for the dataset.
"""
import sys
from collections import defaultdict
from pathlib import Path

from setuptools import setup, find_packages

# make sure python 3 is running
if sys.version_info.major < 3:
    raise Exception(f"Obsplus datasets cannot be run on python 2")


# get path references
here = Path(__file__).absolute().parent
version_file = here / "opsdata_coal_node" / "version.py"


# --- get version
with version_file.open() as fi:
    content = fi.read().split("=")[-1].strip()
    __version__ = content.replace('"', "").replace("'", "")


def get_package_data_files():
    """ Gets data """
    data = Path("opsdata_coal_node") / "coal_node"
    out = defaultdict(list)
    # get list of datasets
    datasets = [x for x in data.glob("*") if x.is_dir()]
    for dataset in datasets:
        for ifile in dataset.glob("*"):
            if ifile.name.endswith("py") or ifile.name.endswith("pyc"):
                continue
            if ifile.is_dir():
                continue
            out[str(ifile.parent)].append(str(ifile))
    return list(out.items())


# get requirements
requirements = open("requirements.txt")
test_requirements = open("tests/requirements.txt")

license_classifiers = {"BSD license": "License :: OSI Approved :: BSD License"}

setup(
    author="Derrick Chambers",
    author_email="djachambeador@gmail.com",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    description="A dataset collected over an operating longwall coalmine using a dense network of geophones",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    entry_points={"obsplus.datasets": ["coal_node=opsdata_coal_node.core"]},
    install_requires=requirements,
    license="BSD",
    include_package_data=True,
    name="opsdata_coal_node",
    packages=find_packages(include=["ops_datasetcoal_node"]),
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/d-chambers/coal_node",
    data_files=get_package_data_files(),
    version=__version__,
    zip_safe=False,
)
