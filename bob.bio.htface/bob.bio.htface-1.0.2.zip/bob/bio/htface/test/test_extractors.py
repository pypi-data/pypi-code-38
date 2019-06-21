#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Tiago de Freitas Pereira <tiago.pereira@idiap.ch>

import tensorflow as tf
import numpy
from bob.bio.htface.extractor import MLBPHS, HoG, ParallelConcatenatedExtractor
#from bob.bio.base.extractor import ParallelExtractor, SequentialExtractor
import bob.ip.base
numpy.random.seed(10)


def test_MLBPHS():

    fake_image = (numpy.random.rand(160, 160)*255).astype("uint8")
    
    lbphs = MLBPHS(block_size=(64, 64),
                  lbp_radius=[1, 2, 4],
                  lbp_uniform=True,
                  lbp_circular=True
                  )

    lbphs = lbphs(fake_image)
    assert lbphs.shape[0] == 708


def test_HOG():

    # TESTING SINGLE CHANNEL
    fake_image = (numpy.random.rand(64, 80)*255).astype("uint8")
    hog_extractor = HoG(bob.ip.base.HOG(image_size = (64, 80)))
    
    hog_hist = hog_extractor(fake_image)
    assert hog_hist.shape == (2560,)
    
    
    # TESTING MULTICHANNEL
    fake_image = (numpy.random.rand(3, 64, 80)*255).astype("uint8")
    hog_extractor = HoG(bob.ip.base.HOG(image_size = (64, 80)))
    
    hog_hist = hog_extractor(fake_image)
    assert hog_hist.shape == (3*2560,)
    

def test_MultiFeature():
    
    # TESTING MULTICHANNEL
    fake_image = (numpy.random.rand(3, 64, 80)*255).astype("uint8")
    
    hog = HoG(bob.ip.base.HOG(image_size = (64, 80)))
    lbp = MLBPHS(block_size=(32, 32), block_overlap=(16, 16), lbp_radius=[1, 3],
                 lbp_uniform=True, lbp_circular=True)
    
    extractor = ParallelConcatenatedExtractor([hog, lbp])
    hists = extractor(fake_image)
    
    assert hists.shape == (9804,)
    
    

