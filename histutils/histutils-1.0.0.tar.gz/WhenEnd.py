#!/usr/bin/env python
"""
calculates a few times relevant to a .DMCdata file depending on inputs:
starttime
fps
xpix,ypix
and so on
"""
from __future__ import division
from datetime import timedelta
from dateutil.parser import parse
from argparse import ArgumentParser

p = ArgumentParser(
    description='calculates what approximate time a .DMCdata file ends, based on inputs')
p.add_argument('starttime', help='date and time of first frame')
p.add_argument('fps', help='frames per second', type=float)
p.add_argument('-k', '--frameind',
               help='frame indices to give times for', nargs='+', type=int)
p.add_argument('--xy', help='binned pixel count', nargs=2, type=int)
p.add_argument('-f', '--filesize',
               help='file size in bytes of big .DMCdata file', type=int)
p.add_argument('--nheadbytes',
               help='number of bytes in each frame for header (default 4)', type=int, default=4)
P = p.parse_args()

tstart = parse(P.starttime)
# %% find start end times
if P.xy and P.filesize:
    nframes = P.filesize // (P.xy[0] * P.xy[1] * 2 + 4)
    totalsec = nframes / P.fps

    tend = tstart + timedelta(seconds=totalsec)
    print(f'tstart {tstart}  tend {tend}')
# %% find times corresponding to frame #s
if P.frameind:
    for k in P.frameind:
        print(f'frame {k}:  {tstart + timedelta(seconds=(k-1)*1/P.fps)}')
