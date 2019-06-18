import re
from setuptools import setup, find_packages


# Retrieve version number
VERSIONFILE = "synfo/_version.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE))


setup(
    name='synfo',
    version=verstr,
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'synfo = synfo.system:main'
        ]
    },
    extras_require={
        'memory': 'psutil>=5.5.1'
    },
    url='https://github.com/mrstephenneal/synfo',
    license='GPL-3.0',
    author='Stephen Neal',
    author_email='stephen@stephenneal.net',
    description='A lightweight utility for retrieving system information and specifications.'
)
