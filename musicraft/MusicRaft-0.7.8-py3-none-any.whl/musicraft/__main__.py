#!/usr/bin/env python3
"""
Copyright 2015 Hippos Technical Systems BV.

@author: Larry Myerscough (aka papahippo)
"""
import sys, os, platform
from .raft import main
from .abcraft import AbcRaft
from .pyraft import PyRaft
# from .freqraft import FreqRaft
from .abcraft import external


print ("using musicraft package from", os.path.split(__file__)[0])

# parse keyword arguments here:
for arg in sys.argv[1:]:
    if arg in ('-S', '--share'):
        # keyword --share or -S means:
        # "use executables (abcm2ps etc.) from the bundled 'share' directory"
        # If this is absent, these are usually assymed to be present on the system path.... but see further below!
        whereAmI = platform.system()
        print("bundled shared executables will be used...")
        if whereAmI == 'Linux':
            external.Abcm2svg.exec_dir = 'share/linux/bin/'
            external.Abc2midi.exec_dir = 'share/linux/bin/'
            external.Abc2abc.exec_dir = 'share/linux/bin/'
        elif whereAmI == 'Windows':
            external.Abcm2svg.exec_dir = 'share/windows/abcm2ps-8.14.4/'
            external.Abc2midi.exec_dir = 'share/windows/abcmidi_win32/'
            external.Abc2abc.exec_dir = 'share/windows/abcmidi_win32/'
        else:
            print("sorry, Musicarft does not come with shared apps for platform %s" %whereAmI)
        sys.argv.remove(arg)
        continue

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

main( Plugins=(AbcRaft,))  #  PyRaft))  # , FreqRaft))

