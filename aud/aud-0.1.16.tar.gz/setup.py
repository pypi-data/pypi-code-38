import os
from setuptools import setup

import sys
if sys.version_info < (2,7):
    sys.exit('Sorry, Python < 2.7 is not supported')

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "aud",
    version = "0.1.16",
    author = "Zach Howard",
    author_email = "zach.d.howard@gmail.com",
    description = ("Quick tools for audio busy-work"),
    license = "MIT",
    keywords = "audio files tools easy",
    url = "http://github.com/zdhoward/aud",
    packages=['aud'],
    py_modules=['aud.AudDir', 'aud.AudFile', 'aud.AudLib', 'aud'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
    install_requires=['pydub', 'arrow', 'colorlog', 'setuptools>24.2.0', 'pip>9.0.0']
)
