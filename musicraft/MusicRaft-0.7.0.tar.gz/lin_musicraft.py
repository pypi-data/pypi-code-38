#!/usr/bin/env python3
"""
Copyright 2015 Hippos Technical Systems BV.

@author: larry
"""
import sys
import musicraft
print ("imported musicraft package from", musicraft.__file__)

# The following paths get adjusted to be relative to the 'head' directory
#
musicraft.abcraft.external.Abcm2svg.exec_dir = 'share/linux/bin/'
musicraft.abcraft.external.Abc2midi.exec_dir = 'share/linux/bin/'
musicraft.abcraft.external.Abc2abc.exec_dir = 'share/linux/bin/'

# Below are examples of how to further 'doctor' the behaviour of musicraft.
# This can be handy if e.g. you've installed a newer version of abcm2ps than that on the standard path.
#
# musicraft.abcraft.external.Abc2midi.exec_dir = '/usr/local/bin/'
#musicraft.abcraft.external.Abc2midi.reMsg = r'.*in\s+line-char\s(\d+)\-(\d+).*'
#

# call the 'raft' with just the 'musicraft' plugin; other optional experimental plugins are currently disabled.
#
musicraft.raft.main(
    Plugins=(musicraft.abcraft.AbcRaft,
             musicraft.pyraft.PyRaft,
           #  musicraft.freqraft.FreqRaft,
             )
)
