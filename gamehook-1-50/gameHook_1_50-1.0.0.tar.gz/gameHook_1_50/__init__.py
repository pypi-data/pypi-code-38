#!/usr/bin/env python
# coding: utf-8
#game site:
#http://wap.jue-huo.com/app/html/game/1to50/1to50.html

from os.path import dirname

Package_Dir = dirname(__file__)

import pyautogui as ag
def autoGame():
    for i in range(1,51):
        A=ag.locateCenterOnScreen(Package_Dir+'/'+str(i)+'.png',confidence=0.92)
        ag.moveTo(A,duration=0.002)
        ag.click(A)