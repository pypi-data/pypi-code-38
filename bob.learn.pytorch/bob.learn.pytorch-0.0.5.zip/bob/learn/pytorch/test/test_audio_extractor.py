#!/usr/bin/env python
# encoding: utf-8


import pkg_resources
import numpy
numpy.random.seed(10)
import os


def test_drn():
    """ test for the DltResNet architecture

        This architecture takes Tx257 audio chunk as input,
        where T is the number of frames and 257 is unique numbers from
        spectrogram with 512 FFT resolution.
        output is an embedding of dimension 128
    """
    from bob.learn.pytorch.preprocessor.audio import DltResNetExtractor
    extractor = DltResNetExtractor(test=True)
    # this architecture expects Tx257 
    data = numpy.random.rand(512, 257).astype("float32")
    output = extractor.extract_embeddings(extractor.network, data, 0)
    assert output.size == 128, output.shape


def test_rn():
    """ test for the ResNet architecture

        This architecture takes Tx257 audio chunk as input,
        where T is the number of frames and 257 is unique numbers from
        spectrogram with 512 FFT resolution.
        output is an embedding of dimension 128
    """
    from bob.learn.pytorch.preprocessor.audio import DltResNetExtractor
    extractor = DltResNetExtractor(test=True, use_res=True)
    # this architecture expects Tx257 
    data = numpy.random.rand(300, 257).astype("float32")
    output = extractor.extract_embeddings(extractor.network, data, 0)
    assert output.size == 128, output.shape