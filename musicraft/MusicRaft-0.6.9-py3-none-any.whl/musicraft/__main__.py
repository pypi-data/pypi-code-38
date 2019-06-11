#!/usr/bin/env python3
"""
Copyright 2015 Hippos Technical Systems BV.

@author: Larry Myerscough (aka papahippo)
"""
import os
from .raft import main
from .abcraft import AbcRaft
from .pyraft import PyRaft
# from .freqraft import FreqRaft
from .abcraft import external


print ("using musicraft package from", os.path.split(__file__)[0])

# Below are examples of how to 'doctor' the behaviour of musicraft.
# This can be handy if e.g. you've installed a newer version of abcm2ps than that on the standard path.
#
# external.Abcm2svg.exec_dir = '/usr/local/bin/'
# external.Abc2midi.exec_dir = '/usr/local/bin/'
# external.Abc2midi.reMsg = r'.*in\s+line-char\s(\d+)\-(\d+).*'
#
# uncomment (and maybve adjust) the above lines only if you need to 'doctor' the behaviour of musicraft.

# call the 'raft' with plugins; other optional experimental plugins are currently disabled.
#
main( Plugins=(AbcRaft, PyRaft))  # , FreqRaft))

