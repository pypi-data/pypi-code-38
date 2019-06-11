"""Setup script for typed-result"""

import os.path
from setuptools import setup

# The directory containing this file
from update_version import get_version, update_version

HERE = os.path.abspath(os.path.dirname(__file__))

# The text of the README file
with open(os.path.join(HERE, "README.md")) as fid:
    README = fid.read()

# Version management
CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
version = get_version(CURRENT_DIR)
package_name = "typedresult"
update_version(version, package_name)

# This call to setup() does all the work
setup(
    name="typed-result",
    version=version,
    description="A simple, typed and monadic-based Result type for Python 3.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/acostapazo/typed-result",
    author="Artur Costa-Pazo",
    author_email="costapazo@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
    packages=["typedresult"],
    include_package_data=True,
    install_requires=[

    ]
)
