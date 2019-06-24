import os
import sys

if sys.version_info < (3,3):
    sys.exit('Sorry, Python < 3.3 is not supported')

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# include all man files
data_dir = os.path.join('man','man1')
data_files = [(d, [os.path.join(d,f) for f in files])
    for d, folders, files in os.walk(data_dir)]

setup(
    name='obis',
    version='0.2.1',
    description='Local data management with assistance from OpenBIS.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://sissource.ethz.ch/sispub/openbis/tree/master/obis',
    author='ID SIS • ETH Zürich',
    author_email='swen@ethz.ch',
    license='Apache Software License Version 2.0',
    packages=['obis', 'obis.dm', 'obis.dm.commands', 'obis.scripts'],
    data_files=data_files,
    package_data={'obis' : ['dm/git-annex-attributes']},
    install_requires=[
        'pyOpenSSL',
        'pytest',
        'pybis',
        'click'
    ],
    entry_points={ 
        'console_scripts' : [
            'obis=obis.scripts.cli:main'
        ]
    },
    zip_safe=False,
    python_requires=">=3.3",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)
