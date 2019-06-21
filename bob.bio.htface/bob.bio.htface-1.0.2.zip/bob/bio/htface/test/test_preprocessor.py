#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Tiago de Freitas Pereira <tiago.pereira@idiap.ch>

import tensorflow as tf
import numpy
from bob.bio.htface.preprocessor import DoG_Pyramid
import bob.ip.base
numpy.random.seed(10)


def test_DoG_Pyramid():

    fake_image = (numpy.random.rand(160, 160)*255).astype("uint8")
    
    filters = []
    sigmas = list(numpy.arange(1, 2.1, 0.5))
    scales = [4,5] 
    for s in sigmas:
        for c in scales:
            filters.append(bob.bio.face.preprocessor.TanTriggs(face_cropper=None, radius=c, alpha=0.1, sigma0=s, sigma1=s+1))

    preprocessor = DoG_Pyramid(filters)
    
    filtered = preprocessor(fake_image)
    assert filtered.shape == (6, 160, 160)

