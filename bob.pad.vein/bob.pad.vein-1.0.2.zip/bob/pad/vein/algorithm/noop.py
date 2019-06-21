#!/usr/bin/env python2
# -*- coding: utf-8 -*-


import numpy
import bob.sp
from bob.pad.base.algorithm import Algorithm


class NOOP(Algorithm):
  '''Returns the input (which is already supposed to be a score)
  '''


  def __init__(self):
    super(NOOP, self).__init__()


  def score(self, data):
    return [data[0]]
