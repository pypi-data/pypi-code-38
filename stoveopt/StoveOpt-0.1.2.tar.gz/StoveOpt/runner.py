# -*- coding: utf-8 -*-
"""
Created on Thu May 30 14:59:06 2019

@author: ADAPTED FROM nxsofsys from github link: https://github.com/dicehub/PyFoam/blob/dev/examples/TestRunner/runIcoFoamCavity.py
"""

#! /usr/bin/env python
#import os
from PyFoam.Infrastructure.CTestRun import CTestRun
#import PyFoam
#from PyFoam import *

case_dir = "C://Oregon_State//Spring_2019//Soft_dev_eng//StoveOpt//foamfiles//counterFlowFlame2D//case_125//"
#case_dir = "C:\\Oregon_State\\Spring_2019\\Soft_dev_eng\\StoveOpt\\foamfiles\\counterFlowFlame2D\\case_25"

class ReactingFoamRunner(CTestRun):
    def init(self):
        self.setParameters(solver="reactingFoam",
                           originalCase=case_dir,
                           sizeClass="unlimited") # Run times are enormous here, so shouldn't have a problem with running my cases

if __name__=='__main__':
    ReactingFoamRunner().run()
    
ReactingFoamRunner().run()




