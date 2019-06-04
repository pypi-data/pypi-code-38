import os
from distutils.core import setup
from setuptools import find_packages

__version__ = open("pyranges_db/version.py").readline().split(
    " = ")[1].replace('"', '').strip()

install_requires = ["cython", "pandas", "natsort", "mysqlclient", "requests"]

if os.getenv("TRAVIS"):
    install_requires.append("coveralls")

setup(
    name="pyranges_db",
    packages=find_packages(),
    include_dirs=["."],
    version=__version__,
    description="Database add-on for PyRanges.",
    author="Endre Bakken Stovner",
    author_email="endrebak85@gmail.com",
    url="http://github.com/pyranges/pyranges_db",
    keywords=["Bioinformatics"],
    license="MIT",
    install_requires=install_requires,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Development Status :: 4 - Beta", "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        'License :: OSI Approved :: MIT License',
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Topic :: Scientific/Engineering"
    ],
    long_description=("Access mysql/ftp databases and return PyRanges."))
