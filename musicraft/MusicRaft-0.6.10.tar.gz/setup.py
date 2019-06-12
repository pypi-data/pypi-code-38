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

share_dirs = ['share/linux/bin',
              'share/windows/abcm2ps-8.14.4',
              'share/windows/abcmidi_win32',
              'share/abc']
share_dirs_here = [os.path.join(HERE, share_dir) for share_dir in share_dirs]

data_files = [(share_dir, [os.path.join(share_dir, one_exec) for one_exec in os.listdir(share_dir_here)])
            for share_dir, share_dir_here in zip(share_dirs, share_dirs_here)]



#print(data_files)
#sys.exit(0)

# This call to setup() does all the work
setup(name = 'MusicRaft',
    version = '0.6.10',
    description='GUI for abcplus music notation.',
    long_description=README,
    long_description_content_type="text/markdown",
    url='https://gitlab.com/papahippo/MusicRaft',
    author = "Larry Myerscough",
    author_email='hippostech@gmail.com',
    packages=find_packages(),
    data_files = data_files,
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
