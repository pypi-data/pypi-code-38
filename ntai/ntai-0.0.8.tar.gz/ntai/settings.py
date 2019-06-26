import os

'''-----------------------------------------------------------------------------
DIRECTORIES AND FILES
-----------------------------------------------------------------------------'''
MODULE_DIR      = os.path.dirname(os.path.realpath(__file__))
PROJECT_DIR     = os.path.join(MODULE_DIR, '..')
DATA_DIR        = os.path.join(PROJECT_DIR, 'data')
SOURCE_DIR      = os.path.join(DATA_DIR, 'source')
DSOURCE_DIR     = os.path.join(DATA_DIR, 'dsource')
DERIVED_DIR     = os.path.join(DATA_DIR, 'derived')
HG38_FILE       = os.path.join(SOURCE_DIR, 'hg38.fa')
JUYPTER_DIR     = os.path.join(PROJECT_DIR, 'juypter')
EXPERIMENTS_DIR = os.path.join(PROJECT_DIR, 'experiments')
