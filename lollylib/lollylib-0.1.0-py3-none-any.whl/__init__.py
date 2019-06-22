"""
A multipurpose Python 3 library that creates an additional abstraction layer and provides
higher level interface for python developers.
"""
import os
import sys
import ntpath

name = "lollylib"

"""
Following code adds this directory to sys.path so that
python files located in it may import each other directly.
"""

head, tail = ntpath.split(os.path.realpath(__file__))
sys.path.append(head)


