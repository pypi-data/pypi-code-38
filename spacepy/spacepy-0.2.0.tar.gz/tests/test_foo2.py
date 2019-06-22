#!/usr/bin/env	python
#	-*-	coding:	utf-8	-*-
"""
MBE for #68
"""

import spacepy
import spacepy.omni
import spacepy.time
import spacepy.coordinates
import spacepy.irbempy as ib

ticks = spacepy.time.Ticktock(['2001-02-02T12:00:00', '2001-02-02T12:10:00'], 'ISO')
loci = spacepy.coordinates.Coords([[3,0,0],[2,0,0]], 'GEO', 'car')
omnivals = spacepy.omni.get_omni(ticks, dbase='Test')

actual = ib.irbempy._get_Lstar(ticks, loci, [90], extMag='ALEX', omnivals=omnivals)


ticks = spacepy.time.Ticktock(['2001-02-02T12:00:00', '2001-02-02T12:10:00'], 'ISO')
loci = spacepy.coordinates.Coords([[3,0,0],[2,0,0]], 'GEO', 'car')
omnivals = spacepy.omni.get_omni(ticks, dbase='Test')


