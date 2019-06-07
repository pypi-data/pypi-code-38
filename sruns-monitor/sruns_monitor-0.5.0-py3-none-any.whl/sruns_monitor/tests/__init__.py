# -*- coding: utf-8 -*-

###
# Nathaniel Watson
# nathanielwatson@stanfordhealthcare.org
###

import os

WATCH_DIR = os.path.join(os.path.dirname(__file__), "SEQ_RUNS")
COMPLETED_RUNS_DIR = os.path.join(os.path.dirname(__file__), "COMPLETED_RUNS")

#: Used for storing output from tests. Tests do attempt to clean up after themselves.
#: Will be created if it doesn't exist yet. 
TMP_DIR = os.path.join(os.path.dirname(__file__), "TMP")
if not os.path.exists(TMP_DIR):
    os.mkdir(TMP_DIR)
