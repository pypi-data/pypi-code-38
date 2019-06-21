#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Tiago de Freitas Pereira <tiago.pereira@idiap.ch>

import bob.bio.face

preprocessor = bob.bio.face.preprocessor.TanTriggs(
  face_cropper = 'face-crop-eyes'
)
