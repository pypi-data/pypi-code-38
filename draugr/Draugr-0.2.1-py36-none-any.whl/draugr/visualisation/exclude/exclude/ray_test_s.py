#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time

import ray

__author__ = 'cnheider'
__doc__ = ''


@ray.remote
def f():
  time.sleep(1)
  return 1


ray.init()
results = ray.get([f.remote() for i in range(4)])

print(results)
