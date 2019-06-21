#!/usr/bin/env python

import os

from bob.pad.face.preprocessor import VideoSparseCoding

#=======================================================================================
# Define instances here:

BLOCK_SIZE = 5
BLOCK_LENGTH = 10
MIN_FACE_SIZE = 50
NORM_FACE_SIZE = 64

DICTIONARY_LENGTH = 128
DIR = os.path.dirname(os.path.abspath(__file__))

DICTIONARY_FILE_NAMES = [
    os.path.join(DIR, "dictionaries",
                 "dictionary_front_10_5_{}.hdf5".format(DICTIONARY_LENGTH)),
    os.path.join(DIR, "dictionaries",
                 "dictionary_hor_10_5_{}.hdf5".format(DICTIONARY_LENGTH)),
    os.path.join(DIR, "dictionaries",
                 "dictionary_vert_10_5_{}.hdf5".format(DICTIONARY_LENGTH))
]

FRAME_STEP = 50  # (!) a small number of feature vectors will be computed
EXTRACT_HISTOGRAMS_FLAG = True
COMP_RECONSTRUCT_ERR_FLAG = False

preprocessor_10_5_128 = VideoSparseCoding(
    gblock_size=BLOCK_SIZE,
    block_length=BLOCK_LENGTH,
    min_face_size=MIN_FACE_SIZE,
    norm_face_size=NORM_FACE_SIZE,
    dictionary_file_names=DICTIONARY_FILE_NAMES,
    frame_step=FRAME_STEP,
    extract_histograms_flag=EXTRACT_HISTOGRAMS_FLAG,
    comp_reconstruct_err_flag=COMP_RECONSTRUCT_ERR_FLAG)
