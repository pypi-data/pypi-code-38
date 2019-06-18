"""
    PyJAMAS is Just A More Awesome Siesta
    Copyright (C) 2018  Rodrigo Fernandez-Gonzalez (rodrigo.fernandez.gonzalez@utoronto.ca)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

""" See this to build an executable:
https://setuptools.readthedocs.io/en/latest/setuptools.html#eggsecutable-scripts"""

"""Building the package:
pythonw setup.py sdist bdist_wheel
#tar tzf dist/*.gz
pythonw -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
pip install -i https://test.pypi.org/simple/ pyjamas

or

pythonw -m twine upload dist/*
pip install pyjamas-rfglab

To fill in the install_requires field below, try pipreqs pyjamas from the src folder.
NOTE: When installing a package from testPyPI, the dependencies are also installed from there.
So you will get package not found errors.

NOTE 2: Windows installation should be after installing CONDA, and "conda install shapely=1.6.4". This also installs
geos (C library used by shapely) 3.7.1. Unfortunately geos is only available up to version 0.2.1 in pypi.
Alternatively, there are shapely wheels at http://www.lfd.uci.edu/~gohlke/pythonlibs/#shapely. 
"""

import os
import setuptools
import sys

with open("README.md", "r") as fh:
    long_description = fh.read()

bin_path: str = os.path.dirname(sys.executable)
# The interpreter needs to be modified to use pythonw, not python (this is a windowed app!!!).
interpreter_name: str = 'pythonw'
shebang: str = '#!/usr/bin/env '
sys.executable = os.path.join(bin_path, interpreter_name)

setuptools.setup(
    name="pyjamas-rfglab",
    version="2019.6.0",  # Calendar versioning: year.month.minor
    author="Rodrigo Fernandez-Gonzalez",
    author_email="rodrigo.fernandez.gonzalez@utoronto.ca",
    description="PyJAMAS is Just A More Awesome SIESTA",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/rfg_lab/pyjamas",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    install_requires=["lxml>=4.2.5", "matplotlib>=3.0.0", "numpy>=1.14.0", "opencv_python>=3.4.5.20", "PyQt5>=5.11.0",
                      "scikit_image>=0.13.0", "scikit_learn>=0.20.2", "scipy>=1.1.0", "setuptools<=39.1.0",
                      "shapely>=1.6.0", "tables>=3.3.0", "tensorflow>=1.10.0", "typing>=3.6.6"],
    python_requires='>=3.6.6,<3.7',
    entry_points={
        'console_scripts': [
            'pyjamas=pyjamas.pjscore:main'
        ]
    }
)