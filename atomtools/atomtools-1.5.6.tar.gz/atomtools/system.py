import os
import sys
import psutil
import random
from importlib import import_module






if sys.platform in ['linux', 'darwin']:
    devnull = open('/dev/null', 'w')
elif sys.platform in ['windows']:
    devnull = open('NUL', 'w')

def get_maxcore():
    return round(psutil.cpu_count()*(1-psutil.cpu_percent()/100))

def get_maxmem(unit=None):
    mem = psutil.virtual_memory().available *0.9
    if unit:
        return mem / kmg_unit(unit)
    return mem

