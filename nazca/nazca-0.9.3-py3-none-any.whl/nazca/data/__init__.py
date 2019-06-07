# -*- coding: utf-8 -*-
""" Data for Nazca
"""
import os.path as osp

HERE = osp.join(osp.abspath(osp.dirname(__file__)))
FRENCH_LEMMAS = dict([t.strip().split('\t')
                      for t in open(osp.join(HERE, 'french_lemmas.txt'))])
