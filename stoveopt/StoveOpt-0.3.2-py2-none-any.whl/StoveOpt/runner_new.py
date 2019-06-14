# -*- coding: utf-8 -*-
"""
Created on Fri May 31 11:38:26 2019

@author: Lee
"""

from PyFoam.Infrastructure.CTestRun import CTestRun

class PlainIcoFoamCavity(CTestRun):
    def init(self):
        self.setParameters(solver="reactingFoam",
                           originalCase="C://Oregon_State//Spring_2019//Soft_dev_eng//StoveOpt//foamfiles//counterFlowFlame2D//case_25",
                           sizeClass="unlimited")

if __name__=='__main__':
    PlainIcoFoamCavity().run()