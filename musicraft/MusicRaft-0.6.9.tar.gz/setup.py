"""
MusicRaft
"""

#from distutils.core import setup
import sys, os, pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

linux_exec_dir = 'share/linux/bin/'
linux_exec_dir_here = os.path.join(HERE, linux_exec_dir)
linux_execs = [os.path.join(linux_exec_dir, one_exec)
               for one_exec in os.listdir(linux_exec_dir_here)]

# This call to setup() does all the work
setup(name = 'MusicRaft',
    version = '0.6.9',
    description='GUI for abcplus music notation.',
    long_description=README,
    long_description_content_type="text/markdown",
    url='https://gitlab.com/papahippo/MusicRaft',
    author = "Larry Myerscough",
    author_email='hippostech@gmail.com',
    packages=find_packages(),
    data_files = [(linux_exec_dir, linux_execs), ],
      scripts=['lin_musicraft.py', 'win_musicraft.py', 'share/linux/bin/xml2abc.py' ],
    license='LICENSE.txt',
    install_requires=[
        "mido == 1.1.14",
        #"pyqtgraph >= 0.10.0",
        "lxml",
        #"pyaudio",
        "numpy",
        #"pillow",
        "PySide2",

    ],
)
