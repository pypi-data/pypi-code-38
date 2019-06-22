#!/usr/bin/env python2.7
#coding:utf-8

import os
import sys
sys.path.append(os.path.dirname(__file__))
from tools import BlenderTools
import bpy

tools = BlenderTools()
tools.blender = False
tools.runMode = 'PRODUCTION'
tools.scale('/home/jmramoss/Descargas/Pexels Videos 1110140.mp4', 1920, 1080, '/home/jmramoss/Descargas/modPexels Videos 1110140.mp4')
