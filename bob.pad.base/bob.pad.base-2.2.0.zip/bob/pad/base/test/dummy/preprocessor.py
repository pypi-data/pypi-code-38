#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# @author: Pavel Korshunov <pavel.korshunov@idiap.ch>
# @date: Thu Apr 21 16:41:21 CEST 2016
#


from bob.bio.base.preprocessor import Preprocessor
import os.path

dummy_data = {'train_real': 1.0, 'train_attack': 2.0,
              'dev_real': 3.0, 'dev_attack': 4.0,
              'eval_real': 5.0, 'eval_attack': 6.0}


class DummyPreprocessor(Preprocessor):
    def __init__(self, **kwargs):
        Preprocessor.__init__(self)

    def __call__(self, data, annotations):
        """Does nothing, simply converts the data type of the data, ignoring any annotation."""
        return data


preprocessor = DummyPreprocessor()
