#!/usr/bin/env python

from bob.pad.face.extractor import ImageQualityMeasure

import bob.bio.video

#=======================================================================================
# Define instances here:

galbally = True
msu = True
dtype = None

video_quality_measure_galbally_msu = bob.bio.video.extractor.Wrapper(ImageQualityMeasure(galbally=galbally, msu=msu, dtype=dtype))
