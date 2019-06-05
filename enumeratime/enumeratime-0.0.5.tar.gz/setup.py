#from distutils.core import setup
from setuptools import setup

setup(
    name="enumeratime",
    version="0.0.5",
    packages=["enumeratime"], #die enthaltenden Packages
    #scripts=["enumeratime"],
    license="GPLV3+",
    author="Michael Ruppert",
    author_email="michael.ruppert@fau.de",
    description="Einfache Prozent und Zeitangabe beim Schleifendurchlauf",
    long_description=open("README.rst", encoding="utf-8").read(),
    #long_description_content_type="text/markdown",
    #install_requires=[,],
    python_requires=">=3.5",
    url="https://github.com/miweru/enumeratime",
    classifiers=[
        "Programming Language :: Python :: 3",
        #'Development Status :: 4 - Beta',
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        #"Operating System :: POSIX :: LINUX",
        "Topic :: Software Development :: Libraries :: Python Modules",
        #"Topic :: Text Processing :: Linguistic",
    ],
    #package_data={
    #}
    )
    
"""
Protokoll dabei:

python3 setup.py sdist bdist_wheel
pip3 install --user dist/py3-non-any.whl

from enumeratime import EnumeraTIME

"""
