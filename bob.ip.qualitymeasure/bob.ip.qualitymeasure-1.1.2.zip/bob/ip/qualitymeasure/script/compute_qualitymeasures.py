#!/usr/bin/env python
# vim: set fileencoding=utf-8 :


import sys
import argparse

import bob.io.base
import bob.io.video
import bob.ip.color
import numpy as np
from bob.ip.qualitymeasure import galbally_iqm_features as iqm
from bob.ip.qualitymeasure import msu_iqa_features as iqa


def computeVideoIQM(video4d):
    '''computes image-quality features for a set of frames comprising a video.
    @param video4d: a '4d' video (N frames, each frame representing an r-g-b
        image). returns  a set of feature-vectors, 1 vector per frame of
        video4d
    '''
    numframes = video4d.shape[0]
    numframes = 3
    # print(numframes)

    # process first frame separately, to get the no. of iqm features
    f = 0
    rgbFrame = video4d[f]
    print('processing frame #: %d' % f)
    # iqmSet = iqm.compute_quality_features(grayFrame)
    iqmSet = iqm.compute_quality_features(rgbFrame)
    numIQM = len(iqmSet)
    iqaSet = iqa.compute_msu_iqa_features(rgbFrame)
    numIQA = len(iqaSet)

    # now initialize fset to store iqm features for all frames of input video.
    bobfset = np.zeros([numframes, numIQM])
    bobfset[f] = iqmSet
    msufset = np.zeros([numframes, numIQA])
    msufset[f] = iqaSet

    for f in range(1, numframes):
        print('processing frame #: %d' % f)
        rgbFrame = video4d[f]
#         print(rgbFrame.shape)
        bobQFeats = iqm.compute_quality_features(rgbFrame)
        msuQFeats = iqa.compute_msu_iqa_features(rgbFrame)
        bobfset[f] = bobQFeats
        msufset[f] = msuQFeats

    return (bobfset, msufset)


def computeIQM_1video(vidPath):
    """ loads a video, and returns 2 arrays of feature-vectors -- one per
    feature-family. Each array contains one feature-vector per frame
    """
    # 1. load video from input path
    inputVideo = bob.io.video.reader(vidPath)
    vin = inputVideo.load()
    # 2. compute and return feature-sets
    return computeVideoIQM(vin)


def main(command_line_parameters=None):
    """Computes image-quality features for specified video-file, and stores the
    feature-arrays in specified output hdf5 file"""

    argParser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    argParser.add_argument(
        '-i',
        '--input_videofile',
        dest='inpVidFile',
        default=None,
        help='filename of video to be processed (including complete path). ')

    argParser.add_argument(
        '-o',
        '--output_featurefile',
        dest='outFile',
        default=None,
        help='filename where computed features will be stored. Output file '
             'will be in hdf5 format.')

    args = argParser.parse_args(command_line_parameters)
    # make sure the user specifies a folder where feature-files exist
    if not args.inpVidFile:
        argParser.error('Specify parameter --input_videofile')
    if not args.outFile:
        argParser.error('Specify parameter --output_featurefile')

    # 1. compute features, 1 vector per frame of input video, per
    # feature-family (galbally,msu).
    infile = args.inpVidFile
    (bobIqmFeats, msuIqaFeats) = computeIQM_1video(infile)
    # 2. save features in file
    outfile = args.outFile
    print("Saving features in output file: %s" % outfile)
    ohf = bob.io.base.HDF5File(outfile, 'w')
    ohf.set('bobiqm', bobIqmFeats)
    ohf.set('msuiqa', msuIqaFeats)
    del ohf
    print('Done')


if __name__ == '__main__':
    main(sys.argv[1:])
