# !/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Example adapted from Josh Sanders' original version on Sanworks Bpod repository
"""
from pybpodapi.bpod import Bpod
"""
Run this protocol now
"""
bpod = Bpod()

for m in bpod.modules:
	print(m)

bpod.close()

