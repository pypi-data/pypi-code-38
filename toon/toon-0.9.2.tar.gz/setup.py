from setuptools import setup, find_packages
from codecs import open
from os import path
import platform

here = path.abspath(path.dirname(__file__))

# get requirements
with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    requirements = f.read().splitlines()

setup(
    name='toon',
    version='0.9.2',
    description='Tools for neuroscience experiments',
    url='https://github.com/aforren1/toon',
    author='Alexander Forrence',
    author_email='aforren1@jhu.edu',
    license='GPL3',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],
    install_requires=requirements,
    extras_require={
        'full': ['hidapi', 'pyserial', 'pynput', 'nidaqmx;platform_system=="Windows"'],
        'hand': ['hidapi'],
        'birds': ['pyserial'],
        'keyboard': ['pynput'],
        'force': ['nidaqmx;platform_system=="Windows"']
    },
    keywords='psychophysics neuroscience input experiment',
    packages=find_packages(exclude=['contrib', 'docs', 'tests'])
)
